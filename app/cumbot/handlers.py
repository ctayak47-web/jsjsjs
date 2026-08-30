import telebot
import random
import time
import os

from . import db

ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = set()
if ADMIN_IDS_STR:
    try:
        ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip())
    except ValueError:
        pass

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

COOLDOWN_SECONDS = 180  # 3 минуты


def _format_remaining(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    if minutes > 0 and secs > 0:
        return f"{minutes} мин {secs} сек"
    if minutes > 0:
        return f"{minutes} мин"
    return f"{secs} сек"


def register_handlers(bot: telebot.TeleBot):

    try:
        bot_username = bot.get_me().username
    except Exception:
        bot_username = None

    @bot.message_handler(commands=["start"])
    def handle_start(message: telebot.types.Message):
        text = (
            "👋 Привет! Я КончаБот – главный симулятор убойных выстрелов в Telegram!\n\n"
            "📝 <b>Команды:</b>\n"
            "• <code>выстрел</code> или <code>.выстрел</code> - стрелять\n"
            "• <code>выстрел</code> (ответом) - стрелять по пользователю\n"
            "• /лидеры - топ-10 кончащих\n"
            "• /статистика - твоя статистика\n\n"
            "⏳ Перезарядка: 3 минуты"
        )

        keyboard = None
        if bot_username:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    "➕ Добавить в группу",
                    url=f"https://t.me/{bot_username}?startgroup=true",
                )
            )

        bot.reply_to(message, text, parse_mode="HTML", reply_markup=keyboard)

    @bot.message_handler(
        func=lambda msg: msg.text and (
            "выстрел" in msg.text.lower() or msg.text.lower().startswith(".выстрел")
        ),
        content_types=["text"]
    )
    def handle_fire(message: telebot.types.Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name or message.from_user.username or "Юзер"
        chat_id = message.chat.id

        now = time.time()
        last = db.get_last_fire(user_id)
        elapsed = now - last
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed)
            bot.reply_to(
                message,
                f"⏳ Перезарядка! Подожди ещё {_format_remaining(remaining)}."
            )
            return
        db.set_last_fire(user_id, now)

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            target_id = target_user.id
            target_name = target_user.first_name or target_user.username or f"Юзер {target_id}"

            amount = random.randint(3, 5)
            new_balance = db.add_balance(user_id, amount, username=user_name)

            final_text = (
                f"💦 <a href=\"tg://user?id={user_id}\">{user_name}</a> кончил на "
                f"<a href=\"tg://user?id={target_id}\">{target_name}</a> 😈\n"
                f"📊 Всего конч: {new_balance}"
            )

            msg = bot.send_message(
                chat_id,
                f"[0%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [начинает подготовку...]",
                parse_mode="HTML"
            )

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
            amount = random.randint(1, 3)
            new_balance = db.add_balance(user_id, amount, username=user_name)

            final_text = (
                f"💦 <a href=\"tg://user?id={user_id}\">{user_name}</a> кончил 😈\n"
                f"📊 Всего конч: {new_balance}"
            )

            msg = bot.send_message(
                chat_id,
                f"[0%] <a href=\"tg://user?id={user_id}\">{user_name}</a> [начинает подготовку...]",
                parse_mode="HTML"
            )

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
        chat_id = message.chat.id

        top_users = db.get_top_users(limit=10)

        if not top_users:
            bot.send_message(chat_id, "Никто ещё не кончил 😢")
            return

        text = "🏆 <b>Топ-10 кончащих</b>\n\n"
        for idx, (uid, uname, balance) in enumerate(top_users, 1):
            display_name = uname or f"Юзер {uid}"
            rank = MEDALS.get(idx, f"{idx}.")
            text += (
                f"{rank} <a href=\"tg://user?id={uid}\">{display_name}</a> — {balance} кончи\n"
            )

        bot.send_message(chat_id, text, parse_mode="HTML")

    @bot.message_handler(commands=["статистика", "stats"])
    def handle_stats(message: telebot.types.Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name or message.from_user.username or "Юзер"
        balance = db.get_balance(user_id)

        text = (
            f"📊 <b>Статистика</b>\n\n"
            f"<a href=\"tg://user?id={user_id}\">{user_name}</a>\n"
            f"Всего кончи: <code>{balance}</code>"
        )
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=["дать"])
    def handle_give(message: telebot.types.Message):
        user_id = message.from_user.id

        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "У тебя нет прав администратора 🚫")
            return

        if not message.reply_to_message:
            bot.reply_to(message, "Ответь на сообщение пользователя, кому дать кончу")
            return

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

        new_balance = db.add_balance(target_id, amount, username=target_name)

        bot.reply_to(
            message,
            f"✅ Выдал {amount} кончи <a href=\"tg://user?id={target_id}\">{target_name}</a>\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=["забрать"])
    def handle_take(message: telebot.types.Message):
        user_id = message.from_user.id

        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "У тебя нет прав администратора 🚫")
            return

        if not message.reply_to_message:
            bot.reply_to(message, "Ответь на сообщение пользователя, у кого забрать кончу")
            return

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

        new_balance = db.add_balance(target_id, -amount, username=target_name)

        bot.reply_to(
            message,
            f"✅ Забрал {amount} кончи у <a href=\"tg://user?id={target_id}\">{target_name}</a>\n"
            f"Новый баланс: {new_balance}",
            parse_mode="HTML"
        )