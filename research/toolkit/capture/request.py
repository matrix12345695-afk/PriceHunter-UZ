from __future__ import annotations

import json
import logging
from pathlib import Path

from playwright.async_api import Request

from ..models import (
    Protocol,
    RequestInfo,
)
from ..filters import (
    get_score,
    is_interesting_request,
)
from ..utils import (
    ensure_directory,
    save_json,
    save_text,
)
from ..config import REQUEST_DIR

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class RequestCapture(CapturePlugin):
    """
    Capture HTTP Request.

    Отвечает исключительно за запись запросов.

    Не знает ничего о:
        • HTML
        • Cookies
        • Screenshot
        • Analyzer
        • Reporter
    """

    @property
    def name(self) -> str:
        return "request"

    def __init__(self) -> None:

        self._counter = 0

        self.requests: list[RequestInfo] = []

        ensure_directory(REQUEST_DIR)

    # ---------------------------------------------------------

    def _next_id(self) -> int:

        self._counter += 1

        return self._counter

    # ---------------------------------------------------------

    @staticmethod
    def detect_protocol(
        request: Request,
    ) -> Protocol:

        url = request.url.lower()

        if "graphql" in url:
            return Protocol.GRAPHQL

        if request.method.upper() in {
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return Protocol.REST

        return Protocol.UNKNOWN

    # ---------------------------------------------------------

    async def on_request(
        self,
        request: Request,
    ) -> None:

        if not is_interesting_request(request):
            return

        request_id = self._next_id()

        protocol = self.detect_protocol(request)

        info = RequestInfo(
            id=request_id,
            method=request.method,
            url=request.url,
            resource_type=request.resource_type,
            headers=dict(request.headers),
            body=request.post_data,
            content_type=request.headers.get(
                "content-type",
                "",
            ),
            protocol=protocol,
        )

        self.requests.append(info)

        logger.debug(
            "[%04d] %s %s",
            request_id,
            request.method,
            request.url,
        )

        save_json(
            REQUEST_DIR / f"{request_id:04d}.json",
            {
                **info.to_dict(),
                "score": get_score(request.url),
            },
        )

        #
        # GraphQL
        #

        if (
            protocol == Protocol.GRAPHQL
            and request.post_data
        ):

            save_text(
                REQUEST_DIR
                / f"{request_id:04d}_graphql.txt",
                request.post_data,
            )

            #
            # Попробуем красиво сохранить query
            #

            try:

                payload = json.loads(
                    request.post_data
                )

                if "query" in payload:

                    save_text(
                        REQUEST_DIR
                        / f"{request_id:04d}.graphql",
                        payload["query"],
                    )

                if "variables" in payload:

                    save_json(
                        REQUEST_DIR
                        / f"{request_id:04d}_variables.json",
                        payload["variables"],
                    )

                if "operationName" in payload:

                    save_text(
                        REQUEST_DIR
                        / f"{request_id:04d}_operation.txt",
                        payload["operationName"],
                    )

            except Exception:

                logger.debug(
                    "GraphQL payload is not JSON."
                )

    # ---------------------------------------------------------

    async def startup(self) -> None:

        logger.info(
            "RequestCapture started."
        )

    async def shutdown(self) -> None:

        logger.info(
            "Captured %d requests.",
            len(self.requests),
        )