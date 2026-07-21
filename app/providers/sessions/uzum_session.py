from __future__ import annotations

import json
from pathlib import Path

from app.core.http import http


class UzumSession:
    def __init__(self) -> None:
        self._headers: dict[str, str] | None = None

    def _load_headers(self) -> dict[str, str]:
        if self._headers is not None:
            return self._headers

        root = Path(__file__).resolve().parents[3]

        cookies_file = (
            root
            / "research"
            / "auth"
            / "cookies"
            / "cookies.json"
        )

        with cookies_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            cookies = json.load(f)

        cookie = "; ".join(
            f"{item['name']}={item['value']}"
            for item in cookies
        )

        self._headers = {
            "Accept": "*/*",
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

    async def headers(self) -> dict[str, str]:
        return self._load_headers()
