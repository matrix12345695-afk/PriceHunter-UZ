from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.async_api import (
    BrowserContext,
    Page,
    Request,
    Response,
)

from .config import (
    HTML_DIR,
    MAX_BODY_SIZE,
    REQUEST_DIR,
    RESPONSE_DIR,
    SCREENSHOT_DIR,
)

from .filters import (
    get_score,
    is_interesting_request,
)

from .utils import (
    ensure_directory,
    save_json,
    save_text,
)


class Recorder:
    """
    Recorder v3

    Записывает:

    • Requests
    • Responses
    • GraphQL
    • HTML
    • Cookies
    • Screenshot
    """

    def __init__(self):

        self.counter = 0

        self.requests: list[dict[str, Any]] = []

        self.responses: list[dict[str, Any]] = []

        ensure_directory(REQUEST_DIR)
        ensure_directory(RESPONSE_DIR)
        ensure_directory(HTML_DIR)
        ensure_directory(SCREENSHOT_DIR)

    # ==========================================================
    # PRIVATE
    # ==========================================================

    def _next_id(self) -> int:

        self.counter += 1

        return self.counter

    # ==========================================================
    # REQUEST
    # ==========================================================

    async def record_request(
        self,
        request: Request,
    ) -> None:

        if not is_interesting_request(request):
            return

        request_id = self._next_id()

        item = {
            "id": request_id,
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
            "headers": dict(request.headers),
            "content_type": request.headers.get(
                "content-type",
                "",
            ),
            "post_data": request.post_data,
            "score": get_score(request.url),
        }

        self.requests.append(item)

        save_json(
            REQUEST_DIR / f"{request_id:04d}.json",
            item,
        )

        #
        # GraphQL request
        #

        if (
            "graphql" in request.url.lower()
            and request.post_data
        ):

            save_text(
                REQUEST_DIR /
                f"{request_id:04d}_graphql.txt",
                request.post_data,
            )

    # ==========================================================
    # RESPONSE
    # ==========================================================

    async def record_response(
        self,
        response: Response,
    ) -> None:

        request = response.request

        if not is_interesting_request(request):
            return

        try:

            body = await response.body()

        except Exception:

            return

        if body is None:
            return

        if len(body) > MAX_BODY_SIZE:
            return

        content_type = (
            response.headers.get(
                "content-type",
                "",
            ).lower()
        )

        item = {
            "url": response.url,
            "status": response.status,
            "content_type": content_type,
            "headers": dict(response.headers),
        }

        self.responses.append(item)

        #
        # GraphQL response
        #

        if "graphql" in response.url.lower():

            save_text(
                RESPONSE_DIR /
                f"{len(self.responses):04d}_graphql_response.txt",
                body.decode(
                    "utf-8",
                    errors="ignore",
                ),
            )

        filename = RESPONSE_DIR / (
            f"{len(self.responses):04d}"
        )
        #
        # JSON
        #

        if "application/json" in content_type:

            try:

                obj = json.loads(
                    body.decode(
                        "utf-8",
                        errors="ignore",
                    )
                )

                save_json(
                    filename.with_suffix(".json"),
                    obj,
                )

            except Exception:

                save_text(
                    filename.with_suffix(".txt"),
                    body.decode(
                        "utf-8",
                        errors="ignore",
                    ),
                )

        #
        # HTML
        #

        elif "text/html" in content_type:

            save_text(
                HTML_DIR / (
                    f"{len(self.responses):04d}.html"
                ),
                body.decode(
                    "utf-8",
                    errors="ignore",
                ),
            )

        #
        # TEXT
        #

        elif content_type.startswith("text/"):

            save_text(
                filename.with_suffix(".txt"),
                body.decode(
                    "utf-8",
                    errors="ignore",
                ),
            )

        #
        # OTHER
        #

        else:

            try:

                save_text(
                    filename.with_suffix(".txt"),
                    body.decode(
                        "utf-8",
                        errors="ignore",
                    ),
                )

            except Exception:

                pass

    # ==========================================================
    # PAGE
    # ==========================================================

    async def save_page_html(
        self,
        page: Page,
    ) -> None:

        html = await page.content()

        save_text(
            HTML_DIR / "page.html",
            html,
        )

    # ==========================================================
    # SCREENSHOT
    # ==========================================================

    async def save_screenshot(
        self,
        page: Page,
    ) -> None:

        await page.screenshot(
            path=str(
                SCREENSHOT_DIR / "page.png"
            ),
            full_page=True,
        )

    # ==========================================================
    # COOKIES
    # ==========================================================

    async def save_cookies(
        self,
        context: BrowserContext,
    ) -> None:

        cookies = await context.cookies()

        save_json(
            RESPONSE_DIR.parent / "cookies.json",
            cookies,
        )

    # ==========================================================
    # EXPORT
    # ==========================================================

    def export_summary(
        self,
    ) -> None:

        save_json(
            RESPONSE_DIR.parent / "requests.json",
            self.requests,
        )

        save_json(
            RESPONSE_DIR.parent / "responses.json",
            self.responses,
        )

    # ==========================================================
    # INFO
    # ==========================================================

    @property
    def request_count(
        self,
    ) -> int:

        return len(
            self.requests
        )

    @property
    def response_count(
        self,
    ) -> int:

        return len(
            self.responses
        )