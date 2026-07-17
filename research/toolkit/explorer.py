from __future__ import annotations
from .capture.auth import AuthCapture

import asyncio
import logging
from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
)

from .config import (
    HEADLESS,
    USER_AGENT,
    BROWSER_TIMEOUT,
    WAIT_AFTER_LOAD,
)

from .capture.manager import CaptureManager

from .capture.request import RequestCapture
from .capture.response import ResponseCapture
from .capture.graphql import GraphQLCapture
from .capture.html import HtmlCapture
from .capture.screenshot import ScreenshotCapture
from .capture.cookies import CookieCapture


logger = logging.getLogger(__name__)


class Explorer:
    """
    Explorer v3

    Управляет браузером Playwright.

    Никакой логики анализа здесь нет.

    Explorer только пересылает события
    CaptureManager.
    """

    def __init__(
        self,
        url: str,
    ) -> None:

        self.url = url

        self.browser: Optional[Browser] = None

        self.context: Optional[BrowserContext] = None

        self._playwright = None

        #
        # Чтобы не подключать
        # одну страницу дважды
        #

        self._attached_pages: set[int] = set()

        #
        # Capture Engine
        #

        self.capture = CaptureManager()

        #
        # Register plugins
        #

        self.capture.register(
            RequestCapture()
        )

        self.capture.register(
            AuthCapture()
        )

        self.capture.register(
            ResponseCapture()
        )

        self.capture.register(
            GraphQLCapture()
        )

        self.capture.register(
            HtmlCapture()
        )

        self.capture.register(
            ScreenshotCapture()
        )

        self.capture.register(
            CookieCapture()
        )

    @property
    def plugins(self):

        return self.capture.plugins

    # ==========================================================
    # STARTUP
    # ==========================================================

    async def startup(self) -> None:

        logger.info("=" * 80)
        logger.info("PriceHunter Toolkit")
        logger.info("=" * 80)

        #
        # Plugins startup
        #

        await self.capture.startup()

        #
        # Playwright
        #

        self._playwright = await async_playwright().start()

        #
        # Browser
        #

        self.browser = await self._playwright.chromium.launch(
            headless=HEADLESS,
        )

        logger.info(
            "Browser started."
        )

        #
        # BrowserContext
        #

        self.context = await self.browser.new_context(
            user_agent=USER_AGENT,
        )

        logger.info(
            "Context created."
        )

        await self.capture.on_context_created(
            self.context,
        )

        #
        # Любая новая вкладка
        #

        self.context.on(
            "page",
            lambda page:
                asyncio.create_task(
                    self.attach_page(page)
                ),
        )
    # ==========================================================
    # NEW PAGE
    # ==========================================================

    async def new_page(
        self,
    ) -> Page:

        if self.context is None:
            raise RuntimeError(
                "BrowserContext is not initialized."
            )

        page = await self.context.new_page()

        await self.attach_page(
            page,
        )

        return page

    # ==========================================================
    # ATTACH PAGE
    # ==========================================================

    async def attach_page(
        self,
        page: Page,
    ) -> None:
        """
        Подключает события страницы.
        """

        #
        # Не подключаем одну страницу дважды
        #

        page_id = id(page)

        if page_id in self._attached_pages:
            return

        self._attached_pages.add(
            page_id,
        )

        logger.info(
            "Attach page: %s",
            page.url or "<new page>",
        )

        #
        # Notify plugins
        #

        await self.capture.on_page_created(
            page,
        )

        #
        # REQUEST
        #

        page.on(
            "request",
            lambda request:
                asyncio.create_task(
                    self.capture.on_request(
                        request,
                    )
                ),
        )

        #
        # RESPONSE
        #

        page.on(
            "response",
            lambda response:
                asyncio.create_task(
                    self.capture.on_response(
                        response,
                    )
                ),
        )

        #
        # POPUP
        #

        page.on(
            "popup",
            lambda popup:
                asyncio.create_task(
                    self.attach_page(
                        popup,
                    )
                ),
        )

        #
        # PAGE LOADED
        #

        async def page_loaded():

            try:

                await page.wait_for_load_state(
                    "networkidle",
                    timeout=BROWSER_TIMEOUT,
                )

            except Exception:

                #
                # Некоторые сайты
                # никогда не достигают
                # networkidle.
                #

                pass

            try:

                await asyncio.sleep(
                    WAIT_AFTER_LOAD,
                )

                await self.capture.on_page_loaded(
                    page,
                )

            except Exception:

                logger.exception(
                    "on_page_loaded failed."
                )

        asyncio.create_task(
            page_loaded()
        )

        logger.info(
            "Page attached."
        )
    # ==========================================================
    # EXPLORE
    # ==========================================================

    async def explore(
        self,
    ) -> None:
        """
        Основной запуск исследования.
        """

        await self.startup()

        try:

            page = await self.new_page()

            logger.info(
                "Opening %s",
                self.url,
            )

            try:

                await page.goto(
                    self.url,
                    wait_until="domcontentloaded",
                    timeout=BROWSER_TIMEOUT,
                )

            except Exception as exc:

                logger.exception(
                    "Navigation failed: %s",
                    exc,
                )

                return

            #
            logger.info("")
            logger.info("=" * 80)
            logger.info("Toolkit is running.")
            logger.info("")

            logger.info("Explore Uzum manually.")
            logger.info("")

            logger.info("When finished press ENTER in this console.")
            logger.info("=" * 80)

            await asyncio.to_thread(input)

        finally:

            await self.shutdown()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    async def shutdown(
        self,
    ) -> None:

        logger.info(
            "Finishing capture..."
        )

        #
        # Даём последним запросам
        # завершиться
        #

        await asyncio.sleep(1)

        #
        # Notify plugins
        #

        await self.capture.on_finished()

        await self.capture.shutdown()

        #
        # Context
        #

        if self.context is not None:

            try:

                await self.context.close()

            except Exception:

                logger.exception(
                    "Unable to close context."
                )

        #
        # Browser
        #

        if self.browser is not None:

            try:

                await self.browser.close()

            except Exception:

                logger.exception(
                    "Unable to close browser."
                )

        #
        # Playwright
        #

        if self._playwright is not None:

            try:

                await self._playwright.stop()

            except Exception:

                logger.exception(
                    "Unable to stop Playwright."
                )

        logger.info("=" * 80)
        logger.info("Toolkit finished successfully.")
        logger.info("=" * 80)