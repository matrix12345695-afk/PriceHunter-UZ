from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    price_id: Mapped[int] = mapped_column(
        ForeignKey("prices.id", ondelete="CASCADE"),
        index=True,
    )

    value: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
