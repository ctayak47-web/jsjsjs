import os
import telebot

from .economy import db as edb
from .economy import handlers as ehandlers

TOKEN = os.environ.get("BOT_TOKEN", "")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

ehandlers.register(bot)

def run():
    if not TOKEN:
        print("[combined] BOT_TOKEN не задан — бот не запущен")
        return
    edb.init()
    print("[combined] бот запущен, начинаю polling")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
