from abc import ABC, abstractmethod

from app.domain.product_dto import ProductDTO


class BaseParser(ABC):

    @abstractmethod
    async def search(
        self,
        query: str,
    ) -> list[ProductDTO]:
        """
        Поиск товаров.
        """

    @abstractmethod
    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO:
        """
        Получить один товар.
        """
