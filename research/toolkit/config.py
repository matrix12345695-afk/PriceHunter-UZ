from pathlib import Path

# ==============================================================================
# PROJECT
# ==============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = ROOT_DIR / "reports"

REQUEST_DIR = REPORT_DIR / "requests"

RESPONSE_DIR = REPORT_DIR / "responses"

HTML_DIR = REPORT_DIR / "html"

SCREENSHOT_DIR = REPORT_DIR / "screenshots"

COOKIE_DIR = REPORT_DIR / "cookies"

# ==============================================================================
# PLAYWRIGHT
# ==============================================================================

HEADLESS = False

BROWSER_TIMEOUT = 30000

WAIT_AFTER_LOAD = 5

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)

# ==============================================================================
# FILTERS
# ==============================================================================

ALLOWED_RESOURCE_TYPES = {
    "fetch",
    "xhr",
}

INTERESTING_KEYWORDS = {
    "api",
    "graphql",
    "search",
    "catalog",
    "product",
    "products",
    "offer",
    "offers",
    "item",
    "items",
    "price",
    "prices",
}

IGNORE_DOMAINS = {
    "facebook.com",
    "doubleclick.net",
    "googletagmanager.com",
    "google-analytics.com",
    "googleads.g.doubleclick.net",
    "mc.yandex.ru",
    "analytics.google.com",
}

MAX_BODY_SIZE = 1_000_000