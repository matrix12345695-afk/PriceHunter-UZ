from app.domain.product_dto import ProductDTO
from app.parsers.base import BaseParser


class OlchaParser(BaseParser):

    async def search(
        self,
        query: str,
    ) -> list[ProductDTO]:

        raise NotImplementedError

    async def get_product(
        self,
        external_id: str,
    ) -> ProductDTO:

        raise NotImplementedError
