from playwright.sync_api import sync_playwright


def log_request(request):
    if request.resource_type in ("fetch", "xhr"):
        print("=" * 80)
        print(request.method, request.url)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.on("request", log_request)

    page.goto("https://uzum.uz/ru/search?query=iphone")

    input("Нажми Enter после полной загрузки...")

    browser.close()