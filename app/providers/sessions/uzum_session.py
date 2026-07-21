from __future__ import annotations

import json
from pathlib import Path


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

    def _build_cookie_header(self) -> str:

        with self._cookies_path().open(
            "r",
            encoding="utf-8",
        ) as f:
            cookies = json.load(f)

        return "; ".join(
            f"{cookie['name']}={cookie['value']}"
            for cookie in cookies
        )

    async def headers(self) -> dict[str, str]:

        if self._headers is None:

            cookie = self._build_cookie_header()

            self._headers = {
                "Accept": "*/*",
                "Accept-Language": "ru",
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
                "Cookie": cookie,
            }

        return self._headers
