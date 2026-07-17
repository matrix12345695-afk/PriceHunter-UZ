from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.product_repository import ProductRepository
from app.repositories.subscription_repository import SubscriptionRepository


class SubscriptionService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.product_repo = ProductRepository(session)

        self.subscription_repo = SubscriptionRepository(session)

    async def subscribe(
        self,
        telegram_id: int,
        product_id: int,
        target_price: int,
    ) -> Subscription:

        exists = await self.subscription_repo.exists(
            telegram_id,
            product_id,
        )

        if exists:

            raise ValueError(
                "Вы уже подписаны на этот товар."
            )

        subscription = await self.subscription_repo.create(
            telegram_id=telegram_id,
            product_id=product_id,
            target_price=target_price,
        )

        await self.session.commit()

        logger.success(
            f"Пользователь {telegram_id} подписался на товар {product_id}"
        )

        return subscription

    async def unsubscribe(
        self,
        subscription_id: int,
    ) -> None:

        await self.subscription_repo.disable(
            subscription_id
        )

        await self.session.commit()

        logger.info(
            f"Подписка {subscription_id} отключена"
        )

    async def get_user_subscriptions(
        self,
        telegram_id: int,
    ) -> list[Subscription]:

        return await self.subscription_repo.get_by_user(
            telegram_id
        )

    async def get_product_subscriptions(
        self,
        product_id: int,
    ) -> list[Subscription]:

        return await self.subscription_repo.get_by_product(
            product_id
        )

    async def get_active_subscriptions(
        self,
    ) -> list[Subscription]:

        return await self.subscription_repo.get_all_active()