# -*- coding: utf-8 -*-
"""
handlers.py - Обработчики команд для КончаБота
"""

import telebot
import random
import time
import os

from . import db

# Загружаем ADMIN_IDS из переменной окружения (через запятую)
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = set()
if ADMIN_IDS_STR:
    try:
        ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip())
    except ValueError:
        pass


def register_handlers(bot: telebot.TeleBot):
    """Регистрировать все обработчики КончаБота"""

    @bot.message_handler(commands=["start"])
    def handle_start(message: telebot.types.Message):
        """Команда /start - приветствие"""
        text = (
            "👋 Привет! Я КончаБот – главный симулятор убойных выстрелов в Telegram!\n\n"
            "📝 <b>Команды:</b>\n"
            "• <code>выстрел</code> или <code>/выстрел</code> - стрелять обычно\n"
            "• <code>выстрел</code> (ответом на сообщение) - стрелять по пользователю\n"
            "• <code>/лидеры</code> - топ-10 кончащих\n"
            "• <code>/дать 10</code> (ответом) - дать кончу (админ)\n"
            "• <code>/забрать 5</code> (ответом) - забрать кончу (админ)\n\n"
            "💦 <b>Как это работает:</b>\n"
            "1️⃣ Напиши <code>выстрел</code>\n"
            "2️⃣ Получишь анимацию процесса\n"
            "3️⃣ Получишь кончу (1-3 обычно, 3-5 если по юзеру)\n"
            "4️⃣ Появишься в топ-10 лидеров"
        )
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(
        func=lambda msg: msg.text and "выстрел" in msg.text.lower(),
        content_types=["text"]
    )
    def handle_fire(message: telebot.types.Message):
        """Обработчик команды выстрела"""
        user_id = message.from_user.id
        user_name = message.from_user.first_name or message.from_user.username or "Юзер"
        chat_id = message.chat.id

        # Проверяем, есть ли reply
        if message.reply_to_message:
            # Выстрел в ответ
            target_user = message.reply_to_message.from_user
            target_id = target_user.id
            target_name = target_user.first_name or target_user.username or f"Юзер {target_id}"

            # Добавляем 3-5 кончи стреляющему
            amount = random.randint(3, 5)
            new_balance = db.add_balance(user_id, amount)

            # Финальный текст с простыми никнеймами (кликабельными)
            final_text = (
                f"<a href=\"tg://user?id={user_id}\">{user_name}</a> кон🧴ил на "
                f"<a href=\"tg://user?id={target_id}\">{target_name}</a> 😈\n"
                f"кончи всего - {new_balance}"
            )

            # Отправляем стартовое сообщение
            msg = bot.send_message(
                chat_id,
                f"[0%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [начинает подготовку...]",
                parse_mode="HTML"
            )

            # Анимация - 3 кадра
            actions = ["открывает порнхаб 🍆", "настраивает прицел 🎯", "ищет вдохновение 💭"]
            for i, action in enumerate(actions):
                time.sleep(1)
                percent = ((i + 1) / 3) * 100
                frame_text = f"[{int(percent)}%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [{action}]"
                
                try:
                    bot.edit_message_text(
                        frame_text,
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode="HTML"
                    )
                except:
                    pass

            # Финальное сообщение
            time.sleep(1)
            try:
                bot.edit_message_text(
                    final_text,
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
            except:
                pass

        else:
            # Обычный выстрел (без reply)
            amount = random.randint(1, 3)
            new_balance = db.add_balance(user_id, amount)

            # Финальный текст
            final_text = (
                f"<a href=\"tg://user?id={user_id}\">{user_name}</a> кон🧴ил 😈\n"
                f"кончи всего - {new_balance}"
            )

            # Отправляем стартовое сообщение
            msg = bot.send_message(
                chat_id,
                f"[0%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [начинает подготовку...]",
                parse_mode="HTML"
            )

            # Анимация - 3 кадра
            actions = ["открывает порнхаб 🍆", "настраивает прицел 🎯", "ищет вдохновение 💭"]
            for i, action in enumerate(actions):
                time.sleep(1)
                percent = ((i + 1) / 3) * 100
                frame_text = f"[{int(percent)}%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [{action}]"
                
                try:
                    bot.edit_message_text(
                        frame_text,
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode="HTML"
                    )
                except:
                    pass

            # Финальное сообщение
            time.sleep(1)
            try:
                bot.edit_message_text(
                    final_text,
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
            except:
                pass

    @bot.message_handler(commands=["leaders", "лидеры"])
    def handle_leaders(message: telebot.types.Message):
        """Команда /лидеры - выводит топ-10"""
        chat_id = message.chat.id

        top_users = db.get_top_users(limit=10)
        
        if not top_users:
            bot.send_message(chat_id, "Никто ещё не кончил 😢")
            return

        text = "🏆 <b>Топ-10 кончащих</b>\n\n"
        for idx, (uid, balance) in enumerate(top_users, 1):
            text += f"{idx}. <code>{balance}</code> кончи\n"

        bot.send_message(chat_id, text, parse_mode="HTML")

    @bot.message_handler(commands=["дать"])
    def handle_give(message: telebot.types.Message):
        """Администраторская команда: дать кончу"""
        user_id = message.from_user.id

        # Проверка прав администратора
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "У тебя нет прав администратора 🚫")
            return

        # Проверяем, есть ли reply
        if not message.reply_to_message:
            bot.reply_to(message, "Ответь на сообщение пользователя, кому дать кончу")
            return

        # Парсим количество из команды
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Использование: /дать <количество>")
            return

        try:
            amount = int(parts[1])
        except ValueError:
            bot.reply_to(message, "Укажи число кончи")
            return

        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.first_name or target_user.username or f"Юзер {target_id}"

        new_balance = db.add_balance(target_id, amount)

        bot.reply_to(
            message,
            f"✅ Выдал {amount} кончи <a href=\"tg://user?id={target_id}\">{target_name}</a>\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=["забрать"])
    def handle_take(message: telebot.types.Message):
        """Администраторская команда: забрать кончу"""
        user_id = message.from_user.id

        # Проверка прав администратора
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "У тебя нет прав администратора 🚫")
            return

        # Проверяем, есть ли reply
        if not message.reply_to_message:
            bot.reply_to(message, "Ответь на сообщение пользователя, у кого забрать кончу")
            return

        # Парсим количество из команды
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Использование: /забрать <количество>")
            return

        try:
            amount = int(parts[1])
        except ValueError:
            bot.reply_to(message, "Укажи число кончи")
            return

        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.first_name or target_user.username or f"Юзер {target_id}"

        new_balance = db.add_balance(target_id, -amount)

        bot.reply_to(
            message,
            f"✅ Забрал {amount} кончи у <a href=\"tg://user?id={target_id}\">{target_name}</a>\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )
