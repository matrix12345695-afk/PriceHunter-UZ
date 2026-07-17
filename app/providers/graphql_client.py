from __future__ import annotations

from typing import Any

import httpx


class GraphQLClient:
    """
    Универсальный GraphQL клиент.

    Используется всеми маркетплейсами,
    где GraphQL является основным API.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        timeout: float = 30.0,
    ) -> None:

        self.endpoint = endpoint

        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36"
                ),
            },
        )

    async def execute(
        self,
        *,
        operation_name: str,
        query: str,
        variables: dict[str, Any],
    ) -> dict[str, Any]:

        payload = {
            "operationName": operation_name,
            "query": query,
            "variables": variables,
        }

        response = await self.client.post(
            self.endpoint,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise RuntimeError(
                data["errors"]
            )

        return data.get(
            "data",
            {},
        )

    async def close(
        self,
    ) -> None:

        await self.client.aclose()