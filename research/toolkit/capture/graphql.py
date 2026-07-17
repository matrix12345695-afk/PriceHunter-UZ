from __future__ import annotations

import json
import logging

from playwright.async_api import (
    Request,
    Response,
)

from ..config import REQUEST_DIR
from ..models import (
    GraphQLOperation,
    Protocol,
)
from ..utils import (
    ensure_directory,
    save_json,
    save_text,
)

from .plugin import CapturePlugin


logger = logging.getLogger(__name__)


class GraphQLCapture(CapturePlugin):
    """
    Capture GraphQL.

    Отвечает только за GraphQL.

    Сохраняет:

        • operationName

        • query

        • variables

        • response

    Ничего не знает
    про HTML, Cookies,
    Screenshot и т.д.
    """

    @property
    def name(self) -> str:
        return "graphql"

    def __init__(self) -> None:

        ensure_directory(REQUEST_DIR)

        self.operations: list[GraphQLOperation] = []

        #
        # operationName -> GraphQLOperation
        #

        self._map: dict[str, GraphQLOperation] = {}

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _is_graphql(
        request: Request,
    ) -> bool:

        if "graphql" in request.url.lower():
            return True

        body = request.post_data or ""

        return (
            "operationName" in body
            or '"query"' in body
        )

    # ==========================================================
    # Request
    # ==========================================================

    async def on_request(
        self,
        request: Request,
    ) -> None:

        if not self._is_graphql(request):
            return

        if not request.post_data:
            return

        try:

            payload = json.loads(
                request.post_data
            )

        except Exception:

            logger.debug(
                "GraphQL payload isn't JSON."
            )

            return

        operation = GraphQLOperation(

            operation_name=payload.get(
                "operationName",
                "Unknown",
            ),

            query=payload.get(
                "query",
                "",
            ),

            variables=payload.get(
                "variables",
                {},
            ),

            endpoint=request.url,

            headers=dict(
                request.headers
            ),
        )

        self.operations.append(
            operation
        )

        self._map[
            operation.operation_name
        ] = operation

        prefix = (
            f"{len(self.operations):04d}"
        )

        save_text(
            REQUEST_DIR
            / f"{prefix}.graphql",
            operation.query,
        )

        save_json(
            REQUEST_DIR
            / f"{prefix}_variables.json",
            operation.variables,
        )

        save_text(
            REQUEST_DIR
            / f"{prefix}_operation.txt",
            operation.operation_name,
        )

        logger.info(
            "GraphQL: %s",
            operation.operation_name,
        )

    # ==========================================================
    # Response
    # ==========================================================

    async def on_response(
        self,
        response: Response,
    ) -> None:

        request = response.request

        if not self._is_graphql(request):
            return

        try:

            body = await response.body()

        except Exception:

            return

        try:

            obj = json.loads(
                body.decode(
                    "utf-8",
                    errors="ignore",
                )
            )

        except Exception:

            return

        #
        # Попытаемся определить operation
        #

        operation_name = None

        if request.post_data:

            try:

                payload = json.loads(
                    request.post_data
                )

                operation_name = payload.get(
                    "operationName"
                )

            except Exception:

                pass

        if (
            operation_name
            and operation_name
            in self._map
        ):

            self._map[
                operation_name
            ].response = obj

        prefix = (
            f"{len(self.operations):04d}"
        )

        save_json(
            REQUEST_DIR
            / f"{prefix}_response.json",
            obj,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def find(
        self,
        operation: str,
    ) -> GraphQLOperation | None:

        return self._map.get(
            operation
        )

    @property
    def count(
        self,
    ) -> int:

        return len(
            self.operations
        )

    def summary(
        self,
    ) -> dict:

        return {

            "graphql": self.count,

            "operations": [
                op.operation_name
                for op
                in self.operations
            ],
        }

    async def startup(
        self,
    ) -> None:

        logger.info(
            "GraphQLCapture started."
        )

    async def shutdown(
        self,
    ) -> None:

        logger.info(
            "Captured %d GraphQL operations.",
            self.count,
        )