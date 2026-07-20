from __future__ import annotations

from app.domain.product_dto import ProductDTO
from app.providers.base import BaseProvider


class UzumProvider(BaseProvider):

    name = "Uzum"

    async def search(
        self,
        query: str,
        page: int = 1,
    ) -> list[ProductDTO]:

        #
        # Реализуем позже
        #

        return []

    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO | None:

        return None

    async def healthcheck(
        self,
    ) -> bool:

        try:

            result = await self.search("iphone")

            return len(result) > 0

        except Exception:

            return False
