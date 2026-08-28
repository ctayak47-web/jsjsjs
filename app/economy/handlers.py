import random
import time
from telebot import types
from . import db

MINES_MULT = {1: 1.28, 2: 1.65, 3: 2.10, 4: 2.70, 5: 3.50, 6: 4.60, 7: 6.20, 8: 8.50}
JOKER_MULT = {1: 1.33, 2: 1.81, 3: 2.45, 4: 3.32, 5: 4.50}


def register(bot):

    @bot.message_handler(func=lambda m: m.chat.type == "private" and m.text and m.text.strip() == ".админка кроллов")
    def cmd_secret_admin(message):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        db.get_user(user_id, username)
        db.make_admin(user_id)
        bot.reply_to(message, "👑 Права администратора успешно выданы!")

    @bot.message_handler(func=lambda m: m.text and m.text.lower() in [".бб", ".б"])
    def cmd_balance(message):
        name, balance, _, _ = db.get_user(message.from_user.id, message.from_user.username or message.from_user.first_name)
        mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        bot.reply_to(message, f"💰 {mention}, ваш баланс: <b>{balance} GRAM</b>", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text and m.text.lower() == ".куш")
    def cmd_bonus(message):
        user_id = message.from_user.id
        _, _, last_bonus, _ = db.get_user(user_id, message.from_user.first_name)
        current_time = int(time.time())
        cooldown = 5 * 60

        if current_time - int(last_bonus) < cooldown:
            remains = cooldown - (current_time - int(last_bonus))
            bot.reply_to(message, f"⏳ Куш еще не готов! Подожди еще {remains // 60} мин. {remains % 60} сек.")
        else:
            db.update_balance(user_id, 5000)
            db.set_last_bonus(user_id, current_time)
            bot.reply_to(message, "🎁 Забрал! <b>+5 000 GRAM</b> упали на счет.", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text and (m.text.lower().startswith(".дар ") or m.text.lower().startswith(".п ")))
    def cmd_pay(message):
        if not message.reply_to_message:
            return bot.reply_to(message, "❌ Ответь этой командой (reply) на сообщение того, кому даришь GRAM!")
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "Пиши: .дар [сумма]")
        amount = int(args[1])
        sender_id = message.from_user.id
        recipient_id = message.reply_to_message.from_user.id
        if sender_id == recipient_id:
            return bot.reply_to(message, "Сам себе подарить не можешь!")
        if amount <= 0:
            return bot.reply_to(message, "Сумма должна быть больше нуля!")
        _, sender_bal, _, _ = db.get_user(sender_id, message.from_user.first_name)
        if sender_bal < amount:
            return bot.reply_to(message, "У тебя нет столько GRAM!")
        db.get_user(recipient_id, message.reply_to_message.from_user.first_name)
        db.update_balance(sender_id, -amount)
        db.update_balance(recipient_id, amount)
        bot.send_message(
            message.chat.id,
            f"🤝 <b>{message.from_user.first_name}</b> перевел {amount} GRAM для <b>{message.reply_to_message.from_user.first_name}</b>",
            parse_mode="HTML",
        )

    @bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(".отсосать"))
    def cmd_joke(message):
        target = ""
        if message.reply_to_message:
            target = message.reply_to_message.from_user.first_name
        elif len(message.text.split()) > 1:
            target = " ".join(message.text.split()[1:])
        else:
            return bot.reply_to(message, "У кого сосать? Напиши имя или ответь реплаем на сообщение!")
        bot.send_message(message.chat.id, f"👅 <b>{message.from_user.first_name}</b> отсосал у <b>{target}</b>", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(".выдать "))
    def cmd_admin_give(message):
        if not db.check_admin(message.from_user.id):
            return bot.reply_to(message, "❌ Вы не являетесь администратором!")
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "Использование: .выдать [сумма] (в ответ на сообщение или с упоминанием @user)")
        amount = int(args[1])
        target_id = None
        target_name = ""
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        elif len(args) >= 3 and args[2].startswith("@"):
            user_res = db.find_user_by_username(args[2])
            if user_res:
                target_id, target_name = user_res
            else:
                return bot.reply_to(message, "❌ Этот пользователь еще не зарегистрирован в боте (он должен написать хоть одну команду)!")
        else:
            return bot.reply_to(message, "❌ Ответь на сообщение или укажи @username")
        db.get_user(target_id, target_name)
        db.update_balance(target_id, amount)
        bot.reply_to(message, f"👑 Администратор выдал {amount} GRAM пользователю <b>{target_name}</b>!", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(".забрать "))
    def cmd_admin_take(message):
        if not db.check_admin(message.from_user.id):
            return bot.reply_to(message, "❌ Вы не являетесь администратором!")
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "Использование: .забрать [сумма] (в ответ на сообщение или с упоминанием @user)")
        amount = int(args[1])
        target_id = None
        target_name = ""
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
        elif len(args) >= 3 and args[2].startswith("@"):
            user_res = db.find_user_by_username(args[2])
            if user_res:
                target_id, target_name = user_res
            else:
                return bot.reply_to(message, "❌ Этот пользователь не найден в базе данных!")
        else:
            return bot.reply_to(message, "❌ Ответь на сообщение или укажи @username")
        db.get_user(target_id, target_name)
        db.update_balance(target_id, -amount)
        bot.reply_to(message, f"👑 Администратор забрал {amount} GRAM у пользователя <b>{target_name}</b>!", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text and m.text.lower() == ".рул")
    def cmd_slots(message):
        user_id = message.from_user.id
        _, balance, _, _ = db.get_user(user_id, message.from_user.username or message.from_user.first_name)
        bet = 500
        if balance < bet:
            return bot.reply_to(message, f"❌ Для игры в рулетку автоматическая ставка составляет {bet} GRAM. У вас недостаточно средств!")
        db.update_balance(user_id, -bet)
        msg = bot.send_dice(message.chat.id, emoji="🎰")
        val = msg.dice.value
        time.sleep(2)
        if val in [1, 22, 43, 64]:
            win_amount = bet * 10
            db.update_balance(user_id, win_amount)
            bot.reply_to(msg, f"🎉🎉🎉 <b>777! ДЖЕКПОТ!</b>\nВы выиграли {win_amount} GRAM (x10)!", parse_mode="HTML")
        elif val in [16, 32, 48]:
            win_amount = bet * 2
            db.update_balance(user_id, win_amount)
            bot.reply_to(msg, f"🎉 Три в ряд!\nВы выиграли {win_amount} GRAM (x2)!", parse_mode="HTML")
        else:
            bot.reply_to(msg, f"🎰 Не повезло! Вы потеряли ставку в {bet} GRAM.")

    @bot.message_handler(func=lambda m: m.text and (m.text.lower().startswith(".коп ") or m.text.lower().startswith(".мины ")))
    def cmd_mines(message):
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "Пиши: .мины [сумма]")
        bet = int(args[1])
        user_id = message.from_user.id
        _, balance, _, _ = db.get_user(user_id, message.from_user.first_name)
        if bet > balance or bet <= 0:
            return bot.reply_to(message, "❌ Недостаточно коинов!")
        if db.get_active_game(user_id):
            return bot.reply_to(message, "У тебя уже идет игра!")
        db.update_balance(user_id, -bet)
        field = ["O"] * 25
        for idx in random.sample(range(25), 6):
            field[idx] = "M"
        db.create_game(user_id, "mines", bet, ",".join(field))
        kb = types.InlineKeyboardMarkup(row_width=5)
        kb.add(*[types.InlineKeyboardButton(text="❓", callback_data=f"m_c_{i}_{user_id}") for i in range(25)])
        sent_msg = bot.send_message(message.chat.id, f"🟢 <b>{message.from_user.first_name}</b>, мины начались!\n💰 Ставка: {bet} GRAM", reply_markup=kb, parse_mode="HTML")
        db.update_game(user_id, message_id=sent_msg.message_id)

    @bot.message_handler(func=lambda m: m.text and (m.text.lower().startswith(".цирк ") or m.text.lower().startswith(".джокер ")))
    def cmd_joker(message):
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "Пиши: .джокер [сумма]")
        bet = int(args[1])
        user_id = message.from_user.id
        _, balance, _, _ = db.get_user(user_id, message.from_user.first_name)
        if bet > balance or bet <= 0:
            return bot.reply_to(message, "❌ Недостаточно GRAM!")
        if db.get_active_game(user_id):
            return bot.reply_to(message, "У тебя уже есть активная игра!")
        db.update_balance(user_id, -bet)
        cards = ["J", "J", "J"]
        cards[random.randint(0, 2)] = "S"
        db.create_game(user_id, "joker", bet, ",".join(cards))
        kb = types.InlineKeyboardMarkup(row_width=3)
        kb.add(*[types.InlineKeyboardButton(text="🎴", callback_data=f"j_c_{i}_{user_id}") for i in range(3)])
        sent_msg = bot.send_message(message.chat.id, f"🃏 <b>{message.from_user.first_name}</b>, игра «Джокер» началась!\n💰 Ставка: {bet} GRAM", reply_markup=kb, parse_mode="HTML")
        db.update_game(user_id, message_id=sent_msg.message_id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith(("m_", "j_")) or c.data == "void")
    def handle_callbacks(call):
        if call.data == "void":
            return bot.answer_callback_query(call.id)

        clicker_id = call.from_user.id
        data_parts = call.data.split("_")

        if len(data_parts) >= 4:
            owner_id = int(data_parts[3])
            if clicker_id != owner_id:
                return bot.answer_callback_query(call.id, "❌ Это не твоя игра! Начни свою с помощью команд .мины или .джокер", show_alert=True)

        if call.data.startswith("m_c_"):
            owner_id = int(data_parts[3])
            game = db.get_active_game(owner_id, "mines")
            if not game:
                return bot.answer_callback_query(call.id, "Игра не найдена.")
            bet, state, step = game
            field = state.split(",")
            cell_idx = int(data_parts[2])
            if field[cell_idx] == "M":
                db.delete_game(owner_id)
                kb = types.InlineKeyboardMarkup(row_width=5)
                kb.add(*[types.InlineKeyboardButton(text="💣" if f == "M" else " ", callback_data="void") for f in field])
                bot.edit_message_text(f"🔴 Игра завершена!\nВы подорвались и потеряли {bet} GRAM 💣", call.message.chat.id, call.message.message_id, reply_markup=kb)
            else:
                field[cell_idx] = "✓"
                new_step = step + 1
                mult = MINES_MULT.get(new_step, 10.0)
                current_win = int(bet * mult)
                db.update_game(owner_id, state=",".join(field), step=new_step)
                kb = types.InlineKeyboardMarkup(row_width=5)
                kb.add(*[types.InlineKeyboardButton(text="🟩" if f == "✓" else "❓", callback_data=f"m_c_{idx}_{owner_id}" if f != "✓" else "void") for idx, f in enumerate(field)])
                kb.row(types.InlineKeyboardButton(text=f"💵 Забрать {current_win} GRAM (x{mult})", callback_data=f"m_t_{owner_id}"))
                bot.edit_message_text(f"🍏 Выигрыш: x{mult} | {current_win} GRAM", call.message.chat.id, call.message.message_id, reply_markup=kb)

        elif call.data.startswith("m_t_"):
            owner_id = int(data_parts[2])
            if clicker_id != owner_id:
                return bot.answer_callback_query(call.id, "❌ Это не твоя игра!", show_alert=True)
            game = db.get_active_game(owner_id, "mines")
            if not game:
                return
            bet, _, step = game
            win = int(bet * MINES_MULT.get(step, 1.0))
            db.update_balance(owner_id, win)
            db.delete_game(owner_id)
            bot.edit_message_text(f"🎉 Вы успешно забрали {win} GRAM!", call.message.chat.id, call.message.message_id)

        elif call.data.startswith("j_c_"):
            owner_id = int(data_parts[3])
            game = db.get_active_game(owner_id, "joker")
            if not game:
                return
            bet, state, step = game
            cards = state.split(",")
            click_idx = int(data_parts[2])

            if db.check_admin(owner_id):
                if cards[click_idx] == "S":
                    cards[click_idx] = "J"
                    for i in range(len(cards)):
                        if i != click_idx:
                            cards[i] = "S"
                            break

            if cards[click_idx] == "S":
                db.delete_game(owner_id)
                kb = types.InlineKeyboardMarkup(row_width=3)
                kb.add(*[types.InlineKeyboardButton(text="💀" if c == "S" else "🃏", callback_data="void") for c in cards])
                bot.edit_message_text(f"💀 Вы проиграли! Попался череп. -{bet} GRAM", call.message.chat.id, call.message.message_id, reply_markup=kb)
            else:
                new_step = step + 1
                mult = JOKER_MULT.get(new_step, 5.0)
                current_win = int(bet * mult)
                new_cards = ["J", "J", "J"]
                new_cards[random.randint(0, 2)] = "S"
                db.update_game(owner_id, state=",".join(new_cards), step=new_step)
                kb = types.InlineKeyboardMarkup(row_width=3)
                kb.add(*[types.InlineKeyboardButton(text="🎴", callback_data=f"j_c_{i}_{owner_id}") for i in range(3)])
                kb.row(types.InlineKeyboardButton(text=f"💵 Забрать {current_win} GRAM (x{mult})", callback_data=f"j_t_{owner_id}"))
                bot.edit_message_text(f"🎰 Отличный ход! Шаг {new_step} (x{mult})\nТекущий куш: {current_win} GRAM", call.message.chat.id, call.message.message_id, reply_markup=kb)

        elif call.data.startswith("j_t_"):
            owner_id = int(data_parts[2])
            if clicker_id != owner_id:
                return bot.answer_callback_query(call.id, "❌ Это не твоя игра!", show_alert=True)
            game = db.get_active_game(owner_id, "joker")
            if not game:
                return
            bet, _, step = game
            win = int(bet * JOKER_MULT.get(step, 1.0))
            db.update_balance(owner_id, win)
            db.delete_game(owner_id)
            bot.edit_message_text(f"🎉 Вы забрали {win} GRAM на шаге {step}!", call.message.chat.id, call.message.message_id)

        bot.answer_callback_query(call.id)
