from urllib.parse import urlparse

from .config import (
    ALLOWED_RESOURCE_TYPES,
    IGNORE_DOMAINS,
    INTERESTING_KEYWORDS,
)


def is_interesting_request(request) -> bool:
    """
    Проверяет, стоит ли сохранять запрос.
    """

    if request.resource_type not in ALLOWED_RESOURCE_TYPES:
        return False

    parsed = urlparse(request.url)

    host = parsed.netloc.lower()

    for ignored in IGNORE_DOMAINS:
        if ignored in host:
            return False

    url = request.url.lower()

    if any(word in url for word in INTERESTING_KEYWORDS):
        return True

    return request.resource_type in ("fetch", "xhr")


def get_score(url: str) -> int:
    """
    Присваивает API рейтинг.
    """

    score = 0

    url = url.lower()

    for keyword in INTERESTING_KEYWORDS:
        if keyword in url:
            score += 10

    return score