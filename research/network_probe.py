import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        page = await browser.new_page()

        requests = []

        async def on_request(request):
            url = request.url

            if (
                "api" in url.lower()
                or "graphql" in url.lower()
                or "search" in url.lower()
                or "mobile.olcha" in url.lower()
            ):
                requests.append(
                    {
                        "method": request.method,
                        "url": request.url,
                    }
                )

                print(request.method, request.url)

        page.on("request", on_request)

        await page.goto(
            "https://olcha.uz/ru/search?search=iphone",
            wait_until="networkidle",
        )

        await page.wait_for_timeout(5000)

        with open(
            "research/network_requests.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                requests,
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\nНайдено запросов: {len(requests)}")

        await browser.close()


asyncio.run(main())