from app.parsers.providers.olcha import OlchaParser


class ParserService:

    def __init__(self):

        self.parsers = {
            "olcha": OlchaParser(),
        }

    async def search(self, query: str):

        results = []

        for parser in self.parsers.values():

            try:
                items = await parser.search(query)
                results.extend(items)

            except Exception:
                pass

        return results
