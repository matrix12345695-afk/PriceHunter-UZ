from __future__ import annotations

import httpx


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "ru,en;q=0.9",
}


class HttpClient:
    """
    Общий HTTP-клиент для всех маркетплейсов.
    Один AsyncClient используется во всём приложении.
    """

    def __init__(self) -> None:

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
            # HTTP/2 временно отключаем.
            # Для работы с Olcha и Uzum он не требуется.
            http2=False,
        )

    async def get(self, url: str, **kwargs):
        response = await self._client.get(url, **kwargs)
        response.raise_for_status()
        return response

    async def post(self, url: str, **kwargs):
        response = await self._client.post(url, **kwargs)
        response.raise_for_status()
        return response

    async def close(self):
        await self._client.aclose()


http = HttpClient()
