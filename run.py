import asyncio

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.database.init_db import init_database
from loguru import logger


async def main():
    logger.info("Starting PriceHunter UZ...")

    await init_database()

    logger.success("Database initialized")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())