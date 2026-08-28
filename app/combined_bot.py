"""
combined_bot — один Telegram-бот (один токен) с экономикой GRAM.

Функции:
  • Экономика GRAM — виртуальная валюта и мини-игры (.бб, .куш, .мины, .джокер, .рул, ...)

Обработчики зарегистрированы на ОДНОМ экземпляре telebot.TeleBot, чтобы не было
конфликта getUpdates (два polling-цикла с одним токеном работать не могут).
"""

import os
import telebot

from .economy import db as edb
from .economy import handlers as ehandlers

TOKEN = os.environ.get("BOT_TOKEN", "")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# Регистрируем обработчики экономики
ehandlers.register(bot)


def run():
    if not TOKEN:
        print("[combined] BOT_TOKEN не задан — бот не запущен")
        return
    edb.init()
    print("[combined] бот запущен, начинаю polling")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
