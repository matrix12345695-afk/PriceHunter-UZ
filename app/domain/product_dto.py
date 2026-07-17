from dataclasses import dataclass


@dataclass(slots=True)
class ProductDTO:

    external_id: str

    title: str

    price: int

    currency: str

    image: str

    url: str

    store: str