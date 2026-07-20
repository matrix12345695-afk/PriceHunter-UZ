from __future__ import annotations

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from app.bot.keyboards.product import product_keyboard
from app.bot.states.search import SearchState
from app.bot.utils.product_formatter import format_product
from app.database.session import AsyncSessionLocal
from app.services.search_service import SearchService

router = Router(
    name="search",
)


@router.message(F.text == "🔍 Поиск товара")
async def start_search(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Начало поиска.
    """

    await state.set_state(
        SearchState.waiting_query
    )

    await message.answer(
        "🔍 <b>Введите название товара</b>\n\n"
        "Например:\n"
        "• iPhone 17\n"
        "• PlayStation 5\n"
        "• Samsung S25 Ultra"
    )


@router.message(SearchState.waiting_query)
async def process_search(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Выполняет поиск товаров.
    """

    query = (message.text or "").strip()

    if len(query) < 2:

        await message.answer(
            "❌ Слишком короткий запрос."
        )

        return

    logger.info(
        f"Поиск товара: {query}"
    )

    progress = await message.answer(
        "⏳ Выполняю поиск..."
    )

    try:

        async with AsyncSessionLocal() as session:

            service = SearchService(session)

            products = await service.search(query)

    except Exception as exc:

        logger.exception(exc)

        await progress.edit_text(
            "❌ Произошла ошибка во время поиска."
        )

        return

    await state.set_state(
        SearchState.viewing_results
    )

    if not products:

        await progress.edit_text(
            f"😔 По запросу <b>{query}</b> ничего не найдено."
        )

        return

    await progress.edit_text(
        f"✅ Найдено товаров: <b>{len(products)}</b>"
    )

    #
    # Пока показываем первые 5.
    #

    for product in products[:5]:
        try:
            text = format_product(product)

            keyboard = product_keyboard(
                product.id,
                product.url,
            )

            await message.answer(
                text,
                reply_markup=keyboard,
            )

        except Exception as e:
            logger.exception(e)

            await message.answer(
                f"❌ Ошибка:\n<code>{type(e).__name__}: {e}</code>"
            )

            break
