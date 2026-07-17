from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


async def get_user(
    session: AsyncSession,
    telegram_id: int,
):
    result = await session.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    username: str | None,
):
    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
    )

    session.add(user)

    await session.commit()

    return user
