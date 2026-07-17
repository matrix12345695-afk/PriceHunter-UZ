from sqlalchemy import desc
from sqlalchemy import select

from app.models.price import Price
from app.repositories.base import BaseRepository


class PriceRepository(BaseRepository):

    async def get_last_price(
        self,
        product_id: int,
    ) -> Price | None:

        result = await self.session.execute(
            select(Price)
            .where(
                Price.product_id == product_id
            )
            .order_by(
                desc(Price.created_at)
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_history(
        self,
        product_id: int,
    ) -> list[Price]:

        result = await self.session.execute(
            select(Price)
            .where(
                Price.product_id == product_id
            )
            .order_by(
                Price.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def get_first_price(
        self,
        product_id: int,
    ) -> Price | None:

        result = await self.session.execute(
            select(Price)
            .where(
                Price.product_id == product_id
            )
            .order_by(
                Price.created_at.asc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_min_price(
        self,
        product_id: int,
    ) -> Price | None:

        history = await self.get_history(product_id)

        if not history:
            return None

        return min(
            history,
            key=lambda item: item.price,
        )

    async def get_max_price(
        self,
        product_id: int,
    ) -> Price | None:

        history = await self.get_history(product_id)

        if not history:
            return None

        return max(
            history,
            key=lambda item: item.price,
        )

    async def create(
        self,
        product_id: int,
        price: int,
        currency: str,
    ) -> Price:

        item = Price(
            product_id=product_id,
            price=price,
            currency=currency,
        )

        await self.add(item)

        return item