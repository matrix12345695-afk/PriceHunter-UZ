from bs4 import BeautifulSoup

from app.extractors.olcha import OlchaExtractor
from app.parsers.base_http import BaseHttpParser


class OlchaHttpParser(BaseHttpParser):

    BASE_URL = "https://olcha.uz"

    def __init__(self):
        super().__init__()
        self.extractor = OlchaExtractor()

    async def search(self, query: str):

        url = f"{self.BASE_URL}/ru/search?search={query}"

        response = await self.client.get(url)

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "lxml",
        )

        return self.extractor.extract_search(soup)
