import asyncio

from app.providers.uzum import UzumProvider


async def main():

    provider = UzumProvider()

    data = await provider.search_raw("iphone")

    print(data)


asyncio.run(main())
