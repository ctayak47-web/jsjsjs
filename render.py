# -*- coding: utf-8 -*-
"""
render.py
Генерация мокапа экрана профиля Telegram (iOS, тёмная тема) по образцу.
Блок "канал" не рендерится.

Все данные (имя, юзернейм, статус, "о себе") вводятся пользователем вручную.

Изменения этой версии:
- Шрифт Poppins вместо DejaVu Sans (геометричнее, ближе к SF Pro).
- Иконки (звонок/звук/поиск/ещё) нарисованы вручную линиями/дугами,
  а не текстовыми эмодзи-глифами (те кривые и не похожи на SF Symbols).
- Панель действий — единая карточка с разделителями, как в реальном
  Telegram, а не 4 отдельные скруглённые кнопки.
- Более крупные, мягкие радиусы скругления карточек.
"""

from __future__ import annotations
import io
import os
import math
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------- Шрифты (лежат в fonts/ рядом с этим файлом) ----------
# ВАЖНО: Poppins не содержит кириллических глифов (проверено — рисует
# пустые квадраты вместо русских букв), поэтому используем DejaVu Sans,
# у которого полная поддержка кириллицы.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = os.path.join(_BASE_DIR, "fonts", "DejaVuSans.ttf")
FONT_MEDIUM = os.path.join(_BASE_DIR, "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(_BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")

def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)

# ---------- Цвета (тёмная тема iOS Telegram) ----------
BG_COLOR = (0, 0, 0)
CARD_COLOR = (28, 28, 30)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (142, 142, 147)
TEXT_TERTIARY = (110, 110, 115)
DIVIDER = (56, 56, 58)
BACK_BTN_BG = (44, 44, 46)
DANGER = (255, 69, 58)
ICON_COLOR = (255, 255, 255)


@dataclass
class ProfileData:
    display_name: str
    username: str
    status: str = "был(а) недавно"
    bio: Optional[str] = None
    avatar: Optional[Image.Image] = None
    music_title: Optional[str] = None   # напр. "2_5299035207041583898"
    music_artist: Optional[str] = None  # напр. "<unknown>"
    time_text: str = "9:41"
    battery_percent: int = 67
    wifi_bars: int = 3          # 0-3
    cellular_bars: int = 5      # 0-5


def _circle_avatar(img: Image.Image, diameter: int) -> Image.Image:
    img = ImageOps.fit(img.convert("RGB"), (diameter, diameter), method=Image.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, diameter, diameter), fill=255)
    out = Image.new("RGBA", (diameter, diameter))
    out.paste(img, (0, 0), mask)
    return out


def _placeholder_avatar(diameter: int, initials: str) -> Image.Image:
    img = Image.new("RGB", (diameter, diameter), (90, 90, 100))
    draw = ImageDraw.Draw(img)
    for y in range(diameter):
        t = y / diameter
        r = int(70 + 60 * t); g = int(80 + 40 * t); b = int(160 - 40 * t)
        draw.line([(0, y), (diameter, y)], fill=(r, g, b))
    f = _font(FONT_BOLD, diameter // 3)
    bbox = draw.textbbox((0, 0), initials, font=f)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((diameter-w)/2 - bbox[0], (diameter-h)/2 - bbox[1]), initials, font=f, fill=(255, 255, 255))
    return _circle_avatar(img, diameter)


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2]-bbox[0] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def _centered_text(draw, cx, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2]-bbox[0]
    draw.text((cx - w/2 - bbox[0], y), text, font=font, fill=fill)
    return bbox[3]-bbox[1]


# ---------- Векторные иконки (рисуются линиями, не текстом) ----------

def _icon_phone(draw, cx, cy, r, lw):
    """
    Иконка "трубка телефона" — классический SF Symbols-силуэт:
    S-образная кривая от нижнего левого края до верхнего правого,
    с двумя скруглёнными "раструбами" на концах.
    Рисуется как последовательность точек плавной кривой + заливка контуром.
    """
    # Строим осевую линию трубки как кривую Безье через 4 контрольные точки
    p0 = (cx - r*0.62, cy + r*0.68)   # нижний левый конец (микрофон)
    p1 = (cx - r*0.75, cy - r*0.05)
    p2 = (cx + r*0.05, cy - r*0.75)
    p3 = (cx + r*0.68, cy - r*0.62)   # верхний правый конец (динамик)

    def bezier(t, a, b, c, d):
        x = (1-t)**3*a[0] + 3*(1-t)**2*t*b[0] + 3*(1-t)*t**2*c[0] + t**3*d[0]
        y = (1-t)**3*a[1] + 3*(1-t)**2*t*b[1] + 3*(1-t)*t**2*c[1] + t**3*d[1]
        return (x, y)

    steps = 20
    curve = [bezier(i/steps, p0, p1, p2, p3) for i in range(steps+1)]

    stroke_w = max(2, int(lw*1.6))
    for i in range(len(curve)-1):
        draw.line([curve[i], curve[i+1]], fill=ICON_COLOR, width=stroke_w, joint="curve")

    # Скруглённые "раструбы" на концах (утолщение, как у настоящей трубки)
    end_r = stroke_w * 0.95
    draw.ellipse([p0[0]-end_r, p0[1]-end_r, p0[0]+end_r, p0[1]+end_r], fill=ICON_COLOR)
    draw.ellipse([p3[0]-end_r, p3[1]-end_r, p3[0]+end_r, p3[1]+end_r], fill=ICON_COLOR)



def _icon_bell(draw, cx, cy, r, lw):
    # Колокольчик: дуга сверху (купол) + прямые бока + маленький кружок-язычок снизу
    top = cy - r*0.6
    bottom = cy + r*0.35
    left = cx - r*0.55
    right = cx + r*0.55
    draw.arc([left, top - r*0.15, right, top + r*0.9], start=180, end=360, fill=ICON_COLOR, width=lw)
    draw.line([(left, top + r*0.35), (left, bottom)], fill=ICON_COLOR, width=lw)
    draw.line([(right, top + r*0.35), (right, bottom)], fill=ICON_COLOR, width=lw)
    draw.line([(left - lw*0.3, bottom), (right + lw*0.3, bottom)], fill=ICON_COLOR, width=lw)
    draw.ellipse([cx-r*0.14, bottom+lw*0.2, cx+r*0.14, bottom+lw*0.2+r*0.3], fill=ICON_COLOR)


def _icon_video(draw, cx, cy, r, lw):
    # Классическая иконка видеокамеры (как в iOS): корпус слева (прямоугольник
    # со скруглением), объектив справа — трапеция, острым краем к корпусу.
    body_w, body_h = r*1.15, r*0.85
    bx0, by0 = cx - r*0.7, cy - body_h/2
    bx1, by1 = bx0 + body_w, by0 + body_h
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=max(2, int(body_h*0.25)), fill=ICON_COLOR)

    lens_h_far = body_h * 0.42   # узкая сторона у корпуса
    lens_h_near = body_h * 0.68  # широкая сторона к зрителю
    lens_x0 = bx1 - lw*0.2
    lens_x1 = cx + r*0.68
    draw.polygon([
        (lens_x0, cy - lens_h_far/2),
        (lens_x0, cy + lens_h_far/2),
        (lens_x1, cy + lens_h_near/2),
        (lens_x1, cy - lens_h_near/2),
    ], fill=ICON_COLOR)


def _icon_search(draw, cx, cy, r, lw):
    # Лупа: окружность + ручка по диагонали
    rad = r * 0.5
    ox, oy = cx - r*0.12, cy - r*0.12
    draw.ellipse([ox-rad, oy-rad, ox+rad, oy+rad], outline=ICON_COLOR, width=lw)
    handle_start = (ox + rad*0.75, oy + rad*0.75)
    handle_end = (cx + r*0.55, cy + r*0.55)
    draw.line([handle_start, handle_end], fill=ICON_COLOR, width=int(lw*1.2))


def _icon_more(draw, cx, cy, r, lw):
    # Три точки по горизонтали
    dot_r = max(2, int(r*0.13))
    spacing = r * 0.55
    for i in (-1, 0, 1):
        x = cx + i*spacing
        draw.ellipse([x-dot_r, cy-dot_r, x+dot_r, cy+dot_r], fill=ICON_COLOR)


def _action_row(draw, x0, x1, y0, h, entries, s):
    """Единая карточка с колонками-кнопками, разделёнными тонкими линиями."""
    draw.rounded_rectangle([(x0, y0), (x1, y0+h)], radius=s(20), fill=CARD_COLOR)
    n = len(entries)
    col_w = (x1 - x0) / n
    label_font = _font(FONT_REGULAR, s(13))
    icon_r = s(12)
    icon_cy = y0 + s(32)
    label_y = y0 + s(58)
    for i, (icon_fn, label) in enumerate(entries):
        col_cx = x0 + col_w*i + col_w/2
        icon_fn(draw, col_cx, icon_cy, icon_r, max(2, s(2)))
        _centered_text(draw, col_cx, label_y, label, label_font, TEXT_SECONDARY)
        if i > 0:
            lx = x0 + col_w*i
            draw.line([(lx, y0+s(18)), (lx, y0+h-s(18))], fill=DIVIDER, width=max(1, s(1)))


def _draw_cellular_bars(draw, x, y, h, bars_filled, s):
    """5 полосок сотовой сети, растущих по высоте слева направо."""
    n = 5
    bar_w = s(4)
    gap = s(2)
    max_h = h
    for i in range(n):
        bh = max_h * (0.35 + 0.65 * (i / (n-1)))
        bx0 = x + i*(bar_w+gap)
        by1 = y + max_h
        by0 = by1 - bh
        color = TEXT_PRIMARY if i < bars_filled else (80, 80, 82)
        draw.rounded_rectangle([bx0, by0, bx0+bar_w, by1], radius=max(1, s(1)), fill=color)
    return n*(bar_w+gap) - gap


def _draw_wifi_icon(draw, cx, y_top, h, bars_filled, s):
    """
    Значок Wi-Fi — 3 концентрические дуги + точка снизу, растущие от точки вверх.
    cx: центр по X. y_top: верхняя граница области значка. h: общая высота значка.
    """
    dot_r = max(2, int(h*0.11))
    dot_cy = y_top + h - dot_r
    draw.ellipse([cx-dot_r, dot_cy-dot_r, cx+dot_r, dot_cy+dot_r],
                 fill=TEXT_PRIMARY if bars_filled >= 1 else (80, 80, 82))

    n_arcs = 2  # две дуги над точкой (упрощённый, но пропорциональный wifi-знак)
    max_span = h * 0.95
    for i in range(n_arcs):
        span = max_span * ((i+1) / n_arcs)
        box = [cx - span, dot_cy - span, cx + span, dot_cy + span]
        color = TEXT_PRIMARY if bars_filled >= (n_arcs - i) else (80, 80, 82)
        draw.arc(box, start=225, end=315, fill=color, width=max(2, s(2)))
    return h*1.3


def _draw_battery(draw, x, y, h, percent, s):
    """Корпус батареи с "носиком" и внутренней заливкой по проценту."""
    w = h * 1.9
    body_w = w - s(3)
    lw = max(1, s(1))
    draw.rounded_rectangle([x, y, x+body_w, y+h], radius=max(2, s(3)), outline=TEXT_PRIMARY, width=lw)
    tip_w = s(3)
    tip_h = h*0.4
    draw.rounded_rectangle([x+body_w+s(1), y+(h-tip_h)/2, x+body_w+s(1)+tip_w, y+(h-tip_h)/2+tip_h],
                            radius=max(1, s(1)), fill=TEXT_PRIMARY)
    pad = max(2, s(2))
    inner_w = body_w - 2*pad
    fill_w = max(0, inner_w * max(0, min(100, percent)) / 100)
    fill_color = TEXT_PRIMARY if percent > 20 else DANGER
    draw.rounded_rectangle([x+pad, y+pad, x+pad+fill_w, y+h-pad], radius=max(1, s(1)), fill=fill_color)
    return w


def render_profile_mockup(data: ProfileData, width: int = 1080) -> Image.Image:
    scale = width / 591
    def s(v): return int(round(v * scale))

    height = s(1050)
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- статус-бар: время слева, сеть/wifi/батарея справа ---
    draw.text((s(24), s(30)), data.time_text, font=_font(FONT_BOLD, s(16)), fill=TEXT_PRIMARY)

    icon_h = s(11)
    icon_y = s(33)
    right_margin = s(24)

    batt_w = icon_h * 1.9
    batt_x = width - right_margin - batt_w
    _draw_battery(draw, batt_x, icon_y, icon_h, data.battery_percent, s)

    wifi_w = icon_h * 1.3
    wifi_cx = batt_x - s(10) - wifi_w/2
    _draw_wifi_icon(draw, wifi_cx, icon_y, icon_h, data.wifi_bars, s)

    cell_w = s(4 + 2) * 5 - s(2)
    cell_x = wifi_cx - wifi_w/2 - s(10) - cell_w
    _draw_cellular_bars(draw, cell_x, icon_y, icon_h, data.cellular_bars, s)

    # --- кнопка назад ---
    back_d = s(56)
    back_xy = (s(24), s(90))
    draw.ellipse([back_xy, (back_xy[0]+back_d, back_xy[1]+back_d)], fill=BACK_BTN_BG)
    cx_b, cy_b = back_xy[0]+back_d/2, back_xy[1]+back_d/2
    lw = max(2, s(3))
    r = s(9)
    draw.line([(cx_b+r*0.4, cy_b-r), (cx_b-r*0.5, cy_b), (cx_b+r*0.4, cy_b+r)],
              fill=(200, 200, 205), width=lw, joint="curve")

    # --- аватар ---
    avatar_d = s(150)
    avatar_xy = ((width - avatar_d)//2, s(88))
    if data.avatar is not None:
        av = _circle_avatar(data.avatar, avatar_d)
    else:
        initials = "".join([p[0] for p in data.display_name.split()[:2]]).upper() or "?"
        av = _placeholder_avatar(avatar_d, initials)
    img.paste(av, avatar_xy, av)

    y = avatar_xy[1] + avatar_d + s(20)
    cx = width / 2

    # --- имя ---
    name_font = _font(FONT_BOLD, s(32))
    h_name = _centered_text(draw, cx, y, data.display_name, name_font, TEXT_PRIMARY)
    y += h_name + s(12)

    # --- статус ---
    status_font = _font(FONT_REGULAR, s(18))
    h_status = _centered_text(draw, cx, y, data.status, status_font, TEXT_SECONDARY)
    y += h_status + s(44)

    if data.music_title:
        note_font = _font(FONT_REGULAR, s(16))
        note_text = f"\u266A {data.music_title} - {data.music_artist or '<unknown>'}"
        h_note = _centered_text(draw, cx, y, note_text, note_font, TEXT_SECONDARY)
        y += h_note + s(24)

    # --- панель действий: единая карточка (5 кнопок, как в референсе) ---
    row_h = s(104)
    entries = [
        (_icon_phone, "звонок"),
        (_icon_video, "видео"),
        (_icon_bell, "звук"),
        (_icon_search, "поиск"),
        (_icon_more, "ещё"),
    ]
    _action_row(draw, s(24), width - s(24), y, row_h, entries, s)
    y += row_h + s(28)

    # ---- карточка "имя пользователя" / "о себе" ----
    card_x0, card_x1 = s(24), width - s(24)
    pad = s(22)
    label_font = _font(FONT_REGULAR, s(14))
    value_font = _font(FONT_REGULAR, s(19))

    lines_bio = _wrap_text(draw, data.bio, value_font, card_x1-card_x0-2*pad) if data.bio else []

    row_h_username = s(74)
    row_h_bio = (pad + s(20) + len(lines_bio)*s(27) + s(8)) if lines_bio else 0
    card_h = row_h_username + row_h_bio

    card_y0 = y
    draw.rounded_rectangle([(card_x0, card_y0), (card_x1, card_y0+card_h)], radius=s(22), fill=CARD_COLOR)

    ty = card_y0 + s(14)
    draw.text((card_x0+pad, ty), "имя пользователя", font=label_font, fill=TEXT_SECONDARY)
    draw.text((card_x0+pad, ty+s(23)), f"@{data.username}", font=_font(FONT_REGULAR, s(19)), fill=TEXT_PRIMARY)

    if lines_bio:
        div_y = card_y0 + row_h_username
        draw.line([(card_x0+pad, div_y), (card_x1-pad, div_y)], fill=DIVIDER, width=max(1, s(1)))
        ty2 = div_y + s(14)
        draw.text((card_x0+pad, ty2), "о себе", font=label_font, fill=TEXT_SECONDARY)
        ty3 = ty2 + s(23)
        for line in lines_bio:
            draw.text((card_x0+pad, ty3), line, font=value_font, fill=TEXT_PRIMARY)
            ty3 += s(27)

    y = card_y0 + card_h + s(22)

    # ---- карточка "Добавить в контакты" / "Заблокировать" ----
    row_h2 = s(68)
    card2_h = row_h2 * 2
    draw.rounded_rectangle([(card_x0, y), (card_x1, y+card2_h)], radius=s(22), fill=CARD_COLOR)
    row_font = _font(FONT_REGULAR, s(19))
    draw.text((card_x0+pad, y + (row_h2-s(23))//2), "Добавить в контакты", font=row_font, fill=TEXT_TERTIARY)
    draw.line([(card_x0+pad, y+row_h2), (card_x1-pad, y+row_h2)], fill=DIVIDER, width=max(1, s(1)))
    draw.text((card_x0+pad, y+row_h2 + (row_h2-s(23))//2), "Заблокировать", font=row_font, fill=DANGER)

    y = y + card2_h + s(20)

    final_height = int(y)
    img = img.crop((0, 0, width, final_height))
    return img


def render_to_bytes(data: ProfileData, width: int = 1080) -> bytes:
    img = render_profile_mockup(data, width=width)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

