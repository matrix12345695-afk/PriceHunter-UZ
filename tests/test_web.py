import json
from unittest.mock import AsyncMock, Mock
import httpx
import pytest
from pricehunter.web import app, configuration
from pricehunter.postgres import normalize_dsn


def test_environment_compatibility(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN','123456:TEST_TOKEN')
    monkeypatch.setenv('DATABASE_URL','postgresql+asyncpg://host/db')
    monkeypatch.setenv('WEBHOOK_URL','https://example.onrender.com/webhook')
    monkeypatch.delenv('WEBHOOK_SECRET',raising=False)
    assert configuration()[2]=='https://example.onrender.com/webhook'
    assert len(configuration()[3])==64
    monkeypatch.setenv('WEBHOOK_SECRET','existing-secret')
    assert configuration()[3]=='existing-secret'
    assert normalize_dsn('postgresql+asyncpg://host/db')=='postgresql://host/db'


@pytest.mark.asyncio
async def test_webhook_auth_validation_and_persistence():
    app.state.secret='test-secret'
    app.state.storage=AsyncMock()
    transport=httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,base_url='https://test') as c:
        r=await c.post('/webhook',json={'update_id':123})
        assert r.status_code==403
        app.state.storage.enqueue.assert_not_called()
        headers={'X-Telegram-Bot-Api-Secret-Token':'test-secret'}
        r=await c.post('/webhook',json={'no':'update_id'},headers=headers)
        assert r.status_code==400
        r=await c.post('/webhook',json={'update_id':123},headers=headers)
        assert r.status_code==200
        app.state.storage.enqueue.assert_awaited_once()
        assert app.state.storage.enqueue.call_args.args[0]==123
        r=await c.post('/webhook',content=b' '*1_000_001,headers=headers)
        assert r.status_code==413


@pytest.mark.asyncio
async def test_health_checks_real_storage_and_worker():
    app.state.storage=AsyncMock()
    app.state.worker=Mock();app.state.worker.done.return_value=False
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://test') as c:
        assert (await c.get('/health')).status_code==200
        app.state.storage.health.side_effect=RuntimeError('DB down')
        assert (await c.get('/health')).status_code==503


@pytest.mark.asyncio
async def test_worker_marks_success_only_after_processing():
    import asyncio
    from types import SimpleNamespace
    from pricehunter.web import process_queue
    storage=AsyncMock()
    storage.next_update.side_effect=[{'update_id':1,'payload':json.dumps({'update_id':1}),'attempts':1},asyncio.CancelledError()]
    dispatcher=AsyncMock()
    fake=SimpleNamespace(state=SimpleNamespace(storage=storage,dispatcher=dispatcher,bot=Mock()))
    with pytest.raises(asyncio.CancelledError):await process_queue(fake)
    dispatcher.feed_update.assert_awaited_once()
    storage.finish_update.assert_awaited_once_with(1,'done')
