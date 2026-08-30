import os
import logging

import telebot

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN_DATA", "")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML") if TOKEN else None

if bot:

    @bot.message_handler(commands=["start"])
    def handle_start(message: telebot.types.Message):
        bot.reply_to(
            message,
            "🚧 regbot временно недоступен (заглушка). "
            "Команда /reg1 пока не реализована."
        )

    @bot.message_handler(commands=["reg1"])
    def handle_reg1(message: telebot.types.Message):
        bot.reply_to(
            message,
            "🚧 Эта функция ещё не готова. Загляни позже."
        )


def run():
    if not TOKEN:
        print("[regbot] BOT_TOKEN_DATA не задан — бот не запущен")
        return

    if not bot:
        print("[regbot] Бот не инициализирован")
        return

    try:
        print("[regbot] бот запущен (заглушка), начинаю polling")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"[regbot] Ошибка: {e}")
