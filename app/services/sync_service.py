from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.product_dto import ProductDTO
from app.models.price import Price
from app.models.product import Product
from app.models.store import Store

from app.providers.olcha import OlchaProvider

from app.repositories.price_repository import PriceRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.store_repository import StoreRepository


STORE_NAME = "Olcha"


@dataclass(slots=True)
class SyncResult:
    total: int = 0
    created_products: int = 0
    created_prices: int = 0
    skipped: int = 0


class SyncService:

    def __init__(
        self,
        session: AsyncSession,
        provider: OlchaProvider | None = None,
    ):

        self.session = session

        self.provider = provider or OlchaProvider()

        self.store_repo = StoreRepository(session)
        self.product_repo = ProductRepository(session)
        self.price_repo = PriceRepository(session)

    async def sync(
        self,
        query: str,
    ) -> SyncResult:

        logger.info(f"Начинаем синхронизацию: {query}")

        try:

            products = await self.provider.search(query)

            return await self.sync_products(
                STORE_NAME,
                products,
            )

        except Exception:

            await self.session.rollback()

            logger.exception("Ошибка синхронизации")

            raise

# ==========================================================
# НОВЫЙ МЕТОД
# ==========================================================

    async def sync_products(
        self,
        store_name: str,
        products: list[ProductDTO],
    ) -> SyncResult:

        logger.info(
            f"Сохраняем {len(products)} товаров магазина '{store_name}'"
        )

        result = SyncResult()
        result.total = len(products)

        try:

            store = await self._get_store(store_name)

            for dto in products:

                await self._process_product(
                    store,
                    dto,
                    result,
                )

            await self.session.commit()

            logger.success(
                f"""
=========================================
SYNC FINISHED

Магазин : {store_name}

Всего товаров : {result.total}

Создано товаров : {result.created_products}

Создано цен : {result.created_prices}

Без изменений : {result.skipped}
=========================================
"""
            )

            return result

        except Exception:

            await self.session.rollback()

            logger.exception("Ошибка sync_products")

            raise
      
    async def _get_store(
        self,
        name: str,
    ) -> Store:

        store = await self.store_repo.get_by_name(name)

        if store:

            return store

        logger.info(f"Создаём магазин {name}")

        store = await self.store_repo.create(name)

        await self.session.flush()

        return store

    async def _process_product(
        self,
        store: Store,
        dto: ProductDTO,
        result: SyncResult,
    ):

        product = await self.product_repo.get_by_external_id(
            dto.external_id
        )

        if product is None:

            product = await self._create_product(
                store,
                dto,
            )

            result.created_products += 1

            await self._create_price(
                product,
                dto,
            )

            result.created_prices += 1

            logger.success(f"Создан товар: {dto.title}")

            return

        last_price = await self.price_repo.get_last_price(
            product.id
        )

        if last_price is None:

            await self._create_price(
                product,
                dto,
            )

            result.created_prices += 1

            return

        if last_price.price != dto.price:

            logger.info(
                f"""
Цена изменилась

{dto.title}

{last_price.price:,}
↓

{dto.price:,}
"""
            )

            await self._create_price(
                product,
                dto,
            )

            result.created_prices += 1

            return

        result.skipped += 1
    async def _create_product(
        self,
        store: Store,
        dto: ProductDTO,
    ) -> Product:

        product = await self.product_repo.create(
            store_id=store.id,
            external_id=dto.external_id,
            title=dto.title,
            image=dto.image,
            url=dto.url,
        )

        await self.session.flush()

        return product

    async def _create_price(
        self,
        product: Product,
        dto: ProductDTO,
    ) -> Price:

        price = await self.price_repo.create(
            product_id=product.id,
            price=dto.price,
            currency=dto.currency,
        )

        await self.session.flush()

        return price

    async def sync_store(
        self,
        store_name: str,
        query: str,
    ) -> SyncResult:

        logger.info(
            f"Синхронизация магазина '{store_name}' по запросу '{query}'"
        )

        store = await self._get_store(store_name)

        products = await self.provider.search(query)

        result = SyncResult()
        result.total = len(products)

        try:

            for dto in products:

                await self._process_product(
                    store,
                    dto,
                    result,
                )

            await self.session.commit()

            return result

        except Exception:

            await self.session.rollback()

            logger.exception("Ошибка sync_store")

            raise

    async def sync_many(
        self,
        queries: list[str],
    ) -> list[SyncResult]:

        results: list[SyncResult] = []

        logger.info(
            f"Запуск пакетной синхронизации ({len(queries)} запросов)"
        )

        for query in queries:

            result = await self.sync(query)

            results.append(result)

        return results

    async def print_summary(
        self,
        result: SyncResult,
    ) -> None:

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

    async def healthcheck(self) -> bool:

        try:

            await self.provider.search("iphone")

            logger.success("Healthcheck OK")

            return True

        except Exception:

            logger.exception("Healthcheck FAILED")

            return False

    async def sync_and_print(
        self,
        query: str,
    ) -> SyncResult:

        result = await self.sync(query)

        await self.print_summary(result)

        return result
