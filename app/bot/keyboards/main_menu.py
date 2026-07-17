from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
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


# Для обратной совместимости
main_menu = main_menu_keyboard()