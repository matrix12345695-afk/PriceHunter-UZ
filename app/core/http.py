from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote


class UzumSession:
    """
    Управляет HTTP-заголовками и cookies для Uzum.

    Пока используется сохранённая браузерная сессия.
    Позже здесь появится автоматическое обновление токенов.
    """

    def __init__(self) -> None:
        self._headers: dict[str, str] | None = None

    def _cookies_path(self) -> Path:
        return (
            Path(__file__).resolve().parents[3]
            / "research"
            / "auth"
            / "cookies"
            / "cookies.json"
        )

    def _load_cookies(self) -> list[dict]:
        with self._cookies_path().open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    @staticmethod
    def _build_cookie_header(cookies: list[dict]) -> str:
        return "; ".join(
            f"{cookie['name']}={cookie['value']}"
            for cookie in cookies
        )

    @staticmethod
    def _find_cookie(
        cookies: list[dict],
        name: str,
    ) -> str | None:
        for cookie in cookies:
            if cookie["name"] == name:
                return cookie["value"]
        return None

    async def headers(self) -> dict[str, str]:

        if self._headers is None:

            cookies = self._load_cookies()

            cookie_header = self._build_cookie_header(cookies)

            access_token = self._find_cookie(
                cookies,
                "access_token",
            )

            install_id = (
                self._find_cookie(cookies, "clickstream-client.installId")
                or self._find_cookie(cookies, "installId")
            )

            if install_id:
                install_id = unquote(install_id).strip('"')

            headers = {
                "Accept": "*/*",
                "Accept-Language": "ru-RU",
                "Content-Type": "application/json",
                "Origin": "https://uzum.uz",
                "Referer": "https://uzum.uz/",
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36"
                ),
                "Cookie": cookie_header,

                # GraphQL
                "apollographql-client-name": "web-customers",
                "apollographql-client-version": "1.63.2",

                # Геолокация
                "city-id": "1",
                "city-latitude": "41.379112",
                "city-longitude": "69.29944",
                "latitude": "41.379112",
                "longitude": "69.29944",
            }

            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

            if install_id:
                headers["x-iid"] = install_id

            self._headers = headers

        return self._headers
