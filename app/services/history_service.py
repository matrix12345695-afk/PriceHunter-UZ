from __future__ import annotations

from statistics import mean

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.price import Price
from app.repositories.price_repository import PriceRepository


class HistoryService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.price_repo = PriceRepository(session)

    async def get_history(
        self,
        product: Product,
    ) -> list[Price]:
        """
        Возвращает всю историю цен товара.
        """

        return await self.price_repo.get_history(product.id)

    async def get_last_price(
        self,
        product: Product,
    ) -> Price | None:
        """
        Последняя цена.
        """

        return await self.price_repo.get_last_price(product.id)

    async def get_min_price(
        self,
        product: Product,
    ) -> Price | None:
        """
        Минимальная цена.
        """

        history = await self.get_history(product)

        if not history:
            return None

        return min(history, key=lambda p: p.price)

    async def get_max_price(
        self,
        product: Product,
    ) -> Price | None:
        """
        Максимальная цена.
        """

        history = await self.get_history(product)

        if not history:
            return None

        return max(history, key=lambda p: p.price)

    async def get_average_price(
        self,
        product: Product,
    ) -> float:
        """
        Средняя цена.
        """

        history = await self.get_history(product)

        if not history:
            return 0

        return mean([price.price for price in history])

    async def get_price_changes(
        self,
        product: Product,
    ) -> int:
        """
        Количество изменений цены.
        """

        history = await self.get_history(product)

        if len(history) <= 1:
            return 0

        return len(history) - 1

    async def get_price_drop(
        self,
        product: Product,
    ) -> int:
        """
        Насколько цена упала относительно максимальной.
        """

        minimum = await self.get_min_price(product)
        maximum = await self.get_max_price(product)

        if not minimum or not maximum:
            return 0

        return maximum.price - minimum.price

    async def get_discount_percent(
        self,
        product: Product,
    ) -> float:
        """
        Процент снижения цены.
        """

        minimum = await self.get_min_price(product)
        maximum = await self.get_max_price(product)

        if not minimum or not maximum:
            return 0

        if maximum.price == 0:
            return 0

        return round(
            (maximum.price - minimum.price)
            / maximum.price
            * 100,
            2,
        )

    async def get_statistics(
        self,
        product: Product,
    ) -> dict:

        history = await self.get_history(product)

        return {
            "records": len(history),
            "current": await self.get_last_price(product),
            "minimum": await self.get_min_price(product),
            "maximum": await self.get_max_price(product),
            "average": await self.get_average_price(product),
            "changes": await self.get_price_changes(product),
            "drop": await self.get_price_drop(product),
            "discount_percent": await self.get_discount_percent(product),
        }