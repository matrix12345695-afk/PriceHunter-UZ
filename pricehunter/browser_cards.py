"""Parse visible catalogue cards, never installment or crossed-out prices."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .models import Product, amount, safe_url
from .providers import image_url

SELECTORS = {
    'olx': '[data-testid="l-card"]',
    'uzum': '[data-test-id="product-card--default"]',
    'wildberries': 'article.product-card',
    'asaxiy': '.product__item',
}


def visible_price(text, default_currency='UNKNOWN'):
    currency = default_currency
    if re.search(r'сум|so.m|UZS|сўм', text, re.I):
        currency = 'UZS'
    elif re.search(r'USD|\$|у\.?\s*е\.?', text, re.I):
        currency = 'USD'
    elif re.search(r'руб|₽|RUB', text, re.I):
        currency = 'RUB'
    match = re.search(r'\d[\d\s\u00a0\u202f]*(?:[.,]\d+)?', text)
    return (amount(match.group()) if match else None), currency


def parse_cards(html, market):
    soup = BeautifulSoup(html, 'html.parser')
    products = {}
    for card in soup.select(SELECTORS[market.key]):
        condition = location = ''
        if market.key == 'olx':
            anchor = card.select_one('a[href*="/d/obyavlenie/"]')
            title = card.select_one('[data-testid="ad-card-title"] h4, [data-testid="ad-card-title"] h6')
            price = card.select_one('[data-testid="ad-price"]')
            img = card.select_one('img')
            state = card.select_one('[title="Б/у"], [title="Новый"], [title="Новое"]')
            place = card.select_one('[data-testid="location-date"]')
            condition = state.get('title', '') if state else ''
            location = place.get_text(' ', strip=True)[:160] if place else ''
        elif market.key == 'uzum':
            anchor = card
            title = card.select_one('[data-test-id="product-card__title"]')
            price = card.select_one('[data-test-id="product-card__actual-price"]')
            img = card.select_one('.product-card__image img')
        else:
            anchor = card.select_one('a[data-testid="product-card-link"]')
            title = card.select_one('[data-testid="productName"], h2')
            price = card.select_one('.product-card__price ins')
            img = card.select_one('img.j-thumbnail')
        if not anchor or not title or not price:
            continue
        url = urljoin('https://' + market.host, anchor.get('href', ''))
        value, currency = visible_price(price.get_text(' ', strip=True), 'UZS' if market.key == 'uzum' else 'UNKNOWN')
        name = ' '.join(title.get_text(' ', strip=True).split())[:250]
        if not name or not value or not safe_url(url, market.host):
            continue
        photo = (img.get('src') or img.get('data-src') or '') if img else ''
        products[url] = Product(market.key, name, url, value, currency,
                                image=image_url(photo), condition=condition, location=location)
    return list(products.values())
