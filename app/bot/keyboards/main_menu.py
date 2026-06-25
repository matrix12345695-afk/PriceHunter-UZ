from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔍 Поиск товара"),
        ],
        [
            KeyboardButton(text="❤️ Избранное"),
            KeyboardButton(text="🔥 Скидки"),
        ],
        [
            KeyboardButton(text="📈 История цен"),
            KeyboardButton(text="👤 Профиль"),
        ],
        [
            KeyboardButton(text="⚙ Настройки"),
        ],
    ],
    resize_keyboard=True,
)
