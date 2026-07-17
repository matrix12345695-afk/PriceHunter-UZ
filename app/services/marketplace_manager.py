from __future__ import annotations

import asyncio

from app.domain.product_dto import ProductDTO
from app.providers.base import BaseProvider
from app.providers.olcha import OlchaProvider


class MarketplaceManager:
    """
    Управляет всеми подключёнными магазинами.
    """

    def __init__(self):

        self.providers: list[BaseProvider] = [
            OlchaProvider(),
        ]

    def register(
        self,
        provider: BaseProvider,
    ) -> None:
        """
        Регистрация нового магазина.
        """

        self.providers.append(provider)

    async def search(
        self,
        query: str,
    ) -> list[ProductDTO]:
        """
        Поиск одновременно во всех магазинах.
        """

        tasks = [
            provider.search(query)
            for provider in self.providers
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        products: list[ProductDTO] = []

        for result in results:

            if isinstance(result, Exception):
                continue

            products.extend(result)

        return products

    async def healthcheck(self) -> dict[str, bool]:
        """
        Проверка всех магазинов.
        """

        result: dict[str, bool] = {}

        for provider in self.providers:

            try:

                result[provider.name] = await provider.healthcheck()

            except Exception:

                result[provider.name] = False

        return result