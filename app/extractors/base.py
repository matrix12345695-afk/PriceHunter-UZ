from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from app.domain.product_dto import ProductDTO


class BaseExtractor(ABC):

    @abstractmethod
    def extract_search(
        self,
        soup: BeautifulSoup,
    ) -> list[ProductDTO]:
        """
        Извлечь список товаров.
        """

    @abstractmethod
    def extract_product(
        self,
        soup: BeautifulSoup,
    ) -> ProductDTO:
        """
        Извлечь один товар.
        """
