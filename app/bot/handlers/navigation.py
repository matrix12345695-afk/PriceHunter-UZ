from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery
from loguru import logger

from app.bot.callbacks.product import NavigationCallback
from app.bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="navigation")


@router.callback_query(NavigationCallback.filter())
async def navigation_handler(
    callback: CallbackQuery,
    callback_data: NavigationCallback,
) -> None:
    """
    Универсальная навигация.
    """

    await callback.answer()

    logger.info(f"Navigation -> {callback_data.page}")

    if callback.message is None:
        return

    #
    # Главный экран поиска
    #
    if callback_data.page == "search":

        # Удаляем старое сообщение с Inline-кнопками
        try:
            await callback.message.delete()
        except Exception:
            pass

        # Отправляем новое сообщение с ReplyKeyboard
        await callback.message.answer(
            text=(
                "🔍 <b>Поиск завершён</b>\n\n"
                "Выберите действие из меню ниже."
            ),
            reply_markup=main_menu_keyboard(),
        )

        return

    #
    # Профиль
    #
    if callback_data.page == "profile":

        await callback.message.edit_text(
            "👤 Раздел находится в разработке."
        )

        return

    #
    # Подписки
    #
    if callback_data.page == "subscriptions":

        await callback.message.edit_text(
            "🔔 Раздел находится в разработке."
        )

        return

    #
    # История цен
    #
    if callback_data.page == "history":

        await callback.message.edit_text(
            "📈 История цен находится в разработке."
        )

        return

    #
    # Настройки
    #
    if callback_data.page == "settings":

        await callback.message.edit_text(
            "⚙ Настройки находятся в разработке."
        )

        return

    #
    # Неизвестный раздел
    #
    await callback.message.edit_text(
        "❌ Неизвестный раздел."
    )