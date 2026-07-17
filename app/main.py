import asyncio

import typer
from loguru import logger

from app.database.database import AsyncSessionLocal
from app.providers.olcha import OlchaProvider
from app.services.sync_service import SyncService

app = typer.Typer(
    help="PriceHunter UZ CLI",
    no_args_is_help=True,
)


@app.command()
def search(query: str):
    """
    Поиск товаров на Olcha.
    """

    async def _run():

        provider = OlchaProvider()

        products = await provider.search(query)

        logger.success(f"Найдено {len(products)} товаров\n")

        for index, product in enumerate(products, start=1):

            logger.info(f"[{index}] {product.title}")
            logger.info(f"💰 {product.price:,} {product.currency}")
            logger.info(f"🔗 {product.url}")

            print("-" * 70)

    asyncio.run(_run())


@app.command()
def sync(query: str):
    """
    Сохранение товаров в PostgreSQL.
    """

    async def _run():

        async with AsyncSessionLocal() as session:

            service = SyncService(session)

            result = await service.sync(query)

            logger.success(
                f"""

================ PriceHunter UZ =================

Получено товаров : {result.total}

Создано товаров : {result.created_products}

Добавлено цен : {result.created_prices}

Без изменений : {result.skipped}

=================================================

"""
            )

    asyncio.run(_run())


@app.command()
def health():
    """
    Проверка подключения к Olcha.
    """

    async def _run():

        async with AsyncSessionLocal() as session:

            service = SyncService(session)

            ok = await service.healthcheck()

            if ok:

                logger.success("Service is healthy")

            else:

                logger.error("Service is unavailable")

    asyncio.run(_run())


@app.command()
def version():
    """
    Версия проекта.
    """

    logger.info("PriceHunter UZ PRO")
    logger.info("Version 0.2.0")


if __name__ == "__main__":
    app()