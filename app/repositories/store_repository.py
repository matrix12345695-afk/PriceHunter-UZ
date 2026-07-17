from sqlalchemy import select

from app.models.store import Store
from app.repositories.base import BaseRepository


class StoreRepository(BaseRepository):

    async def get_by_name(self, name: str):

        result = await self.session.execute(
            select(Store).where(
                Store.name == name
            )
        )

        return result.scalar_one_or_none()

    async def create(self, name: str):

        store = Store(
            name=name
        )

        await self.add(store)

        return store