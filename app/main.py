import asyncio

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.core.logger import get_logger

logger = get_logger()


async def main():
    logger.info("Starting PriceHunter UZ...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
