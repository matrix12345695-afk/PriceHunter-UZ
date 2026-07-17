from app.parsers.providers.olcha_http import (
    OlchaHttpParser,
)
from app.parsers.providers.olcha_browser import (
    OlchaBrowserParser,
)


class ParserManager:

    def __init__(self):

        self.http = {
            "olcha": OlchaHttpParser(),
        }

        self.browser = {
            "olcha": OlchaBrowserParser(),
        }

    async def search(
        self,
        shop: str,
        query: str,
    ):
        try:
            return await self.http[shop].search(query)

        except Exception:

            return await self.browser[shop].search(query)
