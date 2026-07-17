from __future__ import annotations

from typing import Any

from ..graphql import GraphQLClient
from .queries import SEARCH_QUERY


class UzumSearch:

    OPERATION_NAME = "MakeSearch_ItemsAndFilters"

    def __init__(
        self,
        client: GraphQLClient,
    ) -> None:

        self.client = client

    async def search(
        self,
        text: str,
        *,
        offset: int = 0,
        limit: int = 48,
    ) -> list[dict[str, Any]]:

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

        data = await self.client.execute(
            operation_name=self.OPERATION_NAME,
            query=SEARCH_QUERY,
            variables=variables,
        )

        search = data.get("makeSearch")

        if not search:
            return []

        items = []

        for row in search.get("items", []):

            card = row.get("catalogCard")

            if not card:
                continue

            price = (
                card.get("buyingOptions", {})
                    .get("priceBlock", {})
                    .get("finalPrice", {})
                    .get("amount")
            )

            image = None

            photos = card.get("photos") or []

            if photos:

                image = (
                    photos[0]
                    .get("link", {})
                    .get("high")
                )

            items.append(
                {
                    "id": card.get("productId"),
                    "title": card.get("title"),
                    "price": price,
                    "rating": card.get("rating"),
                    "reviews": card.get("feedbackQuantity"),
                    "image": image,
                    "url": (
                        f"https://uzum.uz/product/"
                        f"{card.get('productId')}"
                    ),
                }
            )

        return items