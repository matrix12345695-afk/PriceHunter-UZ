from app.parsers.base_http import BaseHttpParser


class OlchaHttpParser(BaseHttpParser):

    BASE_URL = "https://olcha.uz"

    async def search(self, query: str):

        raise NotImplementedError(
            "Research in progress."
        )
