from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ==========================================================
# ENUMS
# ==========================================================


class Protocol(str, Enum):
    REST = "REST"
    GRAPHQL = "GRAPHQL"
    WEBSOCKET = "WEBSOCKET"
    UNKNOWN = "UNKNOWN"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ==========================================================
# REQUEST
# ==========================================================


@dataclass(slots=True)
class RequestInfo:

    id: int

    method: str

    url: str

    resource_type: str

    headers: dict[str, str] = field(default_factory=dict)

    body: str | None = None

    content_type: str = ""

    protocol: Protocol = Protocol.UNKNOWN

    def is_graphql(self) -> bool:

        return self.protocol == Protocol.GRAPHQL

    def is_rest(self) -> bool:

        return self.protocol == Protocol.REST

    def to_dict(self) -> dict[str, Any]:

        return {
            "id": self.id,
            "method": self.method,
            "url": self.url,
            "resource_type": self.resource_type,
            "headers": self.headers,
            "body": self.body,
            "content_type": self.content_type,
            "protocol": self.protocol.value,
        }


# ==========================================================
# RESPONSE
# ==========================================================


@dataclass(slots=True)
class ResponseInfo:

    url: str

    status: int

    headers: dict[str, str]

    content_type: str

    body: str = ""

    protocol: Protocol = Protocol.UNKNOWN

    def is_success(self) -> bool:

        return 200 <= self.status < 300

    def to_dict(self) -> dict[str, Any]:

        return {
            "url": self.url,
            "status": self.status,
            "headers": self.headers,
            "content_type": self.content_type,
            "protocol": self.protocol.value,
        }


# ==========================================================
# GRAPHQL
# ==========================================================


@dataclass(slots=True)
class GraphQLOperation:

    operation_name: str

    query: str

    variables: dict[str, Any]

    endpoint: str

    headers: dict[str, str]

    response: dict[str, Any] | None = None

    def has_response(self) -> bool:

        return self.response is not None

    def to_dict(self):

        return {
            "operationName": self.operation_name,
            "query": self.query,
            "variables": self.variables,
            "endpoint": self.endpoint,
        }


# ==========================================================
# REST
# ==========================================================


@dataclass(slots=True)
class RestEndpoint:

    method: str

    url: str

    status: int

    request_body: str | None = None

    response_body: str | None = None

    def to_dict(self):

        return {
            "method": self.method,
            "url": self.url,
            "status": self.status,
        }


# ==========================================================
# SECURITY
# ==========================================================


@dataclass(slots=True)
class SecurityFinding:

    severity: Severity

    title: str

    description: str

    value: str = ""

    def to_dict(self):

        return {
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "value": self.value,
        }


# ==========================================================
# SCHEMA
# ==========================================================


@dataclass(slots=True)
class SchemaField:

    name: str

    field_type: str

    nullable: bool = True

    examples: list[Any] = field(default_factory=list)

    def to_dict(self):

        return {
            "name": self.name,
            "type": self.field_type,
            "nullable": self.nullable,
            "examples": self.examples,
        }


# ==========================================================
# PROVIDER
# ==========================================================


@dataclass(slots=True)
class ProviderHint:

    name: str

    confidence: int

    score: int

    endpoint: str

    operation: str = ""

    protocol: Protocol = Protocol.UNKNOWN

    reason: str = ""

    def stars(self) -> str:

        return "★" * max(
            1,
            min(5, self.confidence),
        )

    def to_dict(self):

        return {
            "name": self.name,
            "confidence": self.confidence,
            "score": self.score,
            "endpoint": self.endpoint,
            "operation": self.operation,
            "protocol": self.protocol.value,
            "reason": self.reason,
        }


# ==========================================================
# REPORT
# ==========================================================


@dataclass(slots=True)
class AnalysisReport:

    requests: list[RequestInfo] = field(default_factory=list)

    responses: list[ResponseInfo] = field(default_factory=list)

    graphql: list[GraphQLOperation] = field(default_factory=list)

    rest: list[RestEndpoint] = field(default_factory=list)

    schema: list[SchemaField] = field(default_factory=list)

    security: list[SecurityFinding] = field(default_factory=list)

    providers: list[ProviderHint] = field(default_factory=list)

    def summary(self) -> dict[str, int]:

        return {
            "requests": len(self.requests),
            "responses": len(self.responses),
            "graphql": len(self.graphql),
            "rest": len(self.rest),
            "schema": len(self.schema),
            "security": len(self.security),
            "providers": len(self.providers),
        }