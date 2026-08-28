"""
Inline-mode module for regdateid_bot.

The inline path is intentionally synchronous and tiny:
- validate the query before any expensive work;
- calculate only local CPU data;
- never perform Telegram API calls from build_inline_results;
- always return (results, error).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from threading import RLock
from typing import Dict, List, Optional, Tuple

from .analyzer import MILESTONES, RegistrationAnalyzer

logger = logging.getLogger(__name__)

# Telegram's current Bot API HTML syntax uses emoji-id for <tg-emoji>.
# Buttons themselves do not parse HTML; use icon_custom_emoji_id there.
EMOJI = {
    "id": "5260399854500191689",
    "registration": "5256143829672672750",
    "age": "5258105663359294787",
    "precision": "6032742198179532882",
    "bot": "5258509201306557640",
    "download": "5400176691815406212",
    "go": "5328189264658184861",
    "menu": "5260399854500191689",
}

BOT_USERNAME = "regdateid_bot"


def tg_emoji(emoji_id: str, fallback: str) -> str:
    """Create a valid Telegram HTML custom-emoji tag."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


class InlineCache:
    """Small bounded TTL cache. It is protected because callbacks may be concurrent."""

    def __init__(self, ttl_seconds: int = 3600, max_items: int = 4096):
        self.ttl = max(1, ttl_seconds)
        self.max_items = max(128, max_items)
        self._cache: Dict[int, Tuple[dict, float]] = {}
        self._lock = RLock()

    def get(self, user_id: int) -> Optional[dict]:
        now = time.monotonic()
        with self._lock:
            item = self._cache.get(user_id)
            if item is None:
                return None
            data, created = item
            if now - created >= self.ttl:
                self._cache.pop(user_id, None)
                return None
            return data

    def set(self, user_id: int, data: dict) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._cache) >= self.max_items:
                oldest = min(self._cache, key=lambda key: self._cache[key][1])
                self._cache.pop(oldest, None)
            self._cache[user_id] = (data, now)


class InlineHandler:
    """Pure-ish calculation layer for Telegram inline queries."""

    def __init__(self) -> None:
        self.analyzer = RegistrationAnalyzer(MILESTONES)
        self.cache = InlineCache()

    @staticmethod
    def parse_query(query: str) -> Optional[int]:
        """Instantly validate a numeric Telegram ID."""
        if not isinstance(query, str):
            return None

        value = query.strip()
        if not value or len(value) > 32:
            return None

        # The registration analyzer is intended for user IDs, not arbitrary
        # negative chat IDs. Reject negatives and absurd integer values early.
        if not value.isdigit():
            return None

        try:
            user_id = int(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if user_id <= 0 or user_id > 2**63 - 1:
            return None

        return user_id

    def analyze_user(self, user_id: int) -> Dict:
        cached = self.cache.get(user_id)
        if cached is not None:
            return cached

        timestamp = self.analyzer.calculate_timestamp(user_id)
        reg_date = datetime.fromtimestamp(timestamp / 1000)
        years, months, days = self.analyzer.calculate_age(reg_date)
        precision = self.analyzer.get_precision(user_id)

        result = {
            "user_id": user_id,
            "timestamp": timestamp,
            "reg_date": reg_date.strftime("%d.%m.%Y %H:%M:%S"),
            "age": f"{years} л. {months} мес. {days} дн.",
            "precision": precision,
            "years": years,
            "months": months,
            "days": days,
        }
        self.cache.set(user_id, result)
        return result

    def format_result_text(self, data: Dict) -> str:
        return (
            f'<b>├ {tg_emoji(EMOJI["id"], "👾")} ID:</b> '
            f'<code>{data["user_id"]}</code>\n'
            f'<b>├ {tg_emoji(EMOJI["registration"], "📅")} Регистрация:</b> '
            f'<code>{data["reg_date"]}</code>\n'
            f'<b>├ {tg_emoji(EMOJI["age"], "⏳")} Возраст:</b> '
            f'<code>{data["age"]}</code>\n'
            f'<b>└ {tg_emoji(EMOJI["precision"], "⚙️")} Точность:</b> '
            f'<i>{data["precision"]}</i>\n\n'
            f'<b>{tg_emoji(EMOJI["bot"], "📍")} @{BOT_USERNAME}</b>'
        )

    @staticmethod
    def format_result_description(data: Dict) -> str:
        return (
            f'ID {data["user_id"]} | {data["reg_date"]} | '
            f'{data["precision"]}'
        )


def _button(text: str, callback_data: Optional[str] = None,
            url: Optional[str] = None, style: Optional[str] = None,
            emoji_id: Optional[str] = None) -> Dict:
    """Build a Bot API 9.4+ button.

    HTML is not parsed inside InlineKeyboardButton.text. Therefore custom
    emoji is represented by icon_custom_emoji_id, which is the official
    Bot API 9.4+ mechanism for buttons.
    """
    button = {"text": text}
    if callback_data is not None:
        button["callback_data"] = callback_data
    if url is not None:
        button["url"] = url
    if style is not None:
        button["style"] = style
    if emoji_id is not None:
        button["icon_custom_emoji_id"] = emoji_id
    return button


def get_inline_result_keyboard(user_id: int) -> Dict:
    return {
        "inline_keyboard": [
            [
                _button(
                    "Скачать TXT отчет",
                    url=f"https://t.me/{BOT_USERNAME}?start=download_txt_{user_id}",
                    style="primary",
                    emoji_id=EMOJI["download"],
                ),
                _button(
                    "Скачать HTML отчет",
                    url=f"https://t.me/{BOT_USERNAME}?start=download_html_{user_id}",
                    style="primary",
                    emoji_id=EMOJI["download"],
                ),
            ],
            [
                _button(
                    "Перейти в бота",
                    url=f"https://t.me/{BOT_USERNAME}",
                    style="success",
                    emoji_id=EMOJI["go"],
                )
            ],
        ]
    }


def build_inline_results(
    inline_handler: InlineHandler,
    query: str,
) -> Tuple[List[Dict], Optional[str]]:
    """Build inline results without network/database/blocking operations.

    Contract: this function ALWAYS returns a (results, error) tuple.
    """
    try:
        user_id = inline_handler.parse_query(query)
        if user_id is None:
            if not query.strip():
                return [], None
            return [], "Введите числовой Telegram ID."

        data = inline_handler.analyze_user(user_id)
        result = {
            "type": "article",
            "id": str(user_id),
            "title": f"Анализ аккаунта {user_id}",
            "description": inline_handler.format_result_description(data),
            "input_message_content": {
                "message_text": inline_handler.format_result_text(data),
                "parse_mode": "HTML",
            },
            "reply_markup": get_inline_result_keyboard(user_id),
        }
        return [result], None

    except (ValueError, OverflowError, OSError) as exc:
        logger.warning("inline calculation failed: %s", exc)
        return [], "Не удалось обработать этот ID."

    except Exception:
        logger.exception("unexpected inline calculation error")
        return [], "Временная ошибка анализа."
