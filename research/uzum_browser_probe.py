import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
        )

        page = await browser.new_page()

        async def log_response(response):

            url = response.url

            if (
                "api" in url.lower()
                or "graphql" in url.lower()
                or "search" in url.lower()
                or "catalog" in url.lower()
            ):
                print("=" * 80)
                print(response.status)
                print(url)

                try:
                    print(await response.text())
                except Exception:
                    pass

        page.on("response", log_response)

        await page.goto(
            "https://uzum.uz",
            wait_until="networkidle",
        )

        await page.fill(
            'input[type="search"]',
            "iphone",
        )

        await page.keyboard.press("Enter")

        await page.wait_for_timeout(10000)

        input("Нажми Enter после просмотра браузера...")

        await browser.close()


asyncio.run(main())
