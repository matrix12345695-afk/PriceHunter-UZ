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
        Возвращает последнюю известную цену товара.
        """

        if not self.prices:
            return None

        return max(
            self.prices,
            key=lambda p: p.created_at,
        )

    @property
    def current_price(self) -> int | None:
        """
        Возвращает значение последней цены.
        """

        latest = self.latest_price

        if latest is None:
            return None

        return latest.price

    @property
    def currency(self) -> str | None:
        """
        Валюта последней цены.
        """

        latest = self.latest_price

        if latest is None:
            return None

        return latest.currency

    def __repr__(self) -> str:
        return (
            f"<Product("
            f"id={self.id}, "
            f"title='{self.title}'"
            f")>"
        )