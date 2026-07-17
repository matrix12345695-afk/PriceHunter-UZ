from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from playwright.async_api import Response

from ..config import (
    HTML_DIR,
    MAX_BODY_SIZE,
    RESPONSE_DIR,
)

from ..filters import (
    is_interesting_request,
)

from ..models import (
    Protocol,
    ResponseInfo,
)

from ..utils import (
    ensure_directory,
    save_json,
    save_text,
)

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class ResponseCapture(CapturePlugin):
    """
    Capture HTTP Response.

    Отвечает исключительно
    за сохранение ответов сервера.

    Не анализирует данные.

    Не определяет Search API.

    Не определяет Product API.

    Только Capture.
    """

    @property
    def name(self) -> str:
        return "response"

    def __init__(self) -> None:

        self.responses: list[ResponseInfo] = []

        ensure_directory(RESPONSE_DIR)
        ensure_directory(HTML_DIR)

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def detect_protocol(
        response: Response,
    ) -> Protocol:

        url = response.url.lower()

        if "graphql" in url:
            return Protocol.GRAPHQL

        request = response.request

        if request.method.upper() in {
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return Protocol.REST

        return Protocol.UNKNOWN

    # ==========================================================
    # RESPONSE
    # ==========================================================

    async def on_response(
        self,
        response: Response,
    ) -> None:

        request = response.request

        if not is_interesting_request(request):
            return

        try:

            body = await response.body()

        except Exception as exc:

            logger.debug(
                "Unable to read body: %s",
                exc,
            )

            return

        if body is None:
            return

        if len(body) > MAX_BODY_SIZE:

            logger.debug(
                "Skip large response: %s (%d bytes)",
                response.url,
                len(body),
            )

            return

        protocol = self.detect_protocol(
            response,
        )

        content_type = (
            response.headers.get(
                "content-type",
                "",
            ).lower()
        )

        info = ResponseInfo(
            url=response.url,
            status=response.status,
            headers=dict(response.headers),
            content_type=content_type,
            body=body.decode(
                "utf-8",
                errors="ignore",
            ),
            protocol=protocol,
        )

        self.responses.append(info)

        logger.debug(
            "[%03d] %s %s",
            len(self.responses),
            response.status,
            response.url,
        )

        filename = (
            RESPONSE_DIR
            / f"{len(self.responses):04d}"
        )

        #
        # GraphQL
        #

        if protocol == Protocol.GRAPHQL:

            save_text(
                filename.with_name(
                    filename.name
                    + "_graphql_response.txt"
                ),
                info.body,
            )

            try:

                payload = json.loads(
                    info.body
                )

                save_json(
                    filename.with_name(
                        filename.name
                        + "_graphql.json"
                    ),
                    payload,
                )

            except Exception:

                logger.debug(
                    "GraphQL response isn't JSON."
                )

        #
        # JSON
        #

        if "application/json" in content_type:

            try:

                obj = json.loads(
                    info.body,
                )

                save_json(
                    filename.with_suffix(
                        ".json"
                    ),
                    obj,
                )

                return

            except Exception:

                save_text(
                    filename.with_suffix(
                        ".txt"
                    ),
                    info.body,
                )

                return
        #
        # HTML
        #

        if "text/html" in content_type:

            save_text(
                HTML_DIR / (
                    f"{len(self.responses):04d}.html"
                ),
                info.body,
            )

            return

        #
        # TEXT
        #

        if content_type.startswith("text/"):

            save_text(
                filename.with_suffix(".txt"),
                info.body,
            )

            return

        #
        # XML
        #

        if (
            "xml" in content_type
            or "svg" in content_type
        ):

            save_text(
                filename.with_suffix(".xml"),
                info.body,
            )

            return

        #
        # JavaScript
        #

        if (
            "javascript" in content_type
            or "ecmascript" in content_type
        ):

            save_text(
                filename.with_suffix(".js"),
                info.body,
            )

            return

        #
        # CSS
        #

        if "text/css" in content_type:

            save_text(
                filename.with_suffix(".css"),
                info.body,
            )

            return

        #
        # Binary / Other
        #

        try:

            save_text(
                filename.with_suffix(".txt"),
                info.body,
            )

        except Exception:

            logger.debug(
                "Unsupported response: %s",
                response.url,
            )

    # ==========================================================
    # Lifecycle
    # ==========================================================

    async def startup(
        self,
    ) -> None:

        logger.info(
            "ResponseCapture started."
        )

    async def shutdown(
        self,
    ) -> None:

        logger.info(
            "Captured %d responses.",
            len(self.responses),
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @property
    def count(
        self,
    ) -> int:

        return len(
            self.responses
        )

    def clear(
        self,
    ) -> None:

        self.responses.clear()

    def get_json(
        self,
    ) -> list[dict[str, Any]]:

        return [
            response.to_dict()
            for response in self.responses
        ]

    def find_by_status(
        self,
        status: int,
    ) -> list[ResponseInfo]:

        return [
            response
            for response in self.responses
            if response.status == status
        ]

    def find_by_protocol(
        self,
        protocol: Protocol,
    ) -> list[ResponseInfo]:

        return [
            response
            for response in self.responses
            if response.protocol == protocol
        ]

    def graphql(
        self,
    ) -> list[ResponseInfo]:

        return self.find_by_protocol(
            Protocol.GRAPHQL
        )

    def rest(
        self,
    ) -> list[ResponseInfo]:

        return self.find_by_protocol(
            Protocol.REST
        )

    def success(
        self,
    ) -> list[ResponseInfo]:

        return [
            response
            for response in self.responses
            if response.is_success()
        ]

    def failed(
        self,
    ) -> list[ResponseInfo]:

        return [
            response
            for response in self.responses
            if not response.is_success()
        ]

    def summary(
        self,
    ) -> dict[str, int]:

        graphql = len(
            self.graphql()
        )

        rest = len(
            self.rest()
        )

        success = len(
            self.success()
        )

        failed = len(
            self.failed()
        )

        return {
            "responses": len(self.responses),
            "graphql": graphql,
            "rest": rest,
            "success": success,
            "failed": failed,
        }