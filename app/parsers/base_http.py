from abc import ABC, abstractmethod

import httpx


class BaseHttpParser(ABC):

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64)"
                )
            },
        )

    @abstractmethod
    async def search(self, query: str):
        pass

    async def close(self):
        await self.client.aclose()
