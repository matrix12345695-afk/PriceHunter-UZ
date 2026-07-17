import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()

        await page.goto(
            "https://olcha.uz/ru",
            wait_until="domcontentloaded"
        )

        await page.wait_for_timeout(3000)

        # Кликаем по поиску
        await page.get_by_role(
            "textbox",
            name="Поиск по каталогу"
        ).click()

        await page.wait_for_timeout(2000)

        # Показываем все input
        inputs = await page.locator("input").evaluate_all(
            """
(elements) => elements.map(e => ({
    placeholder: e.placeholder,
    readonly: e.readOnly,
    disabled: e.disabled,
    type: e.type,
    id: e.id,
    className: e.className
}))
"""
        )

        print()

        print("=" * 80)

        for i in inputs:
            print(i)

        print("=" * 80)

        input("Enter...")

        await browser.close()


asyncio.run(main())