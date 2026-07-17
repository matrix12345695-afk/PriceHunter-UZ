from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from playwright.async_api import (
    BrowserContext,
    Request,
    Response,
)

logger = logging.getLogger(__name__)


class AuthCapture:
    """
    Capture plugin.

    Собирает все данные, связанные с авторизацией.
    Пока ничего не анализирует.
    """

    name = "AuthCapture"

    def __init__(self):

        self.output = Path("research/auth")

        self.requests = self.output / "requests"
        self.responses = self.output / "responses"
        self.cookies = self.output / "cookies"

        self.requests.mkdir(parents=True, exist_ok=True)
        self.responses.mkdir(parents=True, exist_ok=True)
        self.cookies.mkdir(parents=True, exist_ok=True)

        self.context: BrowserContext | None = None

        self.counter = 0

        self.timeline = []

        #
        # Request -> ID
        #
        self.request_ids: dict[Request, int] = {}

    async def startup(self):
        logger.info("[AuthCapture] startup")

    async def shutdown(self):
        logger.info("[AuthCapture] shutdown")

    async def on_context_created(
        self,
        context: BrowserContext,
    ):
        self.context = context

    async def on_page_created(self, page):
        pass

    async def on_page_loaded(self, page):
        pass

    async def on_request(
        self,
        request: Request,
    ):

        self.counter += 1

        request_id = self.counter

        self.request_ids[request] = request_id

        try:
            headers = await request.all_headers()
        except Exception:
            headers = {}

        filename = self.requests / f"{request_id:05}.json"

        data = {
            "id": request_id,
            "time": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "headers": headers,
            "body": request.post_data,
        }

        filename.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.timeline.append(
            {
                "id": request_id,
                "type": "request",
                "url": request.url,
            }
        )

    async def on_response(
        self,
        response: Response,
    ):

        request = response.request

        request_id = self.request_ids.get(request)

        if request_id is None:
            return

        try:
            headers = await response.all_headers()
        except Exception:
            headers = {}

        filename = self.responses / f"{request_id:05}.json"

        data = {
            "id": request_id,
            "time": datetime.now().isoformat(),
            "status": response.status,
            "url": response.url,
            "headers": headers,
        }

        filename.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.timeline.append(
            {
                "id": request_id,
                "type": "response",
                "status": response.status,
                "url": response.url,
            }
        )

    async def on_finished(self):

        if self.context is not None:

            try:

                cookies = await self.context.cookies()

                (
                    self.cookies / "cookies.json"
                ).write_text(
                    json.dumps(
                        cookies,
                        indent=4,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

            except Exception as exc:

                logger.warning(
                    "Unable to save cookies: %s",
                    exc,
                )

        (
            self.output / "timeline.json"
        ).write_text(
            json.dumps(
                self.timeline,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        logger.info(
            "[AuthCapture] Saved %d requests",
            self.counter,
        )