import asyncio

from app.services.marketplace_manager import MarketplaceManager


async def main():

    manager = MarketplaceManager()

    products = await manager.search("iphone")

    print(f"Найдено {len(products)} товаров")

    for product in products[:5]:
        print(product.title)
        print(product.price)
        print(product.store)
        print("-" * 40)


asyncio.run(main())