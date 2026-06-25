from app.core.logger import get_logger
from app.database.base import Base
from app.database.session import engine

# Импортируем все модели
from app.database.models import *  # noqa

logger = get_logger()


async def init_database():
    logger.info("Initializing database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.success("Database initialized.")
