from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.bot.bot import bot
from app.core.logger import logger
from app.database.init_db import init_database
from app.web.startup import setup_webhook
from app.web.webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting PriceHunter UZ...")

    # Инициализация базы данных
    await init_database()
    logger.success("✅ Database initialized")

    # Регистрация webhook
    await setup_webhook()
    logger.success("✅ Webhook initialized")

    yield

    logger.info("🛑 Shutting down...")

    # ==========================================
    # ВРЕМЕННО НЕ УДАЛЯЕМ WEBHOOK
    # ==========================================
    # await remove_webhook()

    # Закрываем HTTP-сессию бота
    await bot.session.close()

    logger.success("✅ Shutdown complete")


app = FastAPI(
    title="PriceHunter UZ",
    version="1.0.0",
    lifespan=lifespan,
)

# Webhook
app.include_router(webhook_router)


@app.get("/")
async def root():
    return JSONResponse(
        {
            "status": "ok",
            "service": "PriceHunter UZ",
            "mode": "webhook",
            "version": "1.0.0",
        }
    )


@app.get("/health")
async def health():
    return JSONResponse(
        {
            "status": "healthy",
            "database": "connected",
            "telegram": "webhook",
        }
    )
