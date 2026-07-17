from __future__ import annotations

import logging

from playwright.async_api import Page

from ..config import SCREENSHOT_DIR
from ..utils import ensure_directory

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class ScreenshotCapture(CapturePlugin):
    """
    Автоматически сохраняет скриншот каждой
    полностью загруженной страницы.
    """

    @property
    def name(self) -> str:
        return "screenshot"

    def __init__(self) -> None:

        ensure_directory(SCREENSHOT_DIR)

        self._counter = 0

    async def on_page_loaded(
        self,
        page: Page,
    ) -> None:

        self._counter += 1

        filename = (
            SCREENSHOT_DIR
            / f"{self._counter:04d}.png"
        )

        try:

            await page.screenshot(
                path=str(filename),
                full_page=True,
            )

            logger.info(
                "Screenshot saved: %s",
                filename.name,
            )

        except Exception as exc:

            logger.warning(
                "Unable to save screenshot: %s",
                exc,
            )

    async def startup(self) -> None:

        logger.info(
            "ScreenshotCapture started."
        )

    async def shutdown(self) -> None:

        logger.info(
            "Captured %d screenshots.",
            self._counter,
        )