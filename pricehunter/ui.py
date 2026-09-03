from datetime import datetime, timezone, timedelta
from html import escape
import re
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from .providers import MARKETS

MENU = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔎 Поиск'), KeyboardButton(text='🏪 Площадки')],
    [KeyboardButton(text='⭐ Избранное'), KeyboardButton(text='🕘 История')],
    [KeyboardButton(text='⚙️ Настройки'), KeyboardButton(text='ℹ️ Помощь')],
], resize_keyboard=True, input_field_placeholder='Например: Samsung S25 Ultra 256')


def keyboard(rows):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, **({'url': value} if value.startswith('https://') else {'callback_data': value}))
        for label, value in row] for row in rows])


def money(p):
    if p.price is None:
        return 'Цена не указана'
    return f'{p.price:,}'.replace(',', ' ') + (' сум' if p.currency == 'UZS' else ' ' + escape(p.currency))


def title_text(value):
    text = ' '.join(str(value).split())
    text = re.sub(r'\biphone\b', 'iPhone', text, flags=re.I)
    text = re.sub(r'\bipad\b', 'iPad', text, flags=re.I)
    return text


def product_button(product, index):
    title = title_text(product.title)
    title = re.sub(r"^(?:Смартфон|Пылесос|Телевизор|Ноутбук)\s+", "", title, flags=re.I)
    title = re.sub(r"^Apple\s+(?=iPhone|iPad)", "", title)
    title = title if len(title) <= 34 else title[:33].rstrip() + '…'
    price = f'{product.price:,}'.replace(',', ' ') if product.price else 'цена —'
    return f'{index+1}. {title} · {price}'


def card(p):
    when = datetime.fromtimestamp(p.checked_at, timezone(timedelta(hours=5))).strftime('%d.%m %H:%M')
    return (f'<b>{escape(title_text(p.title))}</b>\n\n💰 <b>{money(p)}</b>\n'
            f'🏪 {escape(MARKETS[p.store].name)}\n🕒 Данные: {when} (Ташкент)\n\n'
            + (f'📦 {escape(p.condition)}\n' if p.condition else '')
            + (f'📍 {escape(p.location)}\n' if p.location else '')
            + 'Доставка и наличие уточняются у продавца.')


STATUS = {'browser_unavailable': '⚙️ браузер поиска не запущен', 'ok': '✅ получены товары', 'empty': '— нет результатов',
          'link': '↗️ поиск на сайте', 'blocked': '🔒 сайт ограничил доступ',
          'timeout': '⏳ сайт не ответил вовремя', 'unsupported': '↗️ цены автоматически недоступны',
          'error': '⚠️ ошибка соединения'}


def page_view(session, sid, page):
    items = session['items']
    pages = max(1, (len(items) + 3) // 4)
    page = max(0, min(page, pages-1))
    text = f'🔎 <b>{escape(session["query"])}</b>\n'
    text += f'Предложений после фильтров: <b>{len(items)}</b> · {page+1}/{pages}\n'
    if session['cached']:
        text += '♻️ Результаты из кэша (до 3 минут)\n'
    if session.get('budget'):
        text += f'Бюджет: до {session["budget"]:,} сум\n'.replace(',', ' ')
    text += 'Сортировка: ' + ('по цене' if session.get('sort') == 'price' else 'по совпадению') + '\n'
    rows = []
    for index in range(page*4, min(page*4+4, len(items))):
        p = items[index]
        text += f'\n<b>{index+1}. {escape(title_text(p.title))}</b>\n{money(p)} · {MARKETS[p.store].name}\n'
        if p.condition:
            text += f'📦 {escape(p.condition)}\n'
        rows.append([(product_button(p, index), f'card:{sid}:{index}')])
    if not items:
        text += '\nНет подходящих карточек. Попробуйте короче запрос или снимите бюджет. Поиск на сайтах доступен ниже.\n'
    received = [MARKETS[r.store].name for r in session['results'] if r.status == 'ok']
    unavailable = [MARKETS[r.store].name for r in session['results'] if r.status not in ('ok', 'empty')]
    if received:
        text += '\nПолучены товары: ' + ', '.join(received)
    if unavailable:
        text += '\nБез автоматических карточек: ' + ', '.join(unavailable)
    text += '\n\nНажмите название товара — откроется карточка с фото. Выдача может быть неполной.'
    nav = []
    if page:
        nav.append(('← Назад', f'page:{sid}:{page-1}'))
    if page < pages-1:
        nav.append(('Далее →', f'page:{sid}:{page+1}'))
    if nav:
        rows.append(nav)
    rows.append([('↕️ Сортировка', f'sort:{sid}:0'), ('🏪 Статус площадок', f'status:{sid}:0')])
    return text, keyboard(rows)
