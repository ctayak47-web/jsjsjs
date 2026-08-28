# -*- coding: utf-8 -*-
"""
profile_bot.py - Адаптированный профиль-бот для интеграции
Генерация мокапа профиля Telegram в стиле iOS
"""

import io
import logging
import os
from datetime import datetime, timezone, timedelta

import telebot
from telebot import types
from PIL import Image

# Импортируем функции рендеринга
from render import ProfileData, render_to_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
NAME, USERNAME, STATUS, BIO, PHOTO, TIMEZONE = range(6)

STATUS_PRESETS = ["в сети", "был(а) недавно", "не в сети"]

TIMEZONE_OPTIONS = {
    "МСК": 3,
    "МСК +1": 4,
    "МСК +2": 5,
}

TOKEN = os.environ.get("BOT_TOKEN_PROFILE", "")


def get_current_time(tz_offset: int) -> str:
    """Получить текущее время в указанном часовом поясе."""
    tz = timezone(timedelta(hours=tz_offset))
    now = datetime.now(tz)
    return now.strftime("%H:%M")


def register_handlers(bot: telebot.TeleBot):
    """Регистрировать все обработчики профиль-бота"""

    @bot.message_handler(commands=["start"])
    def start_handler(message: types.Message):
        text = (
            "Привет! Я делаю профиль Telegram "
            "в стиле iOS для эдэтов.\n\n"
            "Все данные (имя, юзернейм, статус, «о себе», фото) — вымышленные. "
            "Нажми кнопку ниже, чтобы начать"
        )
        keyboard = types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("✏️ Создать профиль", callback_data="new_mockup")]]
        )
        bot.reply_to(message, text, reply_markup=keyboard)

    @bot.message_handler(commands=["new"])
    def new_mockup_command_handler(message: types.Message):
        bot.reply_to(message, "Введи имя, которое будет отображаться в профиле:")
        bot.register_next_step_handler(message, got_name_handler)

    @bot.callback_query_handler(func=lambda call: call.data == "new_mockup")
    def new_mockup_button_handler(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "Введи имя, которое будет отображаться в профиле:")
        bot.register_next_step_handler(msg, got_name_handler)

    def got_name_handler(message: types.Message):
        if message.text:
            user_data = {"display_name": message.text.strip()}
            msg = bot.reply_to(message, "Введи юзернейм (без @). Пример: design_studio")
            bot.register_next_step_handler(msg, got_username_handler, user_data)

    def got_username_handler(message: types.Message, user_data: dict):
        if message.text:
            username = message.text.strip().lstrip("@")
            user_data["username"] = username

            keyboard = types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton(s, callback_data=f"status:{s}")] for s in STATUS_PRESETS]
                + [[types.InlineKeyboardButton("Ввести свой вариант", callback_data="status:custom")]]
            )
            msg = bot.send_message(message.chat.id, "Выбери статус или введи свой:", reply_markup=keyboard)
            
            # Сохраняем user_data в callback контексте
            bot._profile_user_data = {**bot._profile_user_data, message.from_user.id: user_data}

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status:"))
    def status_chosen_handler(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)
        value = call.data.split(":", 1)[1]
        
        if not hasattr(bot, '_profile_user_data'):
            bot._profile_user_data = {}
        
        user_data = bot._profile_user_data.get(call.from_user.id, {})
        
        if value == "custom":
            msg = bot.send_message(call.message.chat.id, "Введи свой текст статуса:")
            bot.register_next_step_handler(msg, status_custom_text_handler, user_data)
        else:
            user_data["status"] = value
            msg = bot.send_message(call.message.chat.id, 
                "Текст «о себе» (или отправь «-», чтобы пропустить этот блок):")
            bot.register_next_step_handler(msg, got_bio_handler, user_data)

    def status_custom_text_handler(message: types.Message, user_data: dict):
        if message.text:
            user_data["status"] = message.text.strip()
            msg = bot.reply_to(message, 
                "Текст «о себе» (или отправь «-», чтобы пропустить этот блок):")
            bot.register_next_step_handler(msg, got_bio_handler, user_data)

    def got_bio_handler(message: types.Message, user_data: dict):
        if message.text:
            text = message.text.strip()
            user_data["bio"] = None if text == "-" else text
            msg = bot.reply_to(message,
                "Пришли фото для аватара (или отправь «-», чтобы использовать заглушку):")
            bot.register_next_step_handler(msg, got_photo_handler, user_data)

    def got_photo_handler(message: types.Message, user_data: dict):
        avatar_img = None
        
        if message.photo:
            file = bot.get_file(message.photo[-1].file_id)
            buf = io.BytesIO()
            downloaded_file = bot.download_file(file.file_path)
            buf.write(downloaded_file)
            buf.seek(0)
            avatar_img = Image.open(buf).convert("RGBA")
        elif message.text and message.text.strip() == "-":
            avatar_img = None
        else:
            msg = bot.reply_to(message, "Пришли фото или «-», чтобы пропустить.")
            bot.register_next_step_handler(msg, got_photo_handler, user_data)
            return

        user_data["avatar"] = avatar_img

        keyboard = types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(tz, callback_data=f"tz:{tz}")] for tz in TIMEZONE_OPTIONS.keys()]
        )
        msg = bot.send_message(message.chat.id, "Выбери часовой пояс:", reply_markup=keyboard)
        
        if not hasattr(bot, '_profile_user_data'):
            bot._profile_user_data = {}
        bot._profile_user_data[message.from_user.id] = user_data

    @bot.callback_query_handler(func=lambda call: call.data.startswith("tz:"))
    def timezone_chosen_handler(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)
        tz_name = call.data.split(":", 1)[1]
        tz_offset = TIMEZONE_OPTIONS[tz_name]
        current_time = get_current_time(tz_offset)

        if not hasattr(bot, '_profile_user_data'):
            bot._profile_user_data = {}
        
        user_data = bot._profile_user_data.get(call.from_user.id, {})

        data = ProfileData(
            display_name=user_data.get("display_name", "Юзер"),
            username=user_data.get("username", "user"),
            status=user_data.get("status", "был(а) недавно"),
            bio=user_data.get("bio"),
            avatar=user_data.get("avatar"),
            time_text=current_time,
        )

        png_bytes = render_to_bytes(data)
        bot.send_photo(
            call.message.chat.id,
            photo=io.BytesIO(png_bytes),
            caption="Готово"
        )
        
        # Очищаем данные
        if call.from_user.id in bot._profile_user_data:
            del bot._profile_user_data[call.from_user.id]


def create_bot() -> telebot.TeleBot:
    """Создать и сконфигурировать профиль-бота"""
    if not TOKEN:
        print("[profile_bot] BOT_TOKEN_PROFILE не задан — бот не создан")
        return None
    
    bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
    bot._profile_user_data = {}
    
    register_handlers(bot)
    
    return bot


def run(bot: telebot.TeleBot):
    """Запустить профиль-бота в режиме polling"""
    if not bot:
        print("[profile_bot] Бот не инициализирован")
        return
    
    try:
        print("[profile_bot] бот запущен, начинаю polling")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"[profile_bot] Ошибка: {e}")
