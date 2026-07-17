import asyncio

from app.providers.olcha import OlchaProvider


async def main():

    provider = OlchaProvider()

    products = await provider.search("iphone")

    print()

    print("=" * 70)

    print(f"Найдено: {len(products)}")

    print("=" * 70)

    for product in products[:10]:

        print(product.title)
        print(product.price)
        print(product.url)
        print()

asyncio.run(main())