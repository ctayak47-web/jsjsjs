# -*- coding: utf-8 -*-
"""
bot.py
Telegram-бот для генерации МАКЕТА (мокапа) верхней части экрана профиля
в стиле iOS. Все данные — имя, юзернейм, статус, "о себе", фото —
пользователь вводит вручную. Бот НЕ обращается к реальным чужим аккаунтам
и не подтягивает данные по существующему юзернейму.

Установка зависимостей:
    pip install python-telegram-bot==21.* pillow --break-system-packages

Запуск:
    export BOT_TOKEN="ваш_токен_от_BotFather"
    python3 bot.py
"""

import io
import logging
import os
from datetime import datetime, timezone, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from render import ProfileData, render_to_bytes
from PIL import Image

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


def get_current_time(tz_offset: int) -> str:
    """Получить текущее время в указанном часовом поясе."""
    tz = timezone(timedelta(hours=tz_offset))
    now = datetime.now(tz)
    return now.strftime("%H:%M")


# ---------------- /start ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет! Я делаю профиль Telegram "
        "в стиле iOS для эдэтов.\n\n"
        "Все данные (имя, юзернейм, статус, «о себе», фото) — вымышленные. "
        "Нажми кнопку ниже, чтобы начать"
    )
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✏️ Создать профиль", callback_data="new_mockup")]]
    )
    await update.message.reply_text(text, reply_markup=keyboard)


async def new_mockup_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Введи имя, которое будет отображаться в профиле:")
    return NAME


async def new_mockup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи имя, которое будет отображаться в профиле:")
    return NAME


# ---------------- Диалог сбора данных ----------------

async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["display_name"] = update.message.text.strip()
    await update.message.reply_text(
        "Введи юзернейм (без @). Пример: design_studio"
    )
    return USERNAME


async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().lstrip("@")
    context.user_data["username"] = username

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(s, callback_data=f"status:{s}")] for s in STATUS_PRESETS]
        + [[InlineKeyboardButton("Ввести свой вариант", callback_data="status:custom")]]
    )
    await update.message.reply_text("Выбери статус или введи свой:", reply_markup=keyboard)
    return STATUS


async def status_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    value = query.data.split(":", 1)[1]
    if value == "custom":
        await query.message.reply_text("Введи свой текст статуса:")
        return STATUS
    context.user_data["status"] = value
    await query.message.reply_text(
        "Текст «о себе» (или отправь «-», чтобы пропустить этот блок):"
    )
    return BIO


async def status_custom_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["status"] = update.message.text.strip()
    await update.message.reply_text(
        "Текст «о себе» (или отправь «-», чтобы пропустить этот блок):"
    )
    return BIO


async def got_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["bio"] = None if text == "-" else text
    await update.message.reply_text(
        "Пришли фото для аватара (или отправь «-», чтобы использовать заглушку):"
    )
    return PHOTO


async def got_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    avatar_img = None
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        buf = io.BytesIO()
        await file.download_to_memory(out=buf)
        buf.seek(0)
        avatar_img = Image.open(buf)
    elif update.message.text and update.message.text.strip() == "-":
        avatar_img = None
    else:
        await update.message.reply_text("Пришли фото или «-», чтобы пропустить.")
        return PHOTO

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(tz, callback_data=f"tz:{tz}")] for tz in TIMEZONE_OPTIONS.keys()]
    )
    await update.message.reply_text("Выбери часовой пояс:", reply_markup=keyboard)
    context.user_data["avatar"] = avatar_img
    return TIMEZONE


async def timezone_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tz_name = query.data.split(":", 1)[1]
    tz_offset = TIMEZONE_OPTIONS[tz_name]
    current_time = get_current_time(tz_offset)
    
    context.user_data["time_text"] = current_time

    data = ProfileData(
        display_name=context.user_data["display_name"],
        username=context.user_data["username"],
        status=context.user_data.get("status", "был(а) недавно"),
        bio=context.user_data.get("bio"),
        avatar=context.user_data.get("avatar"),
        time_text=current_time,
    )

    png_bytes = render_to_bytes(data)
    await query.message.reply_photo(
        photo=io.BytesIO(png_bytes),
        caption="Готово",
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Отменено. Напиши /new, чтобы начать заново.")
    return ConversationHandler.END


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Задай переменную окружения BOT_TOKEN")

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(new_mockup_button, pattern="^new_mockup$"),
            CommandHandler("new", new_mockup_command),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)],
            STATUS: [
                CallbackQueryHandler(status_chosen, pattern="^status:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, status_custom_text),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_bio)],
            PHOTO: [MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, got_photo)],
            TIMEZONE: [CallbackQueryHandler(timezone_chosen, pattern="^tz:")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.run_polling()


if __name__ == "__main__":
    main()
