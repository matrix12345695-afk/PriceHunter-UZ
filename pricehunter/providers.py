"""Public data only. No saved cookies, private tokens or CAPTCHA bypass."""
import asyncio
import json
import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup
from .models import Product, Result, amount, safe_url


@dataclass(frozen=True)
class Market:
    key: str
    name: str
    host: str
    search_template: str
    mode: str = 'link'

    def search_url(self, query):
        return self.search_template.format(query=quote(query, safe=''))


MARKETS = {
    m.key: m for m in [
        Market('olcha', 'Olcha', 'olcha.uz', 'https://olcha.uz/ru/search?search={query}', 'olcha'),
        Market('uzum', 'Uzum Market', 'uzum.uz', 'https://uzum.uz/ru/search?query={query}', 'structured'),
        Market('asaxiy', 'Asaxiy', 'asaxiy.uz', 'https://asaxiy.uz/product?key={query}', 'asaxiy'),
        Market('texnomart', 'Texnomart', 'texnomart.uz', 'https://texnomart.uz/ru/katalog/?q={query}', 'structured'),
        Market('mediapark', 'Mediapark', 'mediapark.uz', 'https://mediapark.uz/ru/search?product={query}', 'structured'),
        Market('idea', 'IDEA', 'idea.uz', 'https://idea.uz/search?search={query}', 'structured'),
        Market('elmakon', 'Elmakon', 'elmakon.uz', 'https://elmakon.uz/ru/?dispatch=products.search&q={query}', 'structured'),
        Market('olx', 'OLX Uzbekistan', 'olx.uz', 'https://www.olx.uz/list/q-{query}/'),
        Market('wildberries', 'Wildberries UZ', 'wildberries.uz', 'https://www.wildberries.uz/catalog/0/search.aspx?search={query}'),
        Market('aliexpress', 'AliExpress', 'aliexpress.com', 'https://www.aliexpress.com/w/wholesale-{query}.html'),
    ]
}


class SchemaChanged(Exception):
    pass


def parse_olcha(data):
    groups = data.get('results', {}).get('item_groups')
    if not isinstance(groups, list):
        raise SchemaChanged('Olcha response has no item_groups')
    products = []
    for group in groups:
        for item in group.get('items', []):
            title, alias = item.get('name'), item.get('alias')
            if not title or not alias:
                continue
            currency = item.get('currency', 'UZS')
            if str(currency).lower() in ('uzs', 'сум', "so'm", 'sum', 'сўм'):
                currency = 'UZS'
            price = amount(item.get('discount_price')) or amount(item.get('price'))
            products.append(Product('olcha', str(title)[:250],
                'https://olcha.uz/ru/product/view/' + quote(str(alias), safe=''), price, currency))
    return products


def parse_html(html, market):
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            if market.key == 'mediapark' and node.get('product_uuid') and node.get('product_name'):
                slug = node.get('slug', {})
                slug = slug.get('ru') if isinstance(slug, dict) else None
                if slug and not slug.startswith('$') and node.get('is_available') == 'available':
                    products.append(Product(market.key, str(node['product_name'])[:250],
                        'https://mediapark.uz/products/view/' + quote(slug, safe=''),
                        amount(node.get('price_without_installment')) or amount(node.get('actual_price'))))
            if node.get('@type') == 'Product':
                offers = node.get('offers', {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if not isinstance(offers, dict):
                    offers = {}
                url = urljoin('https://' + market.host, str(node.get('url') or offers.get('url') or ''))
                title = node.get('name')
                # Do not label an aggregate lowPrice as a purchasable variant's price.
                price = amount(offers.get('price'))
                currency = str(offers.get('priceCurrency') or 'UNKNOWN').upper()
                if title and safe_url(url, market.host) and urlsplit_path(url) != '/':
                    products.append(Product(market.key, str(title)[:250], url, price, currency))
            for value in node.values():
                if isinstance(value, (list, dict)):
                    walk(value)
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            walk(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError):
            continue
    if market.key == 'mediapark':
        # Decode JSON in React server output; never execute script content.
        for script in soup.find_all('script'):
            match = re.fullmatch(r'self\.__next_f\.push\((.*)\);?', script.get_text().strip(), re.S)
            if not match:
                continue
            try:
                payload = json.loads(match.group(1))
                if len(payload) < 2 or not isinstance(payload[1], str):
                    continue
                for line in payload[1].splitlines():
                    try:
                        walk(json.loads(line.partition(':')[2]))
                    except ValueError:
                        continue
            except (ValueError, TypeError):
                continue
    if market.key == 'asaxiy':
        for card in soup.select('.product__item'):
            data = card.select_one('[data-name-ru][data-price]')
            anchor = card.select_one('a[href*="/product/"]')
            title = card.select_one('.product__item__info-title')
            price = card.select_one('.product__item-price')
            if anchor and (data or title):
                url = urljoin('https://asaxiy.uz', anchor['href'])
                if safe_url(url, market.host):
                    name = data.get('data-name-ru') if data else title.get_text(' ', strip=True)
                    raw = data.get('data-price') if data else card.get('data-actual-price')
                    if not raw and price:
                        raw = price.get_text(' ', strip=True).replace('сум', '').replace("so'm", '')
                    products.append(Product(market.key, str(name)[:250], url, amount(raw)))
    return list({p.url: p for p in products}.values())


def urlsplit_path(url):
    from urllib.parse import urlsplit
    return urlsplit(url).path or '/'


async def fetch(client, url):
    for attempt in range(2):
        try:
            response = await client.get(url)
            if response.status_code >= 500 and attempt == 0:
                await asyncio.sleep(.5)
                continue
            response.raise_for_status()
            if len(response.content) > 8_000_000:
                raise SchemaChanged('Response too large')
            return response
        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt:
                raise
            await asyncio.sleep(.5)


async def search_market(client, market, query):
    if market.mode == 'link':
        return Result(market.key, 'link', detail='Поиск на сайте')
    try:
        async with asyncio.timeout(18):
            if market.mode == 'olcha':
                url = 'https://mobile.olcha.uz/api/v2/multi-search/products/' + quote(query, safe='')
                response = await fetch(client, url + '?category_id=&page=1')
                products = parse_olcha(response.json())
                return Result(market.key, 'ok' if products else 'empty', products)
            response = await fetch(client, market.search_url(query))
            products = parse_html(response.text, market)
            # No parseable cards does not mean there are no products on the site.
            return Result(market.key, 'ok' if products else 'unsupported', products)
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        return Result(market.key, 'blocked' if code in (401, 403, 429) else 'error', detail=f'HTTP {code}')
    except (httpx.TimeoutException, TimeoutError):
        return Result(market.key, 'timeout')
    except (ValueError, TypeError, AttributeError, KeyError, SchemaChanged):
        return Result(market.key, 'unsupported')
    except httpx.HTTPError:
        return Result(market.key, 'error')
