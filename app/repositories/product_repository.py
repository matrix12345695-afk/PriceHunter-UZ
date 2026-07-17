from sqlalchemy import select

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository):

    async def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:

        result = await self.session.execute(
            select(Product).where(
                Product.id == product_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_external_id(
        self,
        external_id: str,
    ) -> Product | None:

        result = await self.session.execute(
            select(Product).where(
                Product.external_id == external_id
            )
        )

        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
    ) -> list[Product]:

        result = await self.session.execute(
            select(Product)
            .where(
                Product.title.ilike(f"%{query}%")
            )
            .order_by(
                Product.title
            )
        )

        return list(result.scalars().all())

    async def get_all(
        self,
    ) -> list[Product]:

        result = await self.session.execute(
            select(Product)
            .order_by(Product.title)
        )

        return list(result.scalars().all())

    async def create(
        self,
        store_id: int,
        external_id: str,
        title: str,
        image: str,
        url: str,
    ) -> Product:

        product = Product(
            store_id=store_id,
            external_id=external_id,
            title=title,
            image=image,
            url=url,
        )

        await self.add(product)

        return product