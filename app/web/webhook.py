from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from aiogram.types import Update

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.core.settings import settings

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Endpoint, на который Telegram будет отправлять обновления.
    """

    # Если используем секретный токен Telegram
    if settings.WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if secret != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid secret token")

    data = await request.json()

    update = Update.model_validate(data)

    await dp.feed_update(bot, update)

    return {"ok": True}
