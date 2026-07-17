from __future__ import annotations

from pathlib import Path


GRAPHQL_DIR = Path(__file__).parent


def load_query(filename: str) -> str:
    """
    Загружает GraphQL-запрос из файла.
    """

    path = GRAPHQL_DIR / filename

    return path.read_text(
        encoding="utf-8",
    )