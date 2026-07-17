from aiogram import Dispatcher

from app.bot.handlers.start import router as start_router
from app.bot.handlers.search import router as search_router
from app.bot.handlers.product import router as product_router
from app.bot.handlers.navigation import router as navigation_router

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(search_router)
dp.include_router(product_router)
dp.include_router(navigation_router)