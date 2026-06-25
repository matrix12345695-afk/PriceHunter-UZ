from aiogram import Dispatcher

from app.bot.handlers.start import router as start_router


dp = Dispatcher()

dp.include_router(start_router)
