from __future__ import annotations

from typing import Any

from app.core.http import http
from app.domain.product_dto import ProductDTO
from app.providers.base import BaseProvider
from app.providers.graphql.make_search_items import build_payload
from app.providers.sessions.uzum_session import UzumSession


class UzumProvider(BaseProvider):

    name = "Uzum"

    GRAPHQL_URL = "https://graphql.uzum.uz/"

    def __init__(self) -> None:
        self.session = UzumSession()

    async def _request(
        self,
        query: str,
    ) -> dict[str, Any]:

        payload = build_payload(query)

        headers = await self.session.headers()

        response = await http.post(
            self.GRAPHQL_URL,
            json=payload,
            headers=headers,
        )

        return response.json()

    async def search(
        self,
        query: str,
        page: int = 1,
    ) -> list[ProductDTO]:

        _ = page

        data = await self._request(query)

        print(data)

        products: list[ProductDTO] = []

        return products

    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO | None:

        _ = external_id

        return None

    async def healthcheck(
        self,
    ) -> bool:

        try:
            await self.search("iphone")
            return True
        except Exception:
            return False
