import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock
import httpx
import pytest
from pricehunter.models import amount, Product, Result, safe_url
from pricehunter.providers import MARKETS, parse_olcha, parse_html, search_market, SchemaChanged
from pricehunter.service import SearchService, select_products, normalize
from pricehunter.storage import Storage
from pricehunter.bot import BotApp
from pricehunter.ui import page_view

FIX = Path(__file__).parent / 'fixtures'

@pytest.mark.parametrize('raw,expected', [('1 234 567',1234567),('0',None),('-100',None),('NaN',None),('12.9',None),('1\u00a0000',1000),(True,None)])
def test_price(raw,expected):
    assert amount(raw)==expected


def test_olcha_live_fixture():
    products = parse_olcha(json.loads((FIX/'olcha.json').read_text()))
    assert len(products) >= 10
    assert products[0].price == 18399000
    assert all(p.currency=='UZS' and p.price and safe_url(p.url,'olcha.uz') for p in products)
    with pytest.raises(SchemaChanged):parse_olcha({'captcha':True})


def test_mediapark_full_price():
    nodes = json.loads((FIX/'mediapark.json').read_text())
    script = '<script>self.__next_f.push(' + json.dumps([1,'7e:'+json.dumps(nodes)]) + ')</script>'
    products = parse_html(script,MARKETS['mediapark'])
    assert len(products)>5
    assert products[0].price == int(nodes[0]['price_without_installment'])
    assert products[0].price != int(nodes[0]['installment_monthly_price'])


def test_jsonld_untrusted_urls_and_aggregate_price():
    nodes=[{'@type':'Product','name':'Valid','url':'/product/1','offers':{'lowPrice':100,'priceCurrency':'UZS'}},
           {'@type':'Product','name':'Bad','url':'https://evil.com/product','offers':{'price':1}}]
    p=parse_html('<script type="application/ld+json">'+json.dumps(nodes)+'</script>',MARKETS['asaxiy'])
    assert len(p)==1 and p[0].price is None
    assert not safe_url('https://asaxiy.uz.evil.com/x','asaxiy.uz')


@pytest.mark.asyncio
async def test_failure_isolation_and_cache():
    calls=[]
    def handler(request):
        calls.append(str(request.url))
        if request.url.host=='mobile.olcha.uz':
            return httpx.Response(200,json=json.loads((FIX/'olcha.json').read_text()))
        return httpx.Response(403)
    service=SearchService(httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    results,cached=await service.search('iphone',['olcha','asaxiy'])
    assert {r.store:r.status for r in results}=={'olcha':'ok','asaxiy':'blocked'}
    assert not cached
    again,cached=await service.search('iphone',['asaxiy','olcha'])
    assert cached and len(calls)==2
    await service.close()


@pytest.mark.asyncio
async def test_network_timeout_and_retry():
    count=0
    def handler(request):
        nonlocal count
        count+=1
        raise httpx.ReadTimeout('test',request=request)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        r=await search_market(client,MARKETS['olcha'],'test')
    assert r.status=='timeout' and count==2


def test_budget_currency_and_relevance():
    products=[Product('olcha','iPhone', 'https://olcha.uz/1', 100),
              Product('olcha','iPhone USD', 'https://olcha.uz/2', 1,'USD'),
              Product('olcha','Чехол iPhone','https://olcha.uz/3',10),
              Product('olcha','Other','https://olcha.uz/4',2)]
    result=[Result('olcha','ok',products)]
    assert [p.price for p in select_products(result,'iphone',50)]==[10]
    assert select_products(result,'iphone')[0].title=='iPhone'
    assert select_products(result,'iphone',sort='price')[-1].currency=='USD'


def test_database_persistence_and_user_isolation(tmp_path):
    path=tmp_path/'db.sqlite3'
    db=Storage(path)
    p=Product('olcha','phone','https://olcha.uz/phone',120)
    db.favorite(1,p)
    db.update(1,budget=500)
    for n in range(15):db.remember(1,f'query {n}')
    assert len(db.history(1))==10 and db.favorites(2)==[]
    db.close();db=Storage(path)
    assert db.settings(1)['budget']==500 and db.favorites(1)[0][1]==p
    db.clear(2)
    assert len(db.favorites(1))==1
    db.clear(1)
    assert not db.favorites(1) and not db.history(1)
    db.close()


def test_ui_escape_limits_and_callback_lengths():
    p=Product('olcha','<b>&Phone</b>'*15,'https://olcha.uz/p',100)
    session=dict(query='<script>',items=[p]*40,results=[Result(k,'blocked') for k in MARKETS],cached=True)
    text,markup=page_view(session,'1234567890',0)
    assert '&lt;script&gt;' in text and len(text)<4096
    assert all(len(b.callback_data.encode())<=64 for row in markup.inline_keyboard for b in row if b.callback_data)


@pytest.mark.asyncio
async def test_bot_search_and_cross_user_callback(tmp_path):
    db=Storage(tmp_path/'db.sqlite3')
    service=AsyncMock()
    service.search.return_value=([Result('olcha','ok',[Product('olcha','phone','https://olcha.uz/p',100)])],False)
    app=BotApp(service,AsyncStorage(db))
    m=AsyncMock()
    await app.search(m,1,'phone')
    assert 1 not in app.busy and len(app.sessions)==1
    sid=next(iter(app.sessions))
    c=AsyncMock();c.data=f'save:{sid}:0';c.from_user.id=2
    await app.callback(c)
    assert not db.favorites(2)
    c.from_user.id=1
    await app.callback(c)
    assert len(db.favorites(1))==1
    db.close()


@pytest.mark.asyncio
async def test_old_card_keeps_product_after_sort(tmp_path):
    db=Storage(tmp_path/'db.sqlite3');app=BotApp(AsyncMock(),AsyncStorage(db))
    p1=Product('olcha','phone A','https://olcha.uz/a',200)
    p2=Product('olcha','phone B','https://olcha.uz/b',100)
    app.sessions['old']=dict(user=1,query='phone',results=[Result('olcha','ok',[p1,p2])],
        items=[p1,p2],sort='relevance',budget=None,cached=False,created=time.monotonic())
    c=AsyncMock();c.from_user.id=1;c.data='sort:old:0'
    await app.callback(c)
    assert app.sessions['old']['items'][0]==p1
    c.data='save:old:0';await app.callback(c)
    assert db.favorites(1)[0][1]==p1
    db.close()


def test_asaxiy_live_full_price_and_russian_name():
    items=parse_html((FIX/'asaxiy.html').read_text(),MARKETS['asaxiy'])
    assert items[0].title=='Смартфон iPhone 13 128GB Midnight. Новый.'
    assert items[0].price==6999000


class AsyncStorage:
    def __init__(self,storage):self.storage=storage
    def __getattr__(self,name):
        async def call(*args,**kwargs):
            return getattr(self.storage,name)(*args,**kwargs)
        return call
