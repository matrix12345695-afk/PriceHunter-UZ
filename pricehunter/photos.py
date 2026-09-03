"""Convert supported store images if Telegram cannot import their URL."""
import asyncio
from io import BytesIO
from urllib.parse import urljoin
from PIL import Image, ImageOps
import httpx
from aiogram.types import BufferedInputFile
from .providers import image_url


def to_jpeg(data):
    with Image.open(BytesIO(data)) as image:
        if image.width * image.height > 20_000_000:
            raise ValueError('Image too large')
        image = ImageOps.exif_transpose(image)
        image.thumbnail((1600, 1600))
        rgba = image.convert('RGBA')
        rgb = Image.new('RGB', rgba.size, 'white')
        rgb.paste(rgba, mask=rgba.getchannel('A'))
        output = BytesIO()
        rgb.save(output, format='JPEG', quality=88, optimize=True)
        return output.getvalue()


async def download_photo(url):
    # No forwarding credentials, no redirects to unapproved destinations.
    async with httpx.AsyncClient(timeout=8, follow_redirects=False) as client:
        for _ in range(4):
            if not image_url(url):
                raise ValueError('Unapproved image host')
            async with client.stream('GET', url) as response:
                if response.is_redirect:
                    url = urljoin(url, response.headers.get('Location', ''))
                    continue
                response.raise_for_status()
                if not response.headers.get('content-type', '').startswith('image/'):
                    raise ValueError('Not an image')
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 8_000_000:
                        raise ValueError('Image download too large')
                jpeg = await asyncio.to_thread(to_jpeg, bytes(body))
                return BufferedInputFile(jpeg, filename='product.jpg')
    raise ValueError('Too many redirects')
