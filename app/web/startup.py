from __future__ import annotations

from app.bot.bot import bot
from app.core.logger import logger
from app.core.settings import settings


async def setup_webhook() -> None:
    """
    Регистрирует webhook в Telegram.
    """

    webhook_url = f"{settings.WEBHOOK_URL.rstrip('/')}/webhook"

    logger.info(f"Setting webhook: {webhook_url}")

    #
    # Удаляем старый webhook
    #

    delete_result = await bot.delete_webhook(
        drop_pending_updates=True,
    )

    logger.info(f"deleteWebhook result: {delete_result}")

    #
    # Устанавливаем новый webhook
    #

    set_result = await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.WEBHOOK_SECRET or None,
        allowed_updates=["message", "callback_query"],
    )

    logger.info(f"setWebhook result: {set_result}")

    #
    # Проверяем, что Telegram реально сохранил webhook
    #

    info = await bot.get_webhook_info()

    logger.info("========== WEBHOOK INFO ==========")
    logger.info(f"URL: {info.url}")
    logger.info(f"Pending updates: {info.pending_update_count}")
    logger.info(f"Last error date: {info.last_error_date}")
    logger.info(f"Last error message: {info.last_error_message}")
    logger.info(f"Has custom certificate: {info.has_custom_certificate}")
    logger.info("==================================")

    if info.url != webhook_url:
        logger.error(
            "Webhook was NOT installed correctly!"
        )
    else:
        logger.success(
            "Webhook successfully registered."
        )


async def remove_webhook() -> None:
    """
    Удаляет webhook.
    """

    logger.info("Removing webhook...")

    result = await bot.delete_webhook(
        drop_pending_updates=False,
    )

    logger.info(f"deleteWebhook result: {result}")

    logger.success("Webhook removed")
