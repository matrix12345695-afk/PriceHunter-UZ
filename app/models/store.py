from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class Store(Base):

    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
    )
