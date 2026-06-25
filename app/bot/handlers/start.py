from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 <b>Добро пожаловать в PriceHunter UZ</b>\n\n"
        "🚀 Самый умный поиск цен в Узбекистане.\n\n"
        "Пока проект находится в разработке."
    )
