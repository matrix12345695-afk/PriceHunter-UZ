import asyncio
import logging
import secrets
import time
from collections import OrderedDict
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from .providers import MARKETS
from .service import normalize, select_products
from .ui import MENU, keyboard, card, page_view, STATUS
logger = logging.getLogger(__name__)

class BotApp:

    def __init__(self, service, storage):
        self.service, self.storage = (service, storage)
        self.sessions = OrderedDict()
        self.busy = set()
        self.last = OrderedDict()
        self.waiting_budget = set()
        self.router = Router()
        self.router.message.filter(F.chat.type == 'private')
        self.router.callback_query.filter(F.message.chat.type == 'private')
        self.router.message.register(self.start, CommandStart())
        self.router.message.register(self.help, Command('help'))
        self.router.message.register(self.forget, Command('forget'))
        self.router.message.register(self.message, F.text)
        self.router.callback_query.register(self.callback)

    async def start(self, m: Message):
        self.waiting_budget.discard(m.from_user.id)
        await m.answer('🛍 <b>PriceHunter UZ</b>\n\nНайдём предложения и откроем поиск на площадках.\nОтправьте название товара, например <b>Samsung S25 Ultra 256</b>.\n\nВыбор магазинов, бюджет, история и избранное — в меню ниже.', reply_markup=MENU)

    async def help(self, m):
        await m.answer('ℹ️ <b>Как пользоваться</b>\n\n1. Выберите площадки или оставьте все.\n2. Напишите модель товара.\n3. Откройте карточку и сохраните её в избранное.\n\nБюджет и сортировка — в настройках. Цена рассрочки не заменяет полную стоимость. Поиск может вернуть только часть каталога.\n\nЕсли сайт ограничивает доступ, используйте кнопку перехода. Избранное хранит цену на момент поиска; автоматических уведомлений об изменении цены в этой версии нет.\n\nИстория (10 запросов), настройки и избранное сохраняются локально. /forget — удалить свои данные.', reply_markup=MENU)

    async def forget(self, m):
        await self.storage.clear(m.from_user.id)
        for sid in list(self.sessions):
            if self.sessions[sid]['user'] == m.from_user.id:
                del self.sessions[sid]
        self.waiting_budget.discard(m.from_user.id)
        await m.answer('Ваши настройки, история и избранное удалены.', reply_markup=MENU)

    async def stores(self, m, user):
        chosen = (await self.storage.settings(user))['stores']
        rows = [[(('✅ ' if not chosen or k in chosen else '▫️ ') + v.name, 'store:' + k)] for k, v in MARKETS.items()]
        rows.append([('✅ Все площадки', 'store:all')])
        await m.answer('🏪 <b>Площадки</b>\nНажмите, чтобы включить или выключить магазин. Для части площадок доступен только переход на сайт.', reply_markup=keyboard(rows))

    async def settings(self, m, user):
        s = await self.storage.settings(user)
        budget = f"{s['budget']:,} сум".replace(',', ' ') if s['budget'] else 'без ограничения'
        await m.answer(f'⚙️ <b>Настройки</b>\nБюджет: {budget}\nСортировка: ' + ('по цене' if s['sort'] == 'price' else 'по совпадению'), reply_markup=keyboard([[('💰 Указать бюджет', 'budget:set'), ('Сбросить', 'budget:clear')], [('↕️ Изменить сортировку', 'settings:sort')]]))

    async def message(self, m: Message):
        user, text = (m.from_user.id, m.text.strip())
        if text in ('🔎 Поиск', '🏪 Площадки', '⭐ Избранное', '🕘 История', '⚙️ Настройки', 'ℹ️ Помощь'):
            self.waiting_budget.discard(user)
        if text == '🔎 Поиск':
            return await m.answer('Напишите название и модель товара.', reply_markup=MENU)
        if text == '🏪 Площадки':
            return await self.stores(m, user)
        if text == '⚙️ Настройки':
            return await self.settings(m, user)
        if text == 'ℹ️ Помощь':
            return await self.help(m)
        if text == '⭐ Избранное':
            rows = [[(p.title[:50], f'favopen:{fid}')] for fid, p in await self.storage.favorites(user)]
            return await m.answer('⭐ <b>Избранное</b>' if rows else 'Избранное пусто. Сохраните товар из карточки.', reply_markup=keyboard(rows) if rows else MENU)
        if text == '🕘 История':
            rows = [[(q[:50], f'history:{hid}')] for hid, q in await self.storage.history(user)]
            return await m.answer('🕘 <b>Последние запросы</b>' if rows else 'Пока нет запросов.', reply_markup=keyboard(rows) if rows else MENU)
        if user in self.waiting_budget:
            from .models import amount
            budget = amount(text)
            if not budget:
                return await m.answer('Введите положительную сумму, например 5 000 000. Для отмены нажмите «🔎 Поиск».')
            await self.storage.update(user, budget=budget)
            self.waiting_budget.discard(user)
            return await self.settings(m, user)
        if text.startswith('/'):
            return await m.answer('Используйте /start, /help или /forget.', reply_markup=MENU)
        await self.search(m, user, text)

    async def search(self, m, user, query):
        try:
            query = normalize(query)
        except ValueError as e:
            return await m.answer(str(e))
        if user in self.busy:
            return await m.answer('Предыдущий поиск ещё выполняется. Подождите несколько секунд.')
        if time.monotonic() - self.last.get(user, 0) < 3:
            return await m.answer('Повторите поиск через несколько секунд.')
        self.last[user] = time.monotonic()
        self.last.move_to_end(user)
        if len(self.last) > 5000:
            self.last.popitem(last=False)
        self.busy.add(user)
        progress = None
        try:
            progress = await m.answer('🔎 Ищу предложения… Открываю каталоги площадок. Поиск может занять до 3 минут.')
            settings = await self.storage.settings(user)
            async with asyncio.timeout(200):
                results, cached = await self.service.search(query, settings['stores'])
            await self.storage.remember(user, query)
            sid = secrets.token_hex(5)
            session = dict(user=user, query=query, results=results, cached=cached, budget=settings['budget'], sort=settings['sort'], created=time.monotonic(), items=select_products(results, query, settings['budget'], settings['sort']))
            self.sessions[sid] = session
            while len(self.sessions) > 500:
                self.sessions.popitem(last=False)
            text, markup = page_view(session, sid, 0)
            await progress.edit_text(text, reply_markup=markup)
        except Exception as e:
            logger.error('Search failed: %s', type(e).__name__)
            if progress:
                await progress.edit_text('Не удалось завершить поиск. Попробуйте ещё раз через минуту.')
        finally:
            self.busy.discard(user)

    async def send_product(self, message, product, markup):
        from .providers import image_url
        photo = image_url(product.image)
        if photo:
            try:
                return await message.answer_photo(photo=photo, caption=card(product), reply_markup=markup)
            except TelegramBadRequest as exc:
                # Telegram may reject an image even when the product page is accessible.
                reason = str(exc).lower()
                if not any(word in reason for word in ('photo', 'image', 'url', 'http', 'file', 'content')):
                    raise
                logger.warning('Product photo rejected for store=%s', product.store)
                try:
                    from .photos import download_photo
                    async with asyncio.timeout(12):
                        uploaded = await download_photo(photo)
                    return await message.answer_photo(photo=uploaded, caption=card(product), reply_markup=markup)
                except (ValueError, OSError, TimeoutError, TelegramBadRequest):
                    logger.warning('Product photo unavailable for store=%s', product.store)
                except Exception as download_error:
                    # Network/image failure should not lose the product card.
                    if isinstance(download_error, (KeyboardInterrupt, SystemExit)):
                        raise
                    logger.warning('Photo transfer failed: %s', type(download_error).__name__)

        return await message.answer(card(product) + '\n\nФото сейчас недоступно у источника.', reply_markup=markup)

    async def callback(self, c: CallbackQuery):
        await c.answer()
        user, m = (c.from_user.id, c.message)
        parts = (c.data or '').split(':')
        try:
            action = parts[0]
            if action == 'store':
                key = parts[1]
                if key not in MARKETS and key != 'all':
                    return
                selected = set((await self.storage.settings(user))['stores'] or MARKETS)
                if key == 'all':
                    selected = set()
                elif key in selected:
                    if len(selected) == 1:
                        return await m.answer('Оставьте хотя бы одну площадку.')
                    selected.remove(key)
                else:
                    selected.add(key)
                await self.storage.update(user, stores=sorted(selected))
                return await self.stores(m, user)
            if action == 'budget':
                if parts[1] == 'set':
                    self.waiting_budget.add(user)
                    return await m.answer('Введите максимальную полную стоимость в сумах, например 5000000.')
                self.waiting_budget.discard(user)
                await self.storage.update(user, budget=None)
                return await self.settings(m, user)
            if action == 'settings':
                current = (await self.storage.settings(user))['sort']
                await self.storage.update(user, sort='price' if current == 'relevance' else 'relevance')
                return await self.settings(m, user)
            if action == 'history':
                query = next((q for hid, q in await self.storage.history(user) if hid == int(parts[1])), None)
                if query:
                    return await self.search(m, user, query)
                return await m.answer('Запрос уже удалён из истории.')
            if action in ('favopen', 'favdelete'):
                product = next((p for fid, p in await self.storage.favorites(user) if fid == int(parts[1])), None)
                if not product:
                    return await m.answer('Товар уже удалён.')
                if action == 'favdelete':
                    await self.storage.favorite(user, product)
                    return await m.answer('Удалено из избранного.')
                return await self.send_product(m, product, keyboard([[('🛍 Открыть товар в магазине', product.url)], [('🗑 Удалить из избранного', f'favdelete:{parts[1]}')]]))
            if len(parts) != 3 or action not in ('page', 'card', 'save', 'remove', 'sort', 'links', 'status'):
                return
            sid, index = (parts[1], int(parts[2]))
            session = self.sessions.get(sid)
            if not session or session['user'] != user or time.monotonic() - session['created'] > 3600:
                return await m.answer('Эта выдача устарела. Повторите запрос через историю или отправьте название товара.')
            if action == 'status':
                text = '<b>Площадки по этому запросу</b>\n\n' + '\n'.join(
                    f'{MARKETS[r.store].name}: {STATUS[r.status]}' for r in session['results'])
                return await m.answer(text, reply_markup=keyboard([[('Поиск на сайтах', f'links:{sid}:0')]]))
            if action == 'links':
                rows = [[(MARKETS[r.store].name, MARKETS[r.store].search_url(session['query']))] for r in session['results']]
                return await m.answer('🏪 Открыть поиск на сайте\nЦена и наличие уточняются на площадке.', reply_markup=keyboard(rows))
            if action == 'sort':
                session = dict(session)
                session['sort'] = 'price' if session['sort'] == 'relevance' else 'relevance'
                session['items'] = select_products(session['results'], session['query'], session['budget'], session['sort'])
                sid = secrets.token_hex(5)
                self.sessions[sid] = session
                while len(self.sessions) > 500:
                    self.sessions.popitem(last=False)
                index = 0
            if action in ('page', 'sort'):
                text, markup = page_view(session, sid, index)
                try:
                    await m.edit_text(text, reply_markup=markup)
                except TelegramBadRequest as e:
                    if 'message is not modified' not in str(e):
                        raise
                return
            if not 0 <= index < len(session['items']):
                return
            product = session['items'][index]
            favorites = await self.storage.favorites(user)
            exists = any(p.url == product.url for _, p in favorites)
            if action == 'save':
                if not exists:
                    await self.storage.favorite(user, product)
                return await m.answer('⭐ Товар сохранён в избранном.')
            if action == 'remove':
                if exists:
                    await self.storage.favorite(user, product)
                return await m.answer('Товар удалён из избранного.')
            rows = [[('🛍 Открыть товар в магазине', product.url)],
                    [('🗑 Удалить из избранного' if exists else '⭐ В избранное',
                      f'{"remove" if exists else "save"}:{sid}:{index}')]]
            nav = []
            if index > 0:
                nav.append(('← Предыдущий товар', f'card:{sid}:{index-1}'))
            if index+1 < len(session['items']):
                nav.append(('Следующий товар →', f'card:{sid}:{index+1}'))
            if nav:
                rows.append(nav)
            await self.send_product(m, product, keyboard(rows))
        except (ValueError, IndexError) as e:
            await m.answer(str(e) if 'Лимит' in str(e) else 'Кнопка устарела. Откройте меню заново.')

async def run_bot(token, service, storage):
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import BotCommand, LinkPreviewOptions
    app = BotApp(service, storage)
    dp = Dispatcher()
    dp.include_router(app.router)
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview=LinkPreviewOptions(is_disabled=True)))
    try:
        await bot.set_my_commands([BotCommand(command='start', description='Главное меню'), BotCommand(command='help', description='Помощь'), BotCommand(command='forget', description='Удалить мои данные')])
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
