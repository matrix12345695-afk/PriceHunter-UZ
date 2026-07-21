# app/providers/graphql/make_search_items.py

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

_REQUEST_FILE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "auth"
    / "requests"
    / "00504.json"
)

_REQUEST = json.loads(_REQUEST_FILE.read_text(encoding="utf-8"))
_TEMPLATE = json.loads(_REQUEST["body"])


def build_payload(
    query: str,
    *,
    offset: int = 0,
    limit: int = 48,
) -> dict:
    payload = deepcopy(_TEMPLATE)

    qi = payload["variables"]["queryInput"]
    qi["text"] = query
    qi["pagination"]["offset"] = offset
    qi["pagination"]["limit"] = limit

    return payload
