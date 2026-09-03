import asyncio
import re
import time
from collections import OrderedDict
import httpx
from .providers import MARKETS, search_market


def normalize(query):
    q = ' '.join(query.split())
    if not 2 <= len(q) <= 120:
        raise ValueError('Введите от 2 до 120 символов.')
    return q


class SearchService:
    def __init__(self, client=None, ttl=180, browser=None):
        self.browser = browser
        self.client = client or httpx.AsyncClient(timeout=8, follow_redirects=True,
            limits=httpx.Limits(max_connections=12, max_keepalive_connections=8),
            headers={'User-Agent': 'PriceHunterUZ/1.0', 'Accept-Language': 'ru'})
        self.cache = OrderedDict()
        self.ttl = ttl
        self.semaphore = asyncio.Semaphore(8)

    async def close(self):
        await self.client.aclose()
        if self.browser:
            await self.browser.close()

    async def search(self, query, stores=None):
        query = normalize(query)
        keys = tuple(sorted(k for k in (stores or MARKETS) if k in MARKETS))
        key = (query.casefold(), keys)
        cached = self.cache.get(key)
        if cached and time.monotonic() - cached[0] < self.ttl:
            return cached[1], True
        async def one(k):
            async with self.semaphore:
                market = MARKETS[k]
                if market.mode == 'browser':
                    if self.browser:
                        return await self.browser.search(market, query)
                    from .models import Result
                    return Result(k, 'browser_unavailable')
                result = await search_market(self.client, market, query)
                if self.browser and k == 'asaxiy' and result.status in ('blocked', 'unsupported', 'error', 'timeout'):
                    return await self.browser.search(market, query)
                return result
        results = await asyncio.gather(*(one(k) for k in keys))
        self.cache[key] = (time.monotonic(), results)
        self.cache.move_to_end(key)
        while len(self.cache) > 150:
            self.cache.popitem(last=False)
        return results, False


def select_products(results, query, budget=None, sort='relevance'):
    tokens = re.findall(r'\w+', query.casefold())
    unique = {}
    for result in results:
        for p in result.products:
            title = p.title.casefold()
            if not all(t in title for t in tokens):
                continue
            if budget and (p.currency != 'UZS' or p.price is None or p.price > budget):
                continue
            unique[(p.store, p.url)] = p
    items = list(unique.values())
    if sort == 'price':
        items.sort(key=lambda p: (p.currency != 'UZS' or p.price is None, p.price if p.currency == 'UZS' and p.price else float('inf')))
    else:
        accessory = ('чехол', 'стекло', 'кабель', 'держатель', 'case', 'cover')
        items.sort(key=lambda p: (any(w in p.title.casefold() and w not in query.casefold() for w in accessory), len(p.title)))
    return items
