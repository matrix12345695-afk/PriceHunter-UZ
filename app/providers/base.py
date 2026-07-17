from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.domain.product_dto import ProductDTO


class BaseProvider(ABC):
    """
    Базовый интерфейс всех магазинов.
    """

    name: str

    @abstractmethod
    async def search(
        self,
        query: str,
    ) -> list[ProductDTO]:
        """
        Поиск товаров.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO | None:
        """
        Получить товар по внешнему ID.
        """
        raise NotImplementedError

    @abstractmethod
    async def healthcheck(
        self,
    ) -> bool:
        """
        Проверка доступности магазина.
        """
        raise NotImplementedError