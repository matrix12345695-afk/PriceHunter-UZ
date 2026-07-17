from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.database.init_db import init_database
from app.core.logger import logger
from app.web.webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting PriceHunter UZ...")

    await init_database()

    logger.info("✅ Database initialized")

    yield

    logger.info("🛑 Shutting down...")

    await bot.session.close()


app = FastAPI(
    title="PriceHunter UZ",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_router)


@app.get("/")
async def root():
    return JSONResponse(
        {
            "status": "ok",
            "service": "PriceHunter UZ",
        }
    )


@app.get("/health")
async def health():
    return JSONResponse(
        {
            "status": "healthy",
        }
    )
