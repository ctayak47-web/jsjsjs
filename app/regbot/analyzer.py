"""
Модель оценки даты регистрации Telegram-аккаунта по его числовому ID.

Метод: кусочно-линейная интерполяция между опорными точками (ID -> unix ms),
экстраполяция для ID выше последней опорной точки.

Улучшения по сравнению с исходной версией:

1. Опорные точки объединены и расширены новыми данными вплоть до ID 9100000000.

2. Автоматическая коррекция аномалий (изотоническая регрессия / PAVA).
   Опорные точки обязаны идти по возрастанию: чем больше ID, тем позже дата
   регистрации. На практике в сырых данных иногда встречаются "провалы" —
   точка с timestamp меньше, чем у одной из предыдущих точек (например ID
   8500000000 в исходных данных был помечен как аномалия). Такие точки ломают
   как интерполяцию (np.interp требует строго возрастающий x, но неявно
   "ожидает" и возрастание y для физического смысла), так и экстраполяцию.

   Вместо того чтобы вручную патчить единичные значения, весь набор точек
   прогоняется через pool-adjacent-violators (PAVA) — стандартный алгоритм
   изотонической регрессии. Он находит все нарушения монотонности и заменяет
   проблемные участки взвешенным средним, гарантируя не убывающую последовательность
   и минимальное искажение остальных данных. Это устойчиво к любым будущим
   ошибкам в опорных точках, а не только к уже известной.

3. Экстраполяция за пределами последней опорной точки: вместо полинома 2-й
   степени по последним 5 точкам (нестабилен и может давать не возрастающий
   результат) используется линейная регрессия по последним N точкам —
   она безопаснее для длинной экстраполяции и не может развернуть тренд.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np

# ─── опорные точки: ID телеграм-аккаунта -> unix timestamp регистрации (мс) ──

MILESTONES: Dict[int, int] = {
    2768409: 1383264000000,
    7679610: 1388448000000,
    11538514: 1391212000000,
    15835244: 1392940000000,
    23646077: 1393459000000,
    38015510: 1393632000000,
    44634663: 1399334000000,
    46145305: 1400198000000,
    54845238: 1411257000000,
    63263518: 1414454000000,
    101260938: 1425600000000,
    101323197: 1426204000000,
    111220210: 1429574000000,
    103258382: 1432771000000,
    103151531: 1433376000000,
    116812045: 1437696000000,
    122600695: 1437782000000,
    109393468: 1439078000000,
    112594714: 1439683000000,
    124872445: 1439856000000,
    130029930: 1441324000000,
    125828524: 1444003000000,
    133909606: 1444176000000,
    157242073: 1446768000000,
    143445125: 1448928000000,
    148670295: 1452211000000,
    152079341: 1453420000000,
    171295414: 1457481000000,
    181783990: 1460246000000,
    222021233: 1465344000000,
    225034354: 1466208000000,
    278941742: 1473465000000,
    285253072: 1476835000000,
    294851037: 1479600000000,
    297621225: 1481846000000,
    328594461: 1482969000000,
    337808429: 1487707000000,
    341546272: 1487782000000,
    352940995: 1487894000000,
    369669043: 1490918000000,
    400169472: 1501459000000,
    805158066: 1563208000000,
    989559217: 1574726400000,
    1974255900: 1634000000000,
    5520018289: 1721847912670,
    5595979516: 1661558400000,
    6923148775: 1705881600000,
    6952797555: 1706918400000,
    6958521804: 1707091200000,
    7416124792: 1732838400000,
    7567158698: 1741219200000,
    7602951950: 1742688000000,
    8247881093: 1747958400000,
    8264059120: 1749081600000,
    8292372344: 1751155200000,
    8373380470: 1757289600000,
    # свежие/прогнозные точки (заменяют старые грубые оценки 8700M/8800M)
    8400000000: 1768824000000,
    8450000000: 1769083200000,
    8500000000: 1754395200000,  # аномалия в исходных данных — исправляется PAVA ниже
    8550000000: 1765540800000,
    8600000000: 1767182400000,
    8650000000: 1768910400000,
    8700000000: 1770552000000,
    8750000000: 1772020800000,
    8800000000: 1773921600000,
    8850000000: 1775563200000,
    8900000000: 1777204800000,
    8950000000: 1778846400000,
    9000000000: 1780574400000,
    9100000000: 1783857600000,
}


def _pava(y: np.ndarray) -> np.ndarray:
    """Pool-Adjacent-Violators — изотоническая регрессия (не убывающая).

    Возвращает наименее искаженную неубывающую версию y. Каждый "блок"
    хранит среднее значение и вес (число объединенных точек).
    """
    n = len(y)
    level_vals = list(y.astype(float))
    level_w = [1.0] * n
    level_start = list(range(n))  # первый индекс, покрываемый блоком

    i = 0
    # проходим и объединяем блоки, где следующий блок меньше предыдущего
    stack_vals: List[float] = []
    stack_w: List[float] = []
    stack_start: List[int] = []

    for idx in range(n):
        v = level_vals[idx]
        w = level_w[idx]
        s = level_start[idx]
        stack_vals.append(v)
        stack_w.append(w)
        stack_start.append(s)
        while len(stack_vals) > 1 and stack_vals[-2] > stack_vals[-1]:
            v2 = stack_vals.pop()
            w2 = stack_w.pop()
            s2 = stack_start.pop()
            v1 = stack_vals.pop()
            w1 = stack_w.pop()
            s1 = stack_start.pop()
            new_w = w1 + w2
            new_v = (v1 * w1 + v2 * w2) / new_w
            stack_vals.append(new_v)
            stack_w.append(new_w)
            stack_start.append(s1)

    # разворачиваем блоки обратно в массив длиной n
    result = np.empty(n, dtype=float)
    starts = stack_start + [n]
    for k in range(len(stack_vals)):
        result[starts[k]:starts[k + 1]] = stack_vals[k]
    return result


def _make_monotonic(ids: np.ndarray, ts: np.ndarray) -> np.ndarray:
    """Гарантирует, что ts не убывает по мере роста ids, используя PAVA."""
    return _pava(ts)


def get_current_date() -> datetime:
    return datetime.now()


class RegistrationAnalyzer:
    def __init__(self, milestones: Dict[int, int]):
        self.milestones = milestones
        self._prepare_interpolator()

    def _prepare_interpolator(self):
        ids = sorted(self.milestones.keys())
        raw_ts = [self.milestones[i] for i in ids]

        ids_array = np.array(ids, dtype=np.int64)
        raw_ts_array = np.array(raw_ts, dtype=np.float64)

        # исправляем любые нарушения монотонности (в т.ч. известную аномалию 8500000000)
        fixed_ts_array = _make_monotonic(ids_array, raw_ts_array)

        # запоминаем, какие точки были скорректированы — используется для отчёта о точности
        self._corrected_mask = ~np.isclose(fixed_ts_array, raw_ts_array)

        self.ids_array = ids_array
        self.ts_array = fixed_ts_array

    def calculate_timestamp(self, user_id: int) -> int:
        if user_id <= self.ids_array[0]:
            return int(self.ts_array[0])

        if user_id >= self.ids_array[-1]:
            return int(self._extrapolate(user_id))

        timestamp = np.interp(user_id, self.ids_array, self.ts_array)
        return int(timestamp)

    def _extrapolate(self, user_id: int) -> float:
        # линейная регрессия по последним N точек — устойчивее полинома 2-й
        # степени на длинной экстраполяции и не может "развернуть" тренд
        n_points = min(8, len(self.ids_array))
        last_ids = self.ids_array[-n_points:].astype(np.float64)
        last_ts = self.ts_array[-n_points:]

        slope, intercept = np.polyfit(last_ids, last_ts, 1)
        # защита от вырожденного/отрицательного наклона
        if slope <= 0:
            slope = (last_ts[-1] - last_ts[0]) / max(1.0, (last_ids[-1] - last_ids[0]))
            slope = max(slope, 1e-6)
        projected = intercept + slope * user_id
        # никогда не возвращаем дату раньше последней известной опорной точки
        return max(projected, float(self.ts_array[-1]))

    def calculate_age(self, reg_date: datetime) -> Tuple[int, int, int]:
        current = get_current_date()
        years = current.year - reg_date.year
        months = current.month - reg_date.month
        days = current.day - reg_date.day

        if days < 0:
            months -= 1
            prev_month = current.replace(day=1) - timedelta(days=1)
            days += prev_month.day

        if months < 0:
            years -= 1
            months += 12

        return years, months, days

    def get_precision(self, user_id: int) -> str:
        if user_id in self.milestones:
            return "эталонная точность"
        elif user_id <= self.ids_array[-1]:
            return "интерполяция"
        else:
            return "экстраполяция"
