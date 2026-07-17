import asyncio
import httpx


async def main():
    url = (
        "https://mobile.olcha.uz/api/v2/"
        "multi-search/products/iphone"
        "?category_id=&page=1"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": "https://olcha.uz/",
        "Origin": "https://olcha.uz",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=headers)

        print("STATUS:", r.status_code)
        print()
        print(r.text[:2000])


asyncio.run(main())