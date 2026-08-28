from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

from . import storage
from .analyzer import MILESTONES, RegistrationAnalyzer
from .inline import (
    BOT_USERNAME,
    EMOJI,
    InlineHandler,
    build_inline_results,
    get_inline_result_keyboard,
    tg_emoji,
)
from .templates import generate_html_report, generate_txt_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN_DATA", "")
try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID_DATA", "0") or 0)
except ValueError:
    ADMIN_ID = 0

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(os.environ.get("REGBOT_REPORTS_DIR", str(BASE_DIR / "data" / "reports")))
PHOTO_PATH = Path(os.environ.get("REGBOT_PHOTO", str(BASE_DIR / "foto.png")))

INSTRUCTIONS_TEXT = (
    f'<b>{tg_emoji(EMOJI["menu"], "📖")} Как пользоваться ботом</b>\n\n'
    f'{tg_emoji(EMOJI["id"], "👾")} <b>1. Свой ID</b> — анализирует ваш ID и сохраняет '
    'результат в чате.\n'
    f'{tg_emoji(EMOJI["id"], "🔎")} <b>2. По ID</b> — отправьте числовой Telegram ID.\n'
    f'{tg_emoji(EMOJI["registration"], "↪️")} <b>3. Переслать сообщение</b> — '
    'перешлите сообщение пользователя.\n'
    f'{tg_emoji(EMOJI["bot"], "⚡")} <b>4. /reg1 &lt;id&gt;</b> — быстрый анализ.\n'
    f'{tg_emoji(EMOJI["precision"], "💾")} <b>5. История</b> — бот ничего не удаляет, '
    'поэтому введённые ID и результаты остаются в чате.\n\n'
    f'<i>{tg_emoji(EMOJI["precision"], "⚙️")} Точность: «эталонная» — ID есть в '
    'опорных данных; «интерполяция» — между опорными точками; '
    '«экстраполяция» — прогноз после последней точки.</i>'
)


class TelegramBot:
    """Main bot module.

    The bot is a container for independent modules:
      - analyzer: registration calculation;
      - inline: inline query processing;
      - storage: persistent users/results;
      - templates: report generation.

    No user message is deleted. Menu/photo messages are edited in place,
    while every calculated result is sent as a NEW message.
    """

    def __init__(self, token: str, admin_id: int):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.admin_id = admin_id

        self.analyzer = RegistrationAnalyzer(MILESTONES)
        self.inline_handler = InlineHandler()

        self.user_states: Dict[int, Optional[str]] = {}
        self.user_data: Dict[int, dict] = {}

        # Separate menu message from result messages.
        self.user_menu_messages: Dict[int, int] = {}

        # Telegram file_id for foto.png after the first upload.
        self._menu_photo_file_id: Optional[str] = None

        self.offset = 0
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _make_request(
        self,
        method: str,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        retry_count: int = 2,
        timeout: float = 10.0,
        retry_429: bool = True,
    ) -> Optional[Dict]:
        for attempt in range(max(1, retry_count)):
            try:
                url = f"{self.base_url}/{method}"
                if files:
                    response = requests.post(
                        url,
                        data=params or {},
                        files=files,
                        timeout=timeout,
                    )
                else:
                    response = requests.post(
                        url,
                        json=params or {},
                        timeout=timeout,
                    )

                if response.status_code == 429:
                    if not retry_429:
                        return None

                    try:
                        retry_after = int(
                            response.json()
                            .get("parameters", {})
                            .get("retry_after", 1)
                        )
                    except (TypeError, ValueError, AttributeError):
                        retry_after = 1

                    if attempt + 1 < retry_count:
                        time.sleep(min(retry_after, 2))
                        continue
                    return None

                if response.status_code == 403:
                    logger.warning("Telegram returned 403 for %s", method)
                    return None

                try:
                    return response.json()
                except ValueError:
                    logger.error("Invalid JSON returned by Telegram: %s", method)
                    return None

            except requests.exceptions.Timeout:
                logger.warning(
                    "Telegram timeout: %s attempt %s/%s",
                    method,
                    attempt + 1,
                    retry_count,
                )
                if attempt + 1 < retry_count:
                    time.sleep(0.2)
            except requests.RequestException as exc:
                logger.warning("Telegram request error for %s: %s", method, exc)
                if attempt + 1 < retry_count:
                    time.sleep(0.2)
            except Exception:
                logger.exception("Unexpected Telegram request error: %s", method)
                break

        return None

    def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict] = None,
    ) -> Optional[Dict]:
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        return self._make_request("sendMessage", params)

    def send_photo(
        self,
        chat_id: int,
        caption: str,
        reply_markup: Optional[Dict] = None,
    ) -> Optional[Dict]:
        if not PHOTO_PATH.is_file():
            logger.warning("Menu photo not found: %s", PHOTO_PATH)
            return self.send_message(chat_id, caption, reply_markup)

        params = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            params["reply_markup"] = reply_markup

        try:
            with PHOTO_PATH.open("rb") as photo:
                response = self._make_request(
                    "sendPhoto",
                    params,
                    files={"photo": (PHOTO_PATH.name, photo, "image/png")},
                    timeout=15.0,
                )

            if response and response.get("ok"):
                result = response.get("result", {})
                photo_sizes = result.get("photo") or []
                if photo_sizes:
                    self._menu_photo_file_id = photo_sizes[-1].get("file_id")
            return response

        except OSError:
            logger.exception("Unable to open menu photo")
            return self.send_message(chat_id, caption, reply_markup)
        except Exception:
            logger.exception("sendPhoto failed")
            return self.send_message(chat_id, caption, reply_markup)

    def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[Dict] = None,
    ) -> Optional[Dict]:
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        return self._make_request("editMessageText", params)

    def edit_photo_caption(
        self,
        chat_id: int,
        message_id: int,
        caption: str,
        reply_markup: Optional[Dict] = None,
    ) -> Optional[Dict]:
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            params["reply_markup"] = reply_markup
        return self._make_request("editMessageCaption", params)

    def answer_callback(
        self,
        callback_id: str,
        text: Optional[str] = None,
    ) -> Optional[Dict]:
        params = {"callback_query_id": callback_id}
        if text:
            params["text"] = text
        return self._make_request(
            "answerCallbackQuery",
            params,
            retry_count=1,
            timeout=3.0,
            retry_429=False,
        )

    def answer_inline_query(
        self,
        inline_query_id: str,
        results: list,
    ) -> Optional[Dict]:
        # Inline queries are latency-sensitive. One short request, no retry,
        # and no sleeping on 429.
        params = {
            "inline_query_id": inline_query_id,
            "results": results,
            "cache_time": 30,
            "is_personal": True,
        }
        return self._make_request(
            "answerInlineQuery",
            params,
            retry_count=1,
            timeout=2.2,
            retry_429=False,
        )

    def delete_message(self, chat_id: int, message_id: int) -> Optional[Dict]:
        """Kept for compatibility; normal flow deliberately never calls it."""
        return self._make_request(
            "deleteMessage",
            {"chat_id": chat_id, "message_id": message_id},
            retry_count=1,
        )

    # ------------------------------------------------------------------
    # UI / keyboards
    # ------------------------------------------------------------------

    @staticmethod
    def _button(
        text: str,
        callback_data: Optional[str] = None,
        *,
        style: Optional[str] = None,
        emoji_id: Optional[str] = None,
    ) -> Dict:
        button = {"text": text}
        if callback_data is not None:
            button["callback_data"] = callback_data
        if style is not None:
            button["style"] = style
        if emoji_id is not None:
            # Bot API 9.4+: this is the official custom emoji mechanism
            # for buttons. Button text itself is NOT HTML-parsed.
            button["icon_custom_emoji_id"] = emoji_id
        return button

    def get_main_keyboard(self, is_admin: bool = False) -> Dict:
        keyboard = [
            [
                self._button(
                    "Свой ID + регистрация",
                    "my_id_reg",
                    style="primary",
                    emoji_id=EMOJI["id"],
                )
            ],
            [
                self._button(
                    "По ID",
                    "method_id",
                    style="success",
                    emoji_id=EMOJI["id"],
                )
            ],
            [
                self._button(
                    "Переслать сообщение",
                    "method_forward",
                    style="success",
                    emoji_id=EMOJI["registration"],
                )
            ],
            [
                self._button(
                    "Инструкция",
                    "instructions",
                    emoji_id=EMOJI["menu"],
                )
            ],
        ]

        if is_admin:
            keyboard.append(
                [
                    self._button(
                        "Админ-панель",
                        "admin_panel",
                        style="danger",
                        emoji_id=EMOJI["precision"],
                    )
                ]
            )

        return {"inline_keyboard": keyboard}

    def get_result_keyboard(self, target_id: Optional[int] = None) -> Dict:
        # For ordinary bot messages callback_data is used. For inline results
        # get_inline_result_keyboard() provides URL buttons.
        rows = [
            [
                self._button(
                    "Скачать TXT отчет",
                    "download_txt",
                    style="success",
                    emoji_id=EMOJI["download"],
                ),
                self._button(
                    "Скачать HTML отчет",
                    "download_html",
                    style="success",
                    emoji_id=EMOJI["download"],
                ),
            ],
            [
                self._button(
                    "Перейти в бота",
                    style="success",
                    emoji_id=EMOJI["go"],
                ) | {"url": f"https://t.me/{BOT_USERNAME}"}
            ],
        ]
        return {"inline_keyboard": rows}

    def get_admin_keyboard(self) -> Dict:
        return {
            "inline_keyboard": [
                [
                    self._button(
                        "Статистика",
                        "admin_stats",
                        style="primary",
                        emoji_id=EMOJI["precision"],
                    )
                ],
                [
                    self._button(
                        "Рассылка",
                        "admin_broadcast",
                        style="danger",
                        emoji_id=EMOJI["bot"],
                    )
                ],
                [
                    self._button(
                        "Назад",
                        "back",
                        style="danger",
                        emoji_id=EMOJI["go"],
                    )
                ],
            ]
        }

    def get_back_keyboard(self) -> Dict:
        return {
            "inline_keyboard": [
                [
                    self._button(
                        "Назад",
                        "back",
                        style="danger",
                        emoji_id=EMOJI["go"],
                    )
                ]
            ]
        }

    def _main_caption(self) -> str:
        return (
            f'<b>{tg_emoji(EMOJI["bot"], "👾")} REGDATEID</b>\n\n'
            f'{tg_emoji(EMOJI["id"], "🆔")} Выберите действие ниже.\n'
            f'{tg_emoji(EMOJI["registration"], "📌")} Все введённые ID и результаты '
            'остаются в чате.\n'
            f'{tg_emoji(EMOJI["bot"], "🤖")} @{BOT_USERNAME}'
        )

    def _show_menu(
        self,
        chat_id: int,
        caption: str,
        keyboard: Dict,
        *,
        is_main: bool = False,
    ) -> None:
        """Keep one photo menu message and edit only its caption/buttons."""
        message_id = self.user_menu_messages.get(chat_id)

        if message_id:
            edited = self.edit_photo_caption(
                chat_id,
                message_id,
                caption,
                keyboard,
            )
            if edited and edited.get("ok"):
                return

            edited_text = self.edit_message(
                chat_id,
                message_id,
                caption,
                keyboard,
            )
            if edited_text and edited_text.get("ok"):
                return

        response = self.send_photo(chat_id, caption, keyboard)
        if response and response.get("result"):
            self.user_menu_messages[chat_id] = response["result"]["message_id"]
        elif is_main:
            # Last-resort fallback if Telegram rejects the photo.
            response = self.send_message(chat_id, caption, keyboard)
            if response and response.get("result"):
                self.user_menu_messages[chat_id] = response["result"]["message_id"]

    # ------------------------------------------------------------------
    # Persistent storage
    # ------------------------------------------------------------------

    def register_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        reg_date: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        try:
            storage.register_user(user_id, username, reg_date, timestamp)
        except Exception:
            logger.exception("database user error")

    def save_result(
        self,
        chat_id: int,
        target_id: int,
        result_text: str,
        reg_date: datetime,
        timestamp: int,
        username: Optional[str],
        source: str,
    ) -> None:
        try:
            storage.save_result(
                chat_id=chat_id,
                target_id=target_id,
                result_text=result_text,
                reg_date=reg_date.strftime("%d.%m.%Y %H:%M:%S"),
                timestamp=timestamp,
                username=username,
                source=source,
            )
        except Exception:
            logger.exception("database result error")

    def get_stats(self) -> int:
        try:
            return storage.get_stats()
        except Exception:
            logger.exception("stats error")
            return 0

    def broadcast(self, message: str) -> int:
        try:
            users = storage.all_user_ids()
        except Exception:
            logger.exception("broadcast user list error")
            return 0

        count = 0
        for user_id in users:
            try:
                response = self.send_message(user_id, message)
                if response and response.get("ok"):
                    count += 1
            except Exception:
                logger.exception("broadcast error for %s", user_id)
            time.sleep(0.05)
        return count

    # ------------------------------------------------------------------
    # Analysis / results
    # ------------------------------------------------------------------

    def analyze(
        self,
        target_id: int,
        username: Optional[str] = None,
    ) -> Tuple[str, datetime, int]:
        timestamp = self.analyzer.calculate_timestamp(target_id)
        reg_date = datetime.fromtimestamp(timestamp / 1000)
        years, months, days = self.analyzer.calculate_age(reg_date)
        precision = self.analyzer.get_precision(target_id)

        text = (
            f'<b>├ {tg_emoji(EMOJI["id"], "👾")} ID:</b> '
            f'<code>{target_id}</code>\n'
        )
        if username:
            text += (
                f'<b>├ {tg_emoji(EMOJI["bot"], "👤")} Юзернейм:</b> '
                f'<code>@{username}</code>\n'
            )

        text += (
            f'\n<b>├ {tg_emoji(EMOJI["registration"], "📅")} Регистрация:</b> '
            f'<code>{reg_date.strftime("%d.%m.%Y %H:%M:%S")}</code>\n'
            f'<b>├ {tg_emoji(EMOJI["age"], "⏳")} Возраст:</b> '
            f'<code>{years} лет, {months} мес, {days} дн</code>\n'
            f'<b>└ {tg_emoji(EMOJI["precision"], "⚙️")} Точность:</b> '
            f'<i>{precision}</i>\n\n'
            f'<b>{tg_emoji(EMOJI["bot"], "📍")} @{BOT_USERNAME}</b>'
        )
        return text, reg_date, timestamp

    def _deliver_result(
        self,
        chat_id: int,
        target_id: int,
        username: Optional[str] = None,
        source: str = "message",
    ) -> None:
        try:
            result_text, reg_date, timestamp = self.analyze(target_id, username)
        except Exception:
            logger.exception("analysis error for ID %s", target_id)
            self.send_message(
                chat_id,
                f'{tg_emoji(EMOJI["precision"], "⚠️")} Не удалось обработать ID.',
                self.get_back_keyboard(),
            )
            return

        # Persist before/alongside delivery. The chat message itself is also
        # permanent because we never edit/delete result messages.
        self.user_data[chat_id] = {
            "result_text": result_text,
            "target_id": target_id,
            "reg_date": reg_date,
            "timestamp": timestamp,
            "username": username,
        }

        self.register_user(
            chat_id,
            username,
            reg_date.strftime("%d.%m.%Y %H:%M:%S"),
            timestamp,
        )
        self.save_result(
            chat_id,
            target_id,
            result_text,
            reg_date,
            timestamp,
            username,
            source,
        )

        # IMPORTANT: always send a new message. This preserves the full
        # history of IDs/results in Telegram.
        response = self.send_message(
            chat_id,
            result_text,
            self.get_result_keyboard(target_id),
        )
        if not response or not response.get("ok"):
            logger.warning("result message was not delivered to %s", chat_id)

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

    def process_updates(self) -> None:
        while True:
            try:
                response = self._make_request(
                    "getUpdates",
                    {
                        "offset": self.offset,
                        "timeout": 25,
                        "allowed_updates": [
                            "message",
                            "callback_query",
                            "inline_query",
                        ],
                    },
                    retry_count=2,
                    timeout=35.0,
                )

                if response and response.get("ok"):
                    for update in response.get("result", []):
                        try:
                            if "message" in update:
                                self.handle_message(update["message"])
                            elif "callback_query" in update:
                                self.handle_callback(update["callback_query"])
                            elif "inline_query" in update:
                                self.handle_inline_query(update["inline_query"])
                        except Exception:
                            logger.exception(
                                "update handling error: %s",
                                update.get("update_id"),
                            )
                        finally:
                            self.offset = update["update_id"] + 1

                time.sleep(0.05)

            except Exception:
                logger.exception("updates loop error")
                time.sleep(2)

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def handle_message(self, message: Dict) -> None:
        chat = message.get("chat") or {}
        sender = message.get("from") or {}
        chat_id = chat.get("id")
        user_id = sender.get("id", chat_id)
        username = sender.get("username")

        if chat_id is None:
            return

        try:
            storage.touch_user(user_id, username)
        except Exception:
            logger.exception("touch user error")

        text = message.get("text")
        text = text.strip() if isinstance(text, str) else None

        # /start is NEVER deleted.
        if text:
            command, _, argument = text.partition(" ")
            if command.split("@", 1)[0].lower() == "/start":
                argument = argument.strip()

                if argument.startswith("download_txt_") or argument.startswith(
                    "download_html_"
                ):
                    kind = "txt" if argument.startswith("download_txt_") else "html"
                    raw_id = argument.rsplit("_", 1)[-1]
                    if raw_id.isdigit():
                        self._deliver_result(
                            chat_id,
                            int(raw_id),
                            username,
                            source=f"deeplink_{kind}",
                        )
                    else:
                        self._show_menu(
                            chat_id,
                            f'{tg_emoji(EMOJI["precision"], "⚠️")} Неверный ID.',
                            self.get_back_keyboard(),
                        )
                    return

                self.user_states[chat_id] = None
                self._show_menu(
                    chat_id,
                    self._main_caption(),
                    self.get_main_keyboard(user_id == self.admin_id),
                    is_main=True,
                )
                return

        if text and text.lower().startswith("/reg1"):
            parts = text.split(maxsplit=1)
            raw_id = parts[1].strip() if len(parts) > 1 else ""
            if not raw_id.isdigit():
                self.send_message(
                    chat_id,
                    f'{tg_emoji(EMOJI["precision"], "⚠️")} Использование: '
                    '<code>/reg1 123456789</code>',
                    self.get_back_keyboard(),
                )
                return

            self._deliver_result(
                chat_id,
                int(raw_id),
                username,
                source="reg1",
            )
            return

        state = self.user_states.get(chat_id)

        if state == "waiting_id":
            if text and text.isdigit():
                self._deliver_result(
                    chat_id,
                    int(text),
                    username,
                    source="menu_id",
                )
                self.user_states[chat_id] = None
            else:
                self._show_menu(
                    chat_id,
                    f'{tg_emoji(EMOJI["precision"], "⚠️")} Введите числовой ID.',
                    self.get_back_keyboard(),
                )
            return

        if state == "waiting_broadcast":
            if text:
                sent_count = self.broadcast(text)
                self._show_menu(
                    chat_id,
                    f'{tg_emoji(EMOJI["bot"], "📢")} Рассылка завершена.\n'
                    f'Отправлено: <code>{sent_count}</code>',
                    self.get_back_keyboard(),
                )
                self.user_states[chat_id] = None
            return

        if state == "waiting_forward":
            forwarded = message.get("forward_from")
            if forwarded:
                target_id = forwarded.get("id")
                forwarded_username = forwarded.get("username")
                if isinstance(target_id, int):
                    self._deliver_result(
                        chat_id,
                        target_id,
                        forwarded_username,
                        source="forward",
                    )
                    self.user_states[chat_id] = None
                    return

            # New Telegram clients can expose forwarded origin differently.
            origin = message.get("forward_origin") or {}
            sender_user = origin.get("sender_user") or {}
            target_id = sender_user.get("id")
            forwarded_username = sender_user.get("username")
            if isinstance(target_id, int):
                self._deliver_result(
                    chat_id,
                    target_id,
                    forwarded_username,
                    source="forward_origin",
                )
                self.user_states[chat_id] = None
                return

        # Convenience: a bare number is an ID. We intentionally keep the
        # user's original message in the chat.
        if text and text.isdigit():
            self._deliver_result(
                chat_id,
                int(text),
                username,
                source="bare_id",
            )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def handle_callback(self, callback: Dict) -> None:
        message = callback.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        message_id = message.get("message_id")
        data = callback.get("data", "")
        callback_id = callback.get("id")
        sender = callback.get("from") or {}
        user_id = sender.get("id", chat_id)
        username = sender.get("username")

        if chat_id is None or message_id is None or not callback_id:
            return

        # Acknowledge quickly so Telegram stops the button spinner.
        # Report buttons acknowledge themselves after the file operation.
        if data not in {"download_txt", "download_html"}:
            self.answer_callback(callback_id)

        try:
            storage.touch_user(user_id, username)
        except Exception:
            logger.exception("touch user callback error")

        if data == "my_id_reg":
            self._deliver_result(
                chat_id,
                int(chat_id),
                username,
                source="my_id",
            )
            return

        if data == "method_id":
            self.user_states[chat_id] = "waiting_id"
            self._show_menu(
                chat_id,
                f'<b>{tg_emoji(EMOJI["id"], "🆔")} Введите ID аккаунта</b>\n\n'
                f'{tg_emoji(EMOJI["precision"], "ℹ️")} Отправьте только число. '
                'Ваше сообщение не будет удалено.',
                self.get_back_keyboard(),
            )
            return

        if data == "method_forward":
            self.user_states[chat_id] = "waiting_forward"
            self._show_menu(
                chat_id,
                f'<b>{tg_emoji(EMOJI["registration"], "↪️")} Перешлите сообщение</b>\n\n'
                f'{tg_emoji(EMOJI["precision"], "ℹ️")} Перешлите сообщение нужного '
                'пользователя в этот чат.',
                self.get_back_keyboard(),
            )
            return

        if data == "instructions":
            self._show_menu(
                chat_id,
                INSTRUCTIONS_TEXT,
                self.get_back_keyboard(),
            )
            return

        if data == "download_txt":
            self._send_report_file(chat_id, callback_id, "txt")
            return

        if data == "download_html":
            self._send_report_file(chat_id, callback_id, "html")
            return

        if data == "admin_panel":
            if user_id != self.admin_id:
                self.answer_callback(callback_id, "Доступ запрещён")
                return

            self._show_menu(
                chat_id,
                f'<b>{tg_emoji(EMOJI["precision"], "⚙️")} Админ-панель</b>',
                self.get_admin_keyboard(),
            )
            return

        if data == "admin_stats":
            if user_id != self.admin_id:
                self.answer_callback(callback_id, "Доступ запрещён")
                return

            stats = self.get_stats()
            self._show_menu(
                chat_id,
                f'<b>{tg_emoji(EMOJI["precision"], "📊")} Статистика</b>\n\n'
                f'Пользователей: <code>{stats}</code>',
                self.get_back_keyboard(),
            )
            return

        if data == "admin_broadcast":
            if user_id != self.admin_id:
                self.answer_callback(callback_id, "Доступ запрещён")
                return

            self.user_states[chat_id] = "waiting_broadcast"
            self._show_menu(
                chat_id,
                f'<b>{tg_emoji(EMOJI["bot"], "📢")} Введите текст рассылки</b>',
                self.get_back_keyboard(),
            )
            return

        if data == "back":
            self.user_states[chat_id] = None
            self._show_menu(
                chat_id,
                self._main_caption(),
                self.get_main_keyboard(user_id == self.admin_id),
            )

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def _send_report_file(
        self,
        chat_id: int,
        callback_id: str,
        kind: str,
    ) -> None:
        data = self.user_data.get(chat_id)
        if not data:
            try:
                data = storage.get_latest_result(chat_id)
            except Exception:
                data = None

        if not data or "target_id" not in data:
            self.answer_callback(callback_id, "Нет сохранённого результата")
            return

        try:
            target_id = int(data["target_id"])
            reg_date = data["reg_date"]
            if isinstance(reg_date, str):
                reg_date = datetime.strptime(
                    reg_date,
                    "%d.%m.%Y %H:%M:%S",
                )

            timestamp = int(data["timestamp"])
            username = data.get("username")

            years, months, days = self.analyzer.calculate_age(reg_date)
            precision = self.analyzer.get_precision(target_id)

            if kind == "txt":
                content = generate_txt_report(
                    target_id,
                    reg_date,
                    timestamp,
                    years,
                    months,
                    days,
                    precision,
                    len(MILESTONES),
                    username,
                )
                extension = "txt"
            else:
                content = generate_html_report(
                    target_id,
                    reg_date,
                    timestamp,
                    years,
                    months,
                    days,
                    precision,
                    len(MILESTONES),
                    username,
                )
                extension = "html"

            filename = REPORTS_DIR / (
                f"report_{target_id}_{int(time.time() * 1000)}.{extension}"
            )

            filename.write_text(content, encoding="utf-8")
            try:
                with filename.open("rb") as document:
                    response = self._make_request(
                        "sendDocument",
                        {"chat_id": chat_id},
                        files={
                            "document": (
                                filename.name,
                                document,
                                "text/plain"
                                if extension == "txt"
                                else "text/html",
                            )
                        },
                        retry_count=1,
                        timeout=20.0,
                    )
            finally:
                try:
                    filename.unlink(missing_ok=True)
                except OSError:
                    logger.exception("Unable to remove report file")

            if response and response.get("ok"):
                self.answer_callback(
                    callback_id,
                    f"{extension.upper()} отчёт отправлен",
                )
            else:
                self.answer_callback(callback_id, "Не удалось отправить отчёт")

        except Exception:
            logger.exception("report generation error")
            self.answer_callback(callback_id, "Ошибка формирования отчёта")

    # ------------------------------------------------------------------
    # Inline
    # ------------------------------------------------------------------

    def handle_inline_query(self, inline_query: Dict) -> None:
        """Latency-sensitive inline handler.

        No network/database work happens before answerInlineQuery except the
        final Telegram API call itself. The result builder is guaranteed to
        return a tuple.
        """
        query_id = inline_query.get("id")
        query_text = inline_query.get("query", "")

        if not query_id:
            return

        try:
            results, error = build_inline_results(
                self.inline_handler,
                query_text,
            )

            if error and not results:
                results = [
                    {
                        "type": "article",
                        "id": "invalid",
                        "title": "Введите числовой ID",
                        "description": error,
                        "input_message_content": {
                            "message_text": (
                                f'{tg_emoji(EMOJI["precision"], "⚠️")} '
                                f'<b>{error}</b>'
                            ),
                            "parse_mode": "HTML",
                        },
                    }
                ]

            if not results:
                results = [
                    {
                        "type": "article",
                        "id": "help",
                        "title": "Введите Telegram ID",
                        "description": "Пример: 123456789",
                        "input_message_content": {
                            "message_text": (
                                f'<b>{tg_emoji(EMOJI["bot"], "👾")} '
                                'Инлайн-режим</b>\n\n'
                                f'{tg_emoji(EMOJI["id"], "🆔")} '
                                'Введите числовой Telegram ID.\n'
                                f'{tg_emoji(EMOJI["precision"], "💡")} '
                                '<code>@regdateid_bot 123456789</code>'
                            ),
                            "parse_mode": "HTML",
                        },
                    }
                ]

            response = self.answer_inline_query(query_id, results)

            # Persistence happens AFTER the latency-critical answer.
            if response and response.get("ok") and results:
                first = results[0]
                if first.get("id", "").isdigit():
                    target_id = int(first["id"])
                    requester_id = int(
                        (inline_query.get("from") or {}).get("id", 0)
                    )
                    if requester_id:
                        try:
                            data = self.inline_handler.analyze_user(target_id)
                            reg_date = datetime.strptime(
                                data["reg_date"],
                                "%d.%m.%Y %H:%M:%S",
                            )
                            self.save_result(
                                requester_id,
                                target_id,
                                self.inline_handler.format_result_text(data),
                                reg_date,
                                int(data["timestamp"]),
                                None,
                                "inline",
                            )
                            self.register_user(requester_id)
                        except Exception:
                            logger.exception("inline persistence error")

        except Exception:
            # Never let one malformed update kill the polling loop.
            logger.exception("inline query handler error")
            self.answer_inline_query(
                query_id,
                [
                    {
                        "type": "article",
                        "id": "fatal",
                        "title": "Временная ошибка",
                        "description": "Попробуйте ещё раз",
                        "input_message_content": {
                            "message_text": (
                                f'{tg_emoji(EMOJI["precision"], "⚠️")} '
                                '<b>Попробуйте ещё раз.</b>'
                            ),
                            "parse_mode": "HTML",
                        },
                    }
                ],
            )


def run() -> None:
    if not TOKEN:
        print("[regbot] BOT_TOKEN_DATA не задан — бот не запущен")
        return

    print("[regbot] бот запущен, начинаю polling")
    TelegramBot(TOKEN, ADMIN_ID).process_updates()
