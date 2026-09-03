from dataclasses import dataclass, field, asdict
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
import re
import time


def amount(value):
    if value is None or isinstance(value, bool):
        return None
    text = re.sub(r'[\s\u00a0\u202f]', '', str(value)).replace(',', '.')
    try:
        n = Decimal(text)
        return int(n) if n.is_finite() and 0 < n < 10**12 and n == n.to_integral_value() else None
    except (InvalidOperation, ValueError):
        return None


def safe_url(url, host):
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and not p.username and (p.hostname == host or p.hostname == 'www.' + host)
    except (ValueError, TypeError):
        return False


@dataclass(frozen=True)
class Product:
    store: str
    title: str
    url: str
    price: int | None
    currency: str = 'UZS'
    checked_at: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)


@dataclass
class Result:
    store: str
    status: str
    products: list[Product] = field(default_factory=list)
    detail: str = ''
