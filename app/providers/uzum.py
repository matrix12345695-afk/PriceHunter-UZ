from __future__ import annotations

from typing import Any

from app.core.http import http
from app.domain.product_dto import ProductDTO
from app.providers.base import BaseProvider
from app.providers.graphql.make_search_items import build_payload


class UzumProvider(BaseProvider):

    name = "Uzum"

    GRAPHQL_URL = "https://graphql.uzum.uz/"

    async def _request(
        self,
        query: str,
    ) -> dict[str, Any]:

        payload = build_payload(query)

        response = await http.post(
            self.GRAPHQL_URL,
            json=payload,
        )

        response.raise_for_status()

        return response.json()

    async def search(
        self,
        query: str,
        page: int = 1,
    ) -> list[ProductDTO]:

        #
        # TODO:
        # Здесь будет преобразование GraphQL
        # -> ProductDTO
        #

        _ = page

        data = await self._request(query)

        products: list[ProductDTO] = []

        return products

    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO | None:

        #
        # TODO
        #

        return None

    async def healthcheck(
        self,
    ) -> bool:

        try:

            result = await self.search(
                "iphone"
            )

            return len(result) >= 0

        except Exception:

            return False
