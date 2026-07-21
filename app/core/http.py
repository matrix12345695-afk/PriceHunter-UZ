from __future__ import annotations

import json

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
            http2=False,
        )

    async def get(self, url: str, **kwargs):
        response = await self._client.get(url, **kwargs)

        print("=" * 80)
        print("GET", url)
        print("STATUS:", response.status_code)
        print("=" * 80)

        response.raise_for_status()
        return response

    async def post(self, url: str, **kwargs):

        print("=" * 80)
        print("POST", url)
        print()

        headers = kwargs.get("headers", {})
        body = kwargs.get("json")

        print("HEADERS:")

        for key, value in headers.items():

            if key.lower() == "authorization":
                print(f"{key}: {value[:80]}...")

            elif key.lower() == "cookie":
                print(f"{key}: <hidden>")

            else:
                print(f"{key}: {value}")

        print()

        print("BODY:")
        print(json.dumps(body, indent=2, ensure_ascii=False))

        print("=" * 80)

        response = await self._client.post(url, **kwargs)

        print()
        print("=" * 80)
        print("RESPONSE")
        print("STATUS:", response.status_code)
        print()

        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(response.text)

        print("=" * 80)

        response.raise_for_status()
        return response

    async def close(self):
        await self._client.aclose()


http = HttpClient()
