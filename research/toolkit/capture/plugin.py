from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from playwright.async_api import (
    BrowserContext,
    Page,
    Request,
    Response,
)


class CapturePlugin(ABC):
    """
    Базовый интерфейс всех Capture-плагинов.

    Explorer ничего не знает о GraphQL, REST,
    Cookie, HTML и т.д.

    Он просто вызывает события,
    а зарегистрированные плагины решают,
    что с ними делать.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя плагина."""

    async def startup(self) -> None:
        """
        Вызывается один раз
        перед началом исследования.
        """

    async def shutdown(self) -> None:
        """
        Вызывается один раз
        после окончания исследования.
        """

    async def on_context_created(
        self,
        context: BrowserContext,
    ) -> None:
        """
        Создан BrowserContext.
        """

    async def on_page_created(
        self,
        page: Page,
    ) -> None:
        """
        Создана новая вкладка.
        """

    async def on_request(
        self,
        request: Request,
    ) -> None:
        """
        Любой HTTP Request.
        """

    async def on_response(
        self,
        response: Response,
    ) -> None:
        """
        Любой HTTP Response.
        """

    async def on_page_loaded(
        self,
        page: Page,
    ) -> None:
        """
        Страница полностью загружена.
        """

    async def on_finished(self) -> None:
        """
        Исследование завершено.
        """