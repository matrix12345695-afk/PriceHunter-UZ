import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def main():

    Path("research").mkdir(exist_ok=True)

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
        )

        page = await browser.new_page()

        responses = []

        async def on_response(response):

            if "mobile.olcha.uz/api" not in response.url:
                return

            print(
                f"{response.status} "
                f"{response.request.method} "
                f"{response.url}"
            )

            try:
                body = await response.json()
            except Exception:
                try:
                    body = await response.text()
                except Exception:
                    body = None

            responses.append(
                {
                    "url": response.url,
                    "method": response.request.method,
                    "status": response.status,
                    "body": body,
                }
            )

        page.on("response", on_response)

        await page.goto(
            "https://olcha.uz/ru",
            wait_until="domcontentloaded",
        )

        await page.wait_for_timeout(3000)

        # открыть поиск
        await page.locator("#MSearch-entry").click()

        await page.wait_for_timeout(1000)

        # настоящий input
        search = page.locator('input.multi-input.form-search')

        await search.click()

        await search.fill("iphone")

        await page.wait_for_timeout(5000)

        Path(
            "research/api_responses.json"
        ).write_text(
            json.dumps(
                responses,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print("\n===============================")
        print("ГОТОВО!")
        print(f"Получено ответов: {len(responses)}")
        print("===============================\n")

        input("Enter...")

        await browser.close()


asyncio.run(main())