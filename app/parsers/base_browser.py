from abc import ABC, abstractmethod

from playwright.async_api import async_playwright


class BaseBrowserParser(ABC):

    async def browser(self):
        p = await async_playwright().start()

        browser = await p.chromium.launch(
            headless=True
        )

        return p, browser

    @abstractmethod
    async def search(self, query: str):
        pass
