from datetime import datetime, timezone, timedelta
from html import escape
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


def card(p):
    when = datetime.fromtimestamp(p.checked_at, timezone(timedelta(hours=5))).strftime('%d.%m %H:%M')
    return (f'<b>{escape(p.title)}</b>\n\n💰 <b>{money(p)}</b>\n'
            f'🏪 {escape(MARKETS[p.store].name)}\n🕒 Данные: {when} (Ташкент)\n\n'
            'Проверьте комплектацию, наличие и итоговую цену на сайте.')


STATUS = {'ok': '✅ получены товары', 'empty': '— нет результатов',
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
        text += f'\n<b>{index+1}. {escape(p.title)}</b>\n{money(p)} · {MARKETS[p.store].name}\n'
        rows.append([(f'{index+1}. Открыть карточку', f'card:{sid}:{index}')])
    if not items:
        text += '\nНет подходящих карточек. Попробуйте короче запрос или снимите бюджет. Поиск на сайтах доступен ниже.\n'
    text += '\n<b>Площадки</b>\n' + '\n'.join(f'{MARKETS[r.store].name}: {STATUS[r.status]}' for r in session['results'])
    text += '\n\nСравнивайте одинаковые модели и объём памяти. Доставка не включена. Выдача площадок может быть неполной.'
    nav = []
    if page:
        nav.append(('← Назад', f'page:{sid}:{page-1}'))
    if page < pages-1:
        nav.append(('Далее →', f'page:{sid}:{page+1}'))
    if nav:
        rows.append(nav)
    rows.append([('↕️ Сортировка', f'sort:{sid}:0'), ('🏪 Поиск на сайтах', f'links:{sid}:0')])
    return text, keyboard(rows)
