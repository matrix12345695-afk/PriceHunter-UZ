"""Ordinary Chromium rendering. No login, proxy, CAPTCHA solving or TLS overrides."""
import asyncio
from contextlib import suppress
from .models import Result
from .providers import parse_html
from .browser_cards import SELECTORS


class BrowserRenderer:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.runtime = None
        self.browser = None
        self.start_failed = False

    async def close(self):
        if self.browser:
            with suppress(Exception):
                await self.browser.close()
        if self.runtime:
            with suppress(Exception):
                await self.runtime.stop()
        self.browser = self.runtime = None

    async def _start(self):
        if self.browser and self.browser.is_connected():
            return
        if self.start_failed:
            raise RuntimeError('Chromium unavailable')
        await self.close()
        try:
            from playwright.async_api import async_playwright
            self.runtime = await async_playwright().start()
            self.browser = await self.runtime.chromium.launch(headless=True)
        except Exception:
            self.start_failed = True
            await self.close()
            raise

    async def search(self, market, query):
        if market.key not in SELECTORS:
            return Result(market.key, 'unsupported')
        # One active page limits memory and outbound concurrency on Render.
        async with self.lock:
            try:
                async with asyncio.timeout(15):
                    await self._start()
            except Exception:
                return Result(market.key, 'browser_unavailable', detail='Install Chromium and system dependencies; check server memory')
            context = None
            try:
                async with asyncio.timeout(38):
                    from playwright.async_api import TimeoutError as NavigationTimeout
                    context = await self.browser.new_context(locale='ru-RU', viewport={'width':1280, 'height':900})
                    page = await context.new_page()
                    try:
                        response = await page.goto(market.search_url(query), wait_until='domcontentloaded', timeout=18000)
                        if response and response.status in (401, 403, 429):
                            return Result(market.key, 'blocked', detail=f'HTTP {response.status}')
                        if response and response.status >= 400:
                            return Result(market.key, 'error', detail=f'HTTP {response.status}')
                    except NavigationTimeout:
                        pass  # The catalogue may still finish rendering within the total budget.
                    while True:
                        title = (await page.title()).casefold()
                        if any(word in title for word in ('captcha', 'access denied', 'just a moment', 'проверка безопасности')):
                            return Result(market.key, 'blocked')
                        cards = await page.locator(SELECTORS[market.key]).count()
                        if cards:
                            products = parse_html(await page.content(), market)
                            if products:
                                return Result(market.key, 'ok', products[:40], detail='browser')
                        await asyncio.sleep(.75)
            except TimeoutError:
                return Result(market.key, 'timeout', detail='Catalogue did not render within 38 seconds')
            except Exception as exc:
                return Result(market.key, 'error', detail=type(exc).__name__)
            finally:
                if context:
                    with suppress(Exception):
                        async with asyncio.timeout(3):
                            await context.close()
