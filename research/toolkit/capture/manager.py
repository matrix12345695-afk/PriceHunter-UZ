from __future__ import annotations

import asyncio
import logging

from playwright.async_api import (
    BrowserContext,
    Page,
    Request,
    Response,
)

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class CaptureManager:
    """
    Управляет жизненным циклом Capture-плагинов.

    Explorer работает только с CaptureManager.

    CaptureManager ничего не знает о GraphQL,
    REST, Cookies, HTML и т.д.

    Он лишь пересылает события
    зарегистрированным плагинам.
    """

    def __init__(self) -> None:

        self._plugins: list[CapturePlugin] = []

    # ==========================================================
    # Plugins
    # ==========================================================

    def register(
        self,
        plugin: CapturePlugin,
    ) -> None:

        logger.info(
            "Register plugin: %s",
            plugin.name,
        )

        self._plugins.append(plugin)

    @property
    def plugins(
        self,
    ) -> tuple[CapturePlugin, ...]:

        return tuple(self._plugins)

    # ==========================================================
    # Lifecycle
    # ==========================================================

    async def startup(self) -> None:

        logger.info(
            "Starting %d plugins...",
            len(self._plugins),
        )

        await asyncio.gather(
            *(
                plugin.startup()
                for plugin in self._plugins
            )
        )

    async def shutdown(self) -> None:

        logger.info(
            "Stopping plugins..."
        )

        await asyncio.gather(
            *(
                plugin.shutdown()
                for plugin in self._plugins
            )
        )

    # ==========================================================
    # Browser Context
    # ==========================================================

    async def on_context_created(
        self,
        context: BrowserContext,
    ) -> None:

        await asyncio.gather(
            *(
                plugin.on_context_created(context)
                for plugin in self._plugins
            )
        )

    # ==========================================================
    # Pages
    # ==========================================================

    async def on_page_created(
        self,
        page: Page,
    ) -> None:

        logger.debug(
            "Page created: %s",
            page.url,
        )

        await asyncio.gather(
            *(
                plugin.on_page_created(page)
                for plugin in self._plugins
            )
        )

    async def on_page_loaded(
        self,
        page: Page,
    ) -> None:

        logger.debug(
            "Page loaded: %s",
            page.url,
        )

        await asyncio.gather(
            *(
                plugin.on_page_loaded(page)
                for plugin in self._plugins
            )
        )

    # ==========================================================
    # HTTP
    # ==========================================================

    async def on_request(
        self,
        request: Request,
    ) -> None:

        await asyncio.gather(
            *(
                plugin.on_request(request)
                for plugin in self._plugins
            )
        )

    async def on_response(
        self,
        response: Response,
    ) -> None:

        await asyncio.gather(
            *(
                plugin.on_response(response)
                for plugin in self._plugins
            )
        )

    # ==========================================================
    # Finish
    # ==========================================================

    async def on_finished(
        self,
    ) -> None:

        logger.info(
            "Finishing capture..."
        )

        await asyncio.gather(
            *(
                plugin.on_finished()
                for plugin in self._plugins
            )
        )