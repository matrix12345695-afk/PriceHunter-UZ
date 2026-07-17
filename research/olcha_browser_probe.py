import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


SEARCH_URL = "https://olcha.uz/ru/search?search=iphone"


async def main():
    Path("research/samples").mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Пока показываем окно браузера
        )

        page = await browser.new_page()

        print("Открываем Olcha...")

        await page.goto(
            SEARCH_URL,
            wait_until="networkidle",
            timeout=60000,
        )

        # Небольшая пауза на случай ленивой загрузки
        await page.wait_for_timeout(3000)

        html = await page.content()

        Path("research/samples/olcha_rendered.html").write_text(
            html,
            encoding="utf-8",
        )

        await page.screenshot(
            path="research/samples/olcha.png",
            full_page=True,
        )

        print("✔ HTML сохранён")
        print("✔ Скриншот сохранён")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())