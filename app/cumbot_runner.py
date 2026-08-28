# -*- coding: utf-8 -*-
"""
cumbot_runner.py - Запуск КончаБота отдельным модулем
"""

import os
import telebot

from .cumbot import db, handlers

TOKEN = os.environ.get("BOT_TOKEN_CUM", "")


def create_bot() -> telebot.TeleBot:
    """Создать и сконфигурировать КончаБота"""
    if not TOKEN:
        print("[cumbot] BOT_TOKEN_CUM не задан — бот не создан")
        return None
    
    bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
    
    # Регистрируем обработчики
    handlers.register_handlers(bot)
    
    return bot


def run(bot: telebot.TeleBot):
    """Запустить КончаБота в режиме polling"""
    if not bot:
        print("[cumbot] Бот не инициализирован")
        return
    
    try:
        db.init()
        print("[cumbot] бот запущен, начинаю polling")
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except Exception as e:
        print(f"[cumbot] Ошибка: {e}")
