from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"""
👋 <b>Добро пожаловать в PriceHunter UZ</b>

Привет, <b>{message.from_user.full_name}</b>!

🚀 Мы поможем найти лучшие цены в Узбекистане.

Выберите действие ниже.
""",
        reply_markup=main_menu,
    )
