from __future__ import annotations

import json
import logging
from pathlib import Path

from playwright.async_api import Page

from ..config import COOKIE_DIR
from ..utils import ensure_directory

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class CookieCapture(CapturePlugin):
    """
    Сохраняет cookies браузера после загрузки страницы.

    Каждый снимок сохраняется отдельно.
    """

    @property
    def name(self) -> str:
        return "cookies"

    def __init__(self) -> None:

        ensure_directory(COOKIE_DIR)

        self._counter = 0

    async def on_page_loaded(
        self,
        page: Page,
    ) -> None:

        self._counter += 1

        try:

            context = page.context

            cookies = await context.cookies()

        except Exception as exc:

            logger.warning(
                "Unable to read cookies: %s",
                exc,
            )

            return

        filename = (
            Path(COOKIE_DIR)
            / f"{self._counter:04d}.json"
        )

        try:

            with open(
                filename,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    cookies,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.info(
                "Cookies saved: %s",
                filename.name,
            )

        except Exception as exc:

            logger.warning(
                "Unable to save cookies: %s",
                exc,
            )

    async def startup(self) -> None:

        logger.info(
            "CookieCapture started."
        )

    async def shutdown(self) -> None:

        logger.info(
            "Captured %d cookie snapshots.",
            self._counter,
        )