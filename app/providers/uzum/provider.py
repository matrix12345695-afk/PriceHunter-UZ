from __future__ import annotations

from pathlib import Path
from typing import Any

from app.providers.graphql_client import GraphQLClient


class UzumProvider:
    """
    Uzum GraphQL Provider.

    Работает с настоящими GraphQL-документами,
    сохранёнными Toolkit.
    """

    ENDPOINT = "https://graphql.uzum.uz/"

    def __init__(
        self,
        graphql_dir: str | Path | None = None,
    ) -> None:

        self.client = GraphQLClient(
            self.ENDPOINT,
        )

        if graphql_dir is None:

            graphql_dir = (
                Path(__file__).resolve().parents[2]
                / "graphql"
                / "uzum"
            )

        self.graphql_dir = Path(graphql_dir)

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _load_query(
        self,
        filename: str,
    ) -> str:

        path = self.graphql_dir / filename

        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text(
            encoding="utf-8",
        )

    # ==========================================================
    # SEARCH
    # ==========================================================

    async def search(
        self,
        text: str,
        *,
        offset: int = 0,
        limit: int = 48,
    ) -> dict[str, Any]:

        query = self._load_query(
            "MakeSearch_ItemsAndFilters.graphql",
        )

        variables = {
            "queryInput": {
                "text": text,
                "showAdultContent": "NONE",
                "filters": [],
                "sort": "BY_RELEVANCE_DESC",
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                },
                "correctQuery": False,
                "getFastCategories": True,
                "fastCategoriesLimit": 11,
                "fastCategoriesLevelOffset": 2,
                "getPromotionItems": True,
                "getFastFacets": False,
                "fastFacetsLimit": 0,
            }
        }

        return await self.client.execute(
            operation_name="MakeSearch_ItemsAndFilters",
            query=query,
            variables=variables,
        )

    # ==========================================================
    # PRODUCT
    # ==========================================================

    async def product(
        self,
        product_id: int,
    ) -> dict[str, Any]:

        query = self._load_query(
            "ProductPage.graphql",
        )

        return await self.client.execute(
            operation_name="ProductPage",
            query=query,
            variables={
                "productId": product_id,
            },
        )

    # ==========================================================
    # REVIEWS
    # ==========================================================

    async def reviews(
        self,
        product_id: int,
        *,
        page: int = 0,
        size: int = 20,
    ) -> dict[str, Any]:

        query = self._load_query(
            "Feedbacks.graphql",
        )

        return await self.client.execute(
            operation_name="Feedbacks",
            query=query,
            variables={
                "productPageId": product_id,
                "page": page,
                "size": size,
                "sort": "RELEVANCE",
                "filters": [],
                "trans": "PRODUCT_720",
            },
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    async def recommendations(
        self,
        product_id: int,
    ) -> dict[str, Any]:

        query = self._load_query(
            "RecommendationBlocks.graphql",
        )

        return await self.client.execute(
            operation_name="RecommendationBlocks",
            query=query,
            variables={
                "query": {
                    "itemIds": [
                        product_id,
                    ],
                    "key": "PDP",
                }
            },
        )

    # ==========================================================
    # CLOSE
    # ==========================================================

    async def close(
        self,
    ) -> None:

        await self.client.close()