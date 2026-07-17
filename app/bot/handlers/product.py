from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery
from loguru import logger

from app.bot.callbacks.product import ProductCallback
from app.bot.keyboards.product import product_keyboard
from app.bot.states.search import SearchState
from app.bot.utils.product_formatter import format_product

from app.database.session import AsyncSessionLocal
from app.services.search_service import SearchService

router = Router(
    name="product",
)


@router.callback_query(ProductCallback.filter())
async def product_info(
    callback: CallbackQuery,
    callback_data: ProductCallback,
) -> None:
    """
    Открытие карточки товара.
    """

    await callback.answer()

    logger.info(
        f"Открытие товара #{callback_data.product_id}"
    )

    try:

        async with AsyncSessionLocal() as session:

            service = SearchService(session)

            product = await service.get_product(
                callback_data.product_id
            )

    except Exception as exc:

        logger.exception(exc)

        await callback.message.edit_text(
            "❌ Не удалось получить информацию о товаре."
        )

        return

    if product is None:

        await callback.message.edit_text(
            "❌ Товар не найден."
        )

        return

    #
    # Если позже понадобится хранить состояние,
    # FSM уже готова к этому.
    #

    if callback.message is None:
        return

    await callback.message.edit_text(
        text=format_product(product),
        reply_markup=product_keyboard(
            product_id=product.id,
            url=product.url,
        ),
    )