from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"),
    )

    external_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
    )

    image: Mapped[str]

    url: Mapped[str]

    #
    # Relationships
    #

    store: Mapped["Store"] = relationship(
        back_populates="products",
    )

    prices: Mapped[list["Price"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="Price.created_at",
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    #
    # Helpers
    #

    @property
    def latest_price(self):
        """
        Последняя цена товара.
        """

        if not self.prices:
            return None

        return self.prices[-1]

    @property
    def previous_price(self):
        """
        Предыдущая цена товара.
        """

        if len(self.prices) < 2:
            return None

        return self.prices[-2]

    @property
    def current_price(self) -> int | None:
        """
        Текущая цена.
        """

        latest = self.latest_price

        if latest is None:
            return None

        return latest.price

    @property
    def currency(self) -> str | None:
        """
        Валюта текущей цены.
        """

        latest = self.latest_price

        if latest is None:
            return None

        return latest.currency

    @property
    def discount_amount(self) -> int:
        """
        Размер скидки.
        """

        previous = self.previous_price
        latest = self.latest_price

        if previous is None or latest is None:
            return 0

        if previous.price <= latest.price:
            return 0

        return previous.price - latest.price

    @property
    def discount_percent(self) -> int:
        """
        Процент скидки.
        """

        previous = self.previous_price

        if previous is None:
            return 0

        if previous.price <= 0:
            return 0

        return round(
            self.discount_amount * 100 / previous.price
        )

    @property
    def has_discount(self) -> bool:
        """
        Есть ли скидка.
        """

        return self.discount_amount > 0

    def __repr__(self) -> str:
        return (
            f"<Product("
            f"id={self.id}, "
            f"title='{self.title}'"
            f")>"
        )
