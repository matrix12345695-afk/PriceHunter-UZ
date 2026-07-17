from __future__ import annotations

from pathlib import Path


GRAPHQL_DIR = (
    Path(__file__).resolve().parents[2]
    / "graphql"
    / "uzum"
)


def load_query(filename: str) -> str:
    """
    Загружает GraphQL-запрос с диска.
    """

    path = GRAPHQL_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"GraphQL file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8",
    )


SEARCH_QUERY = load_query(
    "MakeSearch_ItemsAndFilters.graphql"
)

PRODUCT_QUERY = load_query(
    "ProductPage.graphql"
)

FEEDBACKS_QUERY = load_query(
    "Feedbacks.graphql"
)

RECOMMENDATIONS_QUERY = load_query(
    "RecommendationBlocks.graphql"
)