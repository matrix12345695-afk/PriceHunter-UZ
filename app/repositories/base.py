from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj: Any):

        self.session.add(obj)
        await self.session.flush()

        return obj

    async def commit(self):

        await self.session.commit()

    async def refresh(self, obj):

        await self.session.refresh(obj)

    async def delete(self, obj):

        await self.session.delete(obj)

    async def get_by_id(self, model, object_id):

        result = await self.session.execute(
            select(model).where(model.id == object_id)
        )

        return result.scalar_one_or_none()