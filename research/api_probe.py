import asyncio
import httpx


async def main():
    async with httpx.AsyncClient() as client:

        urls = [
            "https://mobile.olcha.uz/api",
            "https://mobile.olcha.uz/api/products",
            "https://mobile.olcha.uz/api/search",
            "https://mobile.olcha.uz/api/v1/search",
            "https://mobile.olcha.uz/api/v1/products",
        ]

        for url in urls:
            try:
                r = await client.get(url)

                print("=" * 60)
                print(url)
                print(r.status_code)
                print(r.text[:300])

            except Exception as e:
                print(url, e)


asyncio.run(main())