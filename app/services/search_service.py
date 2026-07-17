from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.marketplace_manager import MarketplaceManager
from app.services.sync_service import SyncService


class SearchService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.manager = MarketplaceManager()

        self.product_repo = ProductRepository(session)

        self.sync_service = SyncService(session)

    async def search(
        self,
        query: str,
    ) -> list[Product]:

        logger.info(f"Поиск: {query}")

        #
        # 1. Ищем в базе
        #

        products = await self.product_repo.search(query)

        if products:

            logger.success(
                f"Найдено {len(products)} товаров в БД"
            )

            return products

        #
        # 2. Если нет — идём в маркетплейсы
        #

        logger.info(
            "В базе ничего нет. Выполняем поиск..."
        )

        provider_products = await self.manager.search(
            query
        )

        if not provider_products:

            logger.warning(
                "Товаров не найдено."
            )

            return []

        #
        # 3. Сохраняем найденное
        #

        await self.sync_service.sync(query)

        #
        # 4. Снова ищем уже в БД
        #

        products = await self.product_repo.search(
            query
        )

        logger.success(
            f"Добавлено {len(products)} товаров."
        )

        return products

    async def search_exact(
        self,
        title: str,
    ) -> Product | None:

        products = await self.product_repo.search(
            title
        )

        for product in products:

            if product.title.lower() == title.lower():

                return product

        return None

    async def get_product(
        self,
        product_id: int,
    ) -> Product | None:

        return await self.product_repo.get_by_id(
            product_id
        )