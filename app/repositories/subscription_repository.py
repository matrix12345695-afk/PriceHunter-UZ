from sqlalchemy import select
from sqlalchemy import update

from app.models.subscription import Subscription
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository):

    async def create(
        self,
        telegram_id: int,
        product_id: int,
        target_price: int,
    ) -> Subscription:

        subscription = Subscription(
            telegram_id=telegram_id,
            product_id=product_id,
            target_price=target_price,
        )

        await self.add(subscription)

        return subscription

    async def get_by_id(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        result = await self.session.execute(
            select(Subscription).where(
                Subscription.id == subscription_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        telegram_id: int,
    ) -> list[Subscription]:

        result = await self.session.execute(
            select(Subscription)
            .where(
                Subscription.telegram_id == telegram_id,
                Subscription.is_active.is_(True),
            )
            .order_by(
                Subscription.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_all_active(
        self,
    ) -> list[Subscription]:

        result = await self.session.execute(
            select(Subscription)
            .where(
                Subscription.is_active.is_(True)
            )
        )

        return list(result.scalars().all())

    async def get_by_product(
        self,
        product_id: int,
    ) -> list[Subscription]:

        result = await self.session.execute(
            select(Subscription)
            .where(
                Subscription.product_id == product_id,
                Subscription.is_active.is_(True),
            )
        )

        return list(result.scalars().all())

    async def exists(
        self,
        telegram_id: int,
        product_id: int,
    ) -> bool:

        result = await self.session.execute(
            select(Subscription.id).where(
                Subscription.telegram_id == telegram_id,
                Subscription.product_id == product_id,
                Subscription.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none() is not None

    async def disable(
        self,
        subscription_id: int,
    ) -> None:

        await self.session.execute(
            update(Subscription)
            .where(
                Subscription.id == subscription_id
            )
            .values(
                is_active=False
            )
        )

    async def delete(
        self,
        subscription_id: int,
    ) -> None:

        subscription = await self.get_by_id(
            subscription_id
        )

        if subscription:

            await self.session.delete(subscription)