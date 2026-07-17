from __future__ import annotations

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from app.bot.callbacks.product import (
    CompareCallback,
    FavoriteCallback,
    HistoryCallback,
    NavigationCallback,
    ProductCallback,
    SubscribeCallback,
)


def product_keyboard(
    product_id: int,
    url: str,
    *,
    show_details: bool = True,
    show_history: bool = True,
    show_subscribe: bool = True,
    show_favorite: bool = False,
    show_compare: bool = False,
    show_site: bool = True,
    show_back: bool = True,
) -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура карточки товара.

    Используется:
    • поиск
    • история
    • избранное
    • подписки
    • сравнение
    """

    keyboard: list[list[InlineKeyboardButton]] = []

    #
    # Подробнее
    #

    if show_details:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="📄 Подробнее",
                    callback_data=ProductCallback(
                        product_id=product_id,
                    ).pack(),
                )
            ]
        )

    #
    # История / Подписка
    #

    row: list[InlineKeyboardButton] = []

    if show_history:

        row.append(
            InlineKeyboardButton(
                text="📈 История",
                callback_data=HistoryCallback(
                    product_id=product_id,
                ).pack(),
            )
        )

    if show_subscribe:

        row.append(
            InlineKeyboardButton(
                text="🔔 Следить",
                callback_data=SubscribeCallback(
                    product_id=product_id,
                ).pack(),
            )
        )

    if row:
        keyboard.append(row)

    #
    # Избранное / Сравнение
    #

    row = []

    if show_favorite:

        row.append(
            InlineKeyboardButton(
                text="❤️ Избранное",
                callback_data=FavoriteCallback(
                    product_id=product_id,
                ).pack(),
            )
        )

    if show_compare:

        row.append(
            InlineKeyboardButton(
                text="⚖️ Сравнить",
                callback_data=CompareCallback(
                    product_id=product_id,
                ).pack(),
            )
        )

    if row:
        keyboard.append(row)

    #
    # Открыть сайт
    #

    if show_site:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="🌐 Открыть сайт",
                    url=url,
                )
            ]
        )

    #
    # Назад
    #

    if show_back:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data=NavigationCallback(
                        page="search",
                        product_id=product_id,
                    ).pack(),
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )