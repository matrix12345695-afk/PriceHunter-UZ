import asyncio
import hashlib
import hmac
import json
import logging
import os
from contextlib import asynccontextmanager, suppress
from urllib.parse import urlsplit
from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError
from aiogram import Bot, Dispatcher
from aiogram.types import Update, LinkPreviewOptions
from aiogram.client.default import DefaultBotProperties
from .bot import BotApp
from .postgres import PostgresStorage
from .browser import BrowserRenderer
from .service import SearchService

log = logging.getLogger('uvicorn.error')


def configuration():
    token = os.getenv('BOT_TOKEN','').strip()
    database = os.getenv('DATABASE_URL','').strip()
    base = (os.getenv('WEBHOOK_URL') or os.getenv('RENDER_EXTERNAL_URL') or '').strip().rstrip('/')
    if not token or not database:
        raise ValueError('Render Environment: BOT_TOKEN and DATABASE_URL are required')
    if urlsplit(base).scheme != 'https' or not urlsplit(base).hostname:
        raise ValueError('Set WEBHOOK_URL to the HTTPS Render service URL')
    # Keep the existing /webhook route and existing secret if configured.
    endpoint = base if base.endswith('/webhook') else base + '/webhook'
    secret = os.getenv('WEBHOOK_SECRET') or hashlib.sha256(('pricehunter-webhook:'+token).encode()).hexdigest()
    if not 1<=len(secret)<=256 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in secret):
        raise ValueError('WEBHOOK_SECRET must use A-Z, a-z, 0-9, underscore or hyphen (1–256 characters)')
    return token,database,endpoint,secret


async def process_queue(app):
    while True:
        try:
            row=await app.state.storage.next_update()
            if not row:
                await asyncio.sleep(.3)
                continue
            try:
                update=Update.model_validate_json(row['payload'])
                await app.state.dispatcher.feed_update(app.state.bot,update)
                await app.state.storage.finish_update(row['update_id'],'done')
            except asyncio.CancelledError:
                await app.state.storage.finish_update(row['update_id'],'pending')
                raise
            except Exception as exc:
                log.error('Update %s failed: %s',row['update_id'],type(exc).__name__)
                await app.state.storage.finish_update(row['update_id'],'pending' if row['attempts']<3 else 'failed')
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.error('Queue unavailable: %s',type(exc).__name__)
            await asyncio.sleep(2)


async def provider_diagnostics(service):
    try:
        results, _ = await service.search('Iphone 17 pro max')
        for result in results:
            log.info('PROVIDER_CHECK store=%s status=%s cards=%s detail=%s',
                     result.store, result.status, len(result.products), result.detail or '-')
    except Exception as exc:
        log.error('PROVIDER_CHECK failed: %s', type(exc).__name__)


@asynccontextmanager
async def lifespan(app):
    token,dsn,endpoint,secret=configuration()
    storage=await PostgresStorage.connect(dsn)
    service=SearchService(browser=BrowserRenderer())
    bot=Bot(token,default=DefaultBotProperties(parse_mode='HTML',link_preview=LinkPreviewOptions(is_disabled=True)))
    dp=Dispatcher()
    dp.include_router(BotApp(service,storage).router)
    app.state.storage=storage
    app.state.bot=bot
    app.state.dispatcher=dp
    app.state.secret=secret
    task=None
    diagnostic_task=None
    try:
        await bot.set_webhook(endpoint,secret_token=secret,allowed_updates=['message','callback_query'],drop_pending_updates=False)
        task=asyncio.create_task(process_queue(app))
        app.state.worker=task
        if os.getenv("PROVIDER_DIAGNOSTICS", "0") == "1":
            diagnostic_task=asyncio.create_task(provider_diagnostics(service))
        log.info('PriceHunter webhook and PostgreSQL ready')
        yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        if diagnostic_task:
            diagnostic_task.cancel()
            with suppress(asyncio.CancelledError):
                await diagnostic_task
        # Do not delete webhook: the replacement deployment uses the same URL.
        await bot.session.close()
        await service.close()
        await storage.close()


app=FastAPI(title='PriceHunter UZ',version='1.4.0',lifespan=lifespan)


@app.get('/')
async def root():
    return {'status':'ok','service':'PriceHunter UZ','mode':'webhook','version':'1.4.0'}


@app.get('/health')
async def health(request:Request):
    try:
        await request.app.state.storage.health()
        if request.app.state.worker.done():
            raise RuntimeError('worker stopped')
    except Exception:
        raise HTTPException(503,'Not ready')
    return {'status':'healthy','database':'connected','telegram':'webhook'}


@app.post('/webhook')
async def webhook(request:Request):
    provided=request.headers.get('X-Telegram-Bot-Api-Secret-Token','')
    if not hmac.compare_digest(provided,request.app.state.secret):
        raise HTTPException(403,'Invalid webhook secret')
    body=bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body)>1_000_000:
            raise HTTPException(413,'Update too large')
    try:
        update=Update.model_validate_json(bytes(body))
    except ValidationError:
        raise HTTPException(400,'Invalid update')
    # Acknowledge only after PostgreSQL commits; process long searches separately.
    await request.app.state.storage.enqueue(update.update_id,bytes(body).decode())
    return {'ok':True}
