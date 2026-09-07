import os
from aiogram import Bot,Dispatcher,F
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,WebAppInfo

TOKEN=os.getenv("BOT_TOKEN")
WEBAPP_URL=os.getenv("WEBAPP_URL","https://YOUR-SERVICE.onrender.com")

dp=Dispatcher()

def kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 ОТКРЫТЬ CROLDROP",web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🎁 БОНУС — 1000 ⭐",callback_data="bonus")]
    ])

@dp.message(CommandStart())
async def start(message:Message):
    await message.answer(
        f"👋 Добро пожаловать в CrolDrop, {message.from_user.first_name}!\n\n"
        "◈ Собирай коллекционные NFT\n"
        "⬆️ Рискуй в Upgrade\n"
        "📦 Открывай новые предметы\n"
        "🛒 Исследуй маркет\n\n"
        "🎁 Забери стартовый бонус — 1000 ⭐",
        reply_markup=kb()
    )

@dp.callback_query(F.data=="bonus")
async def bonus(q:CallbackQuery):
    from backend.database import ensure_user,conn
    tid=q.from_user.id
    ensure_user(tid,q.from_user.username or "",q.from_user.first_name)
    c=conn();u=c.execute("SELECT stars,bonus_claimed FROM users WHERE telegram_id=?",(tid,)).fetchone()
    if u["bonus_claimed"]:
        text=f"❌ Бонус уже получен\n\n⭐ Баланс: {u['stars']}"
    else:
        c.execute("UPDATE users SET stars=stars+1000,bonus_claimed=1 WHERE telegram_id=?",(tid,));c.commit()
        stars=c.execute("SELECT stars FROM users WHERE telegram_id=?",(tid,)).fetchone()[0]
        text=f"🎉 БОНУС ПОЛУЧЕН\n\n⭐ +1000 Звёзд\n\nБаланс: {stars} ⭐"
    c.close();await q.answer();await q.message.answer(text)

async def start_bot():
    if not TOKEN: raise RuntimeError("BOT_TOKEN is not set")
    bot=Bot(TOKEN)
    await dp.start_polling(bot)
