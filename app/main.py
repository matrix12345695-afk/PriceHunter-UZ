import asyncio

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.core.logger import get_logger
from app.database.init_db import init_database

logger = get_logger()


async def main():
    logger.info("Starting PriceHunter UZ...")

    await init_database()

    logger.success("Bot started.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
