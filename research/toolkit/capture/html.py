from __future__ import annotations

import logging

from playwright.async_api import Page

from ..config import HTML_DIR
from ..utils import (
    ensure_directory,
    save_text,
)

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class HtmlCapture(CapturePlugin):
    """
    Сохраняет HTML каждой загруженной страницы.
    """

    @property
    def name(self) -> str:
        return "html"

    def __init__(self) -> None:

        ensure_directory(HTML_DIR)

        self._counter = 0

    async def on_page_loaded(
        self,
        page: Page,
    ) -> None:

        self._counter += 1

        try:

            html = await page.content()

        except Exception as exc:

            logger.warning(
                "Unable to get HTML: %s",
                exc,
            )

            return

        filename = (
            HTML_DIR
            / f"{self._counter:04d}.html"
        )

        save_text(
            filename,
            html,
        )

        logger.info(
            "HTML saved: %s",
            filename.name,
        )

    async def startup(self) -> None:

        logger.info(
            "HtmlCapture started."
        )

    async def shutdown(self) -> None:

        logger.info(
            "Captured %d HTML pages.",
            self._counter,
        )