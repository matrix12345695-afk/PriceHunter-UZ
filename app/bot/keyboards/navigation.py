from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


def back_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data="back",
                )
            ]
        ]
    )