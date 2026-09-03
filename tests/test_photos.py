import json
from unittest.mock import AsyncMock
import pytest
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.methods import SendPhoto
from pricehunter.models import Product
from pricehunter.providers import parse_olcha, parse_idea, parse_texnomart, parse_mediapark, image_url
from pricehunter.bot import BotApp
from pricehunter.ui import card, page_view, title_text, product_button
from pathlib import Path
FIX=Path(__file__).parent/'fixtures'

@pytest.mark.parametrize('file,parser',[('olcha.json',parse_olcha),('idea.json',parse_idea),('texnomart.json',parse_texnomart),('mediapark-api.json',parse_mediapark)])
def test_real_photos_survive_parsing_and_serialization(file,parser):
    products=parser(json.loads((FIX/file).read_text()))
    assert products and all(p.image.startswith('https://') for p in products)
    assert Product(**products[0].to_dict()).image==products[0].image


def test_legacy_favorites_without_image_still_load():
    p=Product(**dict(store='olcha',title='phone',url='https://olcha.uz/p',price=100))
    assert p.image==''


def test_mediapark_uses_sale_price_and_public_url():
    products=parse_mediapark(json.loads((FIX/'mediapark-api.json').read_text()))
    assert len(products)==6
    assert products[0].price==19402000
    assert '/products/view/' in products[0].url


def test_image_url_validation():
    assert image_url('https://cdn.mediapark.uz/a.webp')
    assert not image_url('https://olcha.uz.evil.com/a.jpg')
    assert not image_url('http://127.0.0.1/a')
    assert not image_url('https://user:password@olcha.uz/a')


def test_names_and_real_product_buttons():
    p=Product('olcha','  IPHONE  17 Pro Max 512GB ','https://olcha.uz/p',18000000)
    assert title_text(p.title)=='iPhone 17 Pro Max 512GB'
    assert 'iPhone' in product_button(p,0) and '18 000 000' in product_button(p,0)
    assert 'Открыть карточку' not in product_button(p,0)


@pytest.mark.asyncio
async def test_card_sent_as_photo_with_caption_and_buttons():
    app=BotApp(AsyncMock(),AsyncMock());message=AsyncMock()
    p=Product('olcha','Vacuum G9+','https://olcha.uz/p',2237500,image='https://olcha.uz/p.jpg')
    await app.send_product(message,p,None)
    message.answer_photo.assert_awaited_once_with(photo=p.image,caption=card(p),reply_markup=None)
    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_rejected_photo_falls_back_without_losing_product(monkeypatch):
    monkeypatch.setattr("pricehunter.photos.download_photo", AsyncMock(side_effect=ValueError("image unavailable")))
    app=BotApp(AsyncMock(),AsyncMock());message=AsyncMock()
    p=Product('olcha','Vacuum G9+','https://olcha.uz/p',2237500,image='https://olcha.uz/p.jpg')
    message.answer_photo.side_effect=TelegramBadRequest(method=SendPhoto(chat_id=1,photo=p.image),message='wrong type of the web page content')
    await app.send_product(message,p,None)
    assert 'Vacuum G9+' in message.answer.call_args.args[0]
    assert 'Фото сейчас недоступно' in message.answer.call_args.args[0]


def test_webp_photo_converted_to_telegram_jpeg():
    from PIL import Image
    from io import BytesIO
    from pricehunter.photos import to_jpeg
    source=BytesIO()
    Image.new('RGBA',(2000,1000),(255,0,0,128)).save(source,format='WEBP')
    result=Image.open(BytesIO(to_jpeg(source.getvalue())))
    assert result.format=='JPEG' and result.size==(1600,800) and result.mode=='RGB'


@pytest.mark.asyncio
async def test_url_rejection_uses_file_upload(monkeypatch):
    from aiogram.types import BufferedInputFile
    file=BufferedInputFile(b'jpeg',filename='product.jpg')
    monkeypatch.setattr('pricehunter.photos.download_photo',AsyncMock(return_value=file))
    app=BotApp(AsyncMock(),AsyncMock());message=AsyncMock()
    p=Product('olcha','Vacuum G9+','https://olcha.uz/p',2237500,image='https://olcha.uz/p.webp')
    message.answer_photo.side_effect=[TelegramBadRequest(method=SendPhoto(chat_id=1,photo=p.image),message='failed to get HTTP URL content'),None]
    await app.send_product(message,p,None)
    assert message.answer_photo.await_count==2
    assert message.answer_photo.call_args.kwargs['photo'] is file
    message.answer.assert_not_called()
