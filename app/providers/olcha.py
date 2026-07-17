from __future__ import annotations

from app.core.http import http
from app.domain.product_dto import ProductDTO
from app.providers.base import BaseProvider


class OlchaProvider(BaseProvider):

    name = "Olcha"

    BASE_URL = "https://mobile.olcha.uz/api/v2"

    HEADERS = {
        "Referer": "https://olcha.uz/",
        "Origin": "https://olcha.uz",
    }

    async def search(
        self,
        query: str,
        page: int = 1,
    ) -> list[ProductDTO]:

        url = (
            f"{self.BASE_URL}"
            f"/multi-search/products/{query}"
            f"?category_id=&page={page}"
        )

        response = await http.get(
            url,
            headers=self.HEADERS,
        )

        data = response.json()

        products: list[ProductDTO] = []

        for group in data.get("results", {}).get("item_groups", []):

            for item in group.get("items", []):

                products.append(
                    ProductDTO(
                        external_id=str(item["id"]),
                        title=item["name"],
                        price=int(
                            item.get("discount_price")
                            or item.get("price")
                            or 0
                        ),
                        currency=item.get(
                            "currency",
                            "UZS",
                        ),
                        image=item.get(
                            "main_image",
                            "",
                        ),
                        url=(
                            "https://olcha.uz/ru/product/view/"
                            f"{item['alias']}"
                        ),
                        store=self.name,
                    )
                )

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

            return len(result) > 0

        except Exception:

            return False