from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from aiogram.types import Update

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.core.logger import logger
from app.core.settings import settings

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):

    if settings.WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if secret != settings.WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret")
            raise HTTPException(status_code=403)

    data = await request.json()

    logger.info(f"Webhook update received: {data.get('update_id')}")

    update = Update.model_validate(data)

    await dp.feed_update(bot, update)

    logger.success("Update processed")

    return {"ok": True}
