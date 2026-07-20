from __future__ import annotations

from typing import Any

from app.core.http import http
from app.providers.base import BaseProvider


class UzumProvider(BaseProvider):

    name = "Uzum"

    GRAPHQL_URL = "https://graphql.uzum.uz/"

    async def search_raw(
        self,
        query: str,
    ) -> dict[str, Any]:

        payload = {
            "operationName": "MakeSearch_ItemsAndFilters",
            "variables": {
                "queryInput": {
                    "text": query,
                    "showAdultContent": "NONE",
                    "filters": [],
                    "sort": "BY_RELEVANCE_DESC",
                    "pagination": {
                        "offset": 0,
                        "limit": 48,
                    },
                    "correctQuery": True,
                    "getFastCategories": True,
                    "fastCategoriesLimit": 11,
                    "fastCategoriesLevelOffset": 2,
                    "getPromotionItems": True,
                    "getFastFacets": False,
                    "fastFacetsLimit": 0,
                }
            },
            "query": """
query MakeSearch_ItemsAndFilters(
  $queryInput: MakeSearchQueryInput!
) {
  makeSearch(query: $queryInput) {
    queryText
    total
    catalogCards {
      id
      title
      product {
        id
      }
    }
  }
}
""",
        }

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
    ):
        return []

    async def get_product(
        self,
        external_id: str,
    ):
        return None

    async def healthcheck(self) -> bool:
        try:
            await self.search_raw("iphone")
            return True
        except Exception:
            return False
