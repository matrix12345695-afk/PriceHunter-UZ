from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class ProductDTO:
    """
    Унифицированная модель товара.

    Любой магазин обязан вернуть именно этот объект.
    """

    shop: str

    external_id: str

    name: str

    brand: str | None

    model: str | None

    price: Decimal

    old_price: Decimal | None

    monthly_price: Decimal | None

    currency: str

    url: str

    image: str | None

    available: bool
