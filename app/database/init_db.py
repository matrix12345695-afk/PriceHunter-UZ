from app.core.logger import get_logger
from app.database.base import Base
from app.database.session import engine

# Импортируем модели, чтобы SQLAlchemy зарегистрировала их
from app.models.product import Product
from app.models.price import Price
from app.models.store import Store
from app.models.subscription import Subscription

logger = get_logger()


async def init_database():
    logger.info("Initializing database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.success("Database initialized.")