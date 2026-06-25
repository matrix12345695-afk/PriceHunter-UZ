from bs4 import BeautifulSoup

from app.domain.product_dto import ProductDTO
from app.extractors.base import BaseExtractor


class OlchaExtractor(BaseExtractor):

    def extract_search(
        self,
        soup: BeautifulSoup,
    ) -> list[ProductDTO]:

        raise NotImplementedError()

    def extract_product(
        self,
        soup: BeautifulSoup,
    ) -> ProductDTO:

        raise NotImplementedError()
