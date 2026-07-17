from logging.config import fileConfig

from sqlalchemy.engine import Connection

from alembic import context

from app.core.settings import settings
from app.database.base import Base

# Импорт моделей
from app.models.store import Store
from app.models.product import Product
from app.models.price import Price

from app.models.subscription import Subscription


config = context.config

# Передаем URL из .env
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

print("=" * 80)
print("DATABASE_URL :", settings.DATABASE_URL)
print("ALEMBIC_URL  :", config.get_main_option("sqlalchemy.url"))
print("=" * 80)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


import ssl

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool


async def run_async_migrations():

    ssl_context = ssl.create_default_context()

    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args={
            "ssl": ssl_context,
        },
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()