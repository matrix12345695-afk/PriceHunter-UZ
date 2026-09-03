import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
import httpx
from pricehunter.providers import MARKETS, parse_html
from pricehunter.models import Result
from pricehunter.service import SearchService
from pricehunter.browser import BrowserRenderer
from pricehunter.browser_cards import visible_price

FIX = Path(__file__).parent / 'fixtures'

@pytest.mark.parametrize('key,price', [('olx',15933915), ('uzum',17999000), ('wildberries',17461700)])
def test_real_rendered_cards(key, price):
    cards = parse_html((FIX/f'{key}-browser.html').read_text(),MARKETS[key])
    assert len(cards) == 4
    assert cards[0].price == price
    assert all(p.image.startswith('https://') and p.currency=='UZS' and p.title for p in cards)
    if key=='uzum': assert 'skuId=' in cards[0].url
    if key=='olx': assert cards[0].condition == 'Б/у' and 'Ташкент' in cards[0].location


def test_currency_not_assumed():
    assert visible_price('1 500 $ Договорная') == (1500,'USD')
    assert visible_price('12 000 руб.') == (12000,'RUB')
    assert visible_price('1 000') == (1000,'UNKNOWN')


def test_browser_routing_and_asaxiy_fallback():
    async def run():
        browser=AsyncMock()
        browser.search.side_effect=lambda market,q: Result(market.key,'ok')
        client=httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(403)))
        service=SearchService(client=client,browser=browser)
        with patch('pricehunter.service.search_market',new=AsyncMock(return_value=Result('asaxiy','blocked'))) as direct:
            results,_=await service.search('iphone',['uzum','olx','wildberries','asaxiy'])
            assert all(r.status=='ok' for r in results)
            assert browser.search.await_count==4
            assert direct.await_count==1
            await service.search('iphone',['uzum','olx','wildberries','asaxiy'])
            assert browser.search.await_count==4
        await service.close()
        browser.close.assert_awaited_once()
    asyncio.run(run())


def test_missing_browser_is_explicit():
    async def run():
        renderer=BrowserRenderer()
        renderer._start=AsyncMock(side_effect=RuntimeError('unavailable'))
        result=await renderer.search(MARKETS['uzum'],'iphone')
        assert result.status=='browser_unavailable'
        assert not result.products
    asyncio.run(run())


def test_no_browser_for_unverified_markets():
    async def run():
        renderer=BrowserRenderer()
        renderer._start=AsyncMock()
        assert (await renderer.search(MARKETS['aliexpress'],'iphone')).status=='unsupported'
        renderer._start.assert_not_awaited()
    asyncio.run(run())


def test_renderer_parses_and_closes_context():
    import sys
    from types import SimpleNamespace
    async def run():
        page=AsyncMock()
        page.goto.return_value=SimpleNamespace(status=200)
        page.title.return_value='Uzum Market'
        page.locator=lambda _:SimpleNamespace(count=AsyncMock(return_value=4))
        page.content.return_value=(FIX/'uzum-browser.html').read_text()
        context=AsyncMock()
        context.new_page.return_value=page
        renderer=BrowserRenderer()
        renderer.browser=AsyncMock()
        renderer.browser.new_context.return_value=context
        renderer._start=AsyncMock()
        fake=SimpleNamespace(TimeoutError=TimeoutError)
        with patch.dict(sys.modules, {'playwright.async_api':fake}):
            result=await renderer.search(MARKETS['uzum'],'iphone')
        assert result.status=='ok' and len(result.products)==4
        context.close.assert_awaited_once()
    asyncio.run(run())


def test_renderer_does_not_parse_access_denied():
    import sys
    from types import SimpleNamespace
    async def run():
        page=AsyncMock()
        page.goto.return_value=SimpleNamespace(status=403)
        context=AsyncMock()
        context.new_page.return_value=page
        renderer=BrowserRenderer()
        renderer.browser=AsyncMock()
        renderer.browser.new_context.return_value=context
        renderer._start=AsyncMock()
        with patch.dict(sys.modules, {'playwright.async_api':SimpleNamespace(TimeoutError=TimeoutError)}):
            result=await renderer.search(MARKETS['asaxiy'],'iphone')
        assert result.status=='blocked'
        page.content.assert_not_awaited()
        context.close.assert_awaited_once()
    asyncio.run(run())
