# -*- coding: utf-8 -*-
"""
handlers.py - Обработчики команд для КончаБота
"""

import telebot
import random
import time
import os
import html
from typing import Optional

from . import db

# Загружаем ADMIN_IDS из переменной окружения (через запятую)
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = set()
if ADMIN_IDS_STR:
    try:
        ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip())
    except ValueError:
        pass


# Пул действий для анимации (8+ разнообразных фраз)
ANIMATION_ACTIONS = [
    "открывает порнхаб 🍆",
    "смотрит категорию студентки 👨‍🎓",
    "настраивает прицел 🎯",
    "ищет вдохновение 💭",
    "включает музыку 🎵",
    "разминается перед боем 💪",
    "медитирует в ванне 🛁",
    "читает любовный роман 📖",
    "вызывает мастера по ремонту 🔧",
    "считает до десяти 🔢",
    "занимается йогой 🧘",
    "пьёт кофе для энергии ☕",
]

# Последние действия для каждого пользователя (избегаем повторений подряд)
_last_action = {}


def get_random_action(user_id: int) -> str:
    """Получить случайное действие, исключив последнее для этого пользователя"""
    available = ANIMATION_ACTIONS.copy()
    
    if user_id in _last_action:
        # Убираем последнее действие из выбора
        if _last_action[user_id] in available:
            available.remove(_last_action[user_id])
    
    action = random.choice(available) if available else "молчит 🤐"
    _last_action[user_id] = action
    return action


def escape_html(text: str) -> str:
    """Экранировать HTML-символы в тексте"""
    return html.escape(text, quote=False)


def make_user_link(user_id: int, name: str) -> str:
    """Создать HTML-ссылку на пользователя"""
    escaped_name = escape_html(name)
    return f'<a href="tg://user?id={user_id}">{escaped_name}</a>'


def register_handlers(bot: telebot.TeleBot):
    """Регистрировать все обработчики КончаБота"""

    @bot.message_handler(
        func=lambda msg: (
            msg.text and 
            ("выстрел" in msg.text.lower() or 
             msg.text.lower() == "выстрел")
        ),
        content_types=["text"]
    )
    def handle_fire(message: telebot.types.Message):
        """Обработчик команды выстрела"""
        user_id = message.from_user.id
        user_name = message.from_user.first_name or f"Юзер {user_id}"
        chat_id = message.chat.id

        # Проверяем, есть ли reply
        if message.reply_to_message:
            # Выстрел в ответ
            target_user = message.reply_to_message.from_user
            target_id = target_user.id
            target_name = target_user.first_name or f"Юзер {target_id}"

            # Добавляем 3-5 кончи стреляющему
            amount = random.randint(3, 5)
            new_balance = db.add_balance(user_id, amount)

            # Формируем итоговое сообщение
            shooter_link = make_user_link(user_id, user_name)
            target_link = make_user_link(target_id, target_name)
            
            final_text = (
                f"{shooter_link} кон🧴ил на {target_link} 😈\n"
                f"кончи всего - {new_balance}"
            )

            # Отправляем стартовое сообщение
            msg = bot.send_message(
                chat_id,
                f"[0%] {shooter_link} [начинает подготовку...]",
                parse_mode="HTML"
            )

            # Анимация - 3-4 кадра
            for frame in range(1, 4):
                time.sleep(1)
                percent = (frame / 3) * 100
                action = get_random_action(user_id)
                frame_text = f"[{int(percent)}%] {shooter_link} [{action}]"
                
                try:
                    bot.edit_message_text(
                        frame_text,
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"[КончаБот] Ошибка при редактировании сообщения: {e}")

            # Финальное сообщение
            time.sleep(1)
            try:
                bot.edit_message_text(
                    final_text,
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"[КончаБот] Ошибка при отправке финального сообщения: {e}")

        else:
            # Обычный выстрел (без reply)
            amount = random.randint(1, 3)
            new_balance = db.add_balance(user_id, amount)

            # Формируем итоговое сообщение
            user_link = make_user_link(user_id, user_name)
            
            final_text = (
                f"{user_link} кон🧴ил 😈\n"
                f"кончи всего - {new_balance}"
            )

            # Отправляем стартовое сообщение
            msg = bot.send_message(
                chat_id,
                f"[0%] {user_link} [начинает подготовку...]",
                parse_mode="HTML"
            )

            # Анимация - 3-4 кадра
            for frame in range(1, 4):
                time.sleep(1)
                percent = (frame / 3) * 100
                action = get_random_action(user_id)
                frame_text = f"[{int(percent)}%] {user_link} [{action}]"
                
                try:
                    bot.edit_message_text(
                        frame_text,
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"[КончаБот] Ошибка при редактировании сообщения: {e}")

            # Финальное сообщение
            time.sleep(1)
            try:
                bot.edit_message_text(
                    final_text,
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"[КончаБот] Ошибка при отправке финального сообщения: {e}")

    @bot.message_handler(commands=["leaders", "лидеры"])
    def handle_leaders(message: telebot.types.Message):
        """Команда /лидеры кончи - выводит топ-10"""
        chat_id = message.chat.id

        top_users = db.get_top_users(limit=10)
        
        if not top_users:
            bot.send_message(chat_id, "Никто ещё не кончил 😢")
            return

        text = "<b>🏆 Топ-10 кончащих</b>\n\n"
        for idx, (uid, balance) in enumerate(top_users, 1):
            text += f"{idx}. Юзер {uid}: <code>{balance}</code> кончи\n"

        bot.send_message(chat_id, text, parse_mode="HTML")

    @bot.message_handler(commands=["дать"])
    def handle_give(message: telebot.types.Message):
        """Администраторская команда: дать кончу на ответ сообщение"""
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
        target_name = target_user.first_name or f"Юзер {target_id}"

        new_balance = db.add_balance(target_id, amount)
        target_link = make_user_link(target_id, target_name)

        bot.reply_to(
            message,
            f"✅ Выдал {amount} кончи {target_link}\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=["забрать"])
    def handle_take(message: telebot.types.Message):
        """Администраторская команда: забрать кончу на ответ сообщение"""
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
        target_name = target_user.first_name or f"Юзер {target_id}"

        new_balance = db.add_balance(target_id, -amount)
        target_link = make_user_link(target_id, target_name)

        bot.reply_to(
            message,
            f"✅ Забрал {amount} кончи у {target_link}\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=["выстрел"])
    def handle_fire_command(message: telebot.types.Message):
        """Команда /выстрел"""
        # Перенаправляем на обработчик текстовой команды
        handle_fire(message)
