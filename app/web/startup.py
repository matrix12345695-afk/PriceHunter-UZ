from __future__ import annotations

from aiogram.client.default import DefaultBotProperties

from app.bot.bot import bot
from app.core.logger import logger
from app.core.settings import settings


async def setup_webhook() -> None:
    """
    Регистрирует webhook в Telegram.
    """

    webhook_url = f"{settings.WEBHOOK_URL.rstrip('/')}/webhook"

    logger.info(f"Setting webhook: {webhook_url}")

    # Удаляем старый webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # Устанавливаем новый
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.WEBHOOK_SECRET or None,
        allowed_updates=None,
    )

    logger.success("Webhook successfully registered")


async def remove_webhook() -> None:
    """
    Удаляет webhook.
    """

    logger.info("Removing webhook...")

    await bot.delete_webhook(drop_pending_updates=False)

    logger.success("Webhook removed")
