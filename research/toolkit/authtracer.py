from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


class AuthTracer:
    """
    Собирает цепочку авторизации браузера.
    Ничего не анализирует, только сохраняет.
    """

    def __init__(self, output_dir: str | Path):

        self.output_dir = Path(output_dir)

        self.requests_dir = self.output_dir / "requests"
        self.cookies_dir = self.output_dir / "cookies"
        self.graphql_dir = self.output_dir / "graphql"

        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.graphql_dir.mkdir(parents=True, exist_ok=True)

        self.timeline = []

        self.counter = 1

    def log_request(
        self,
        method: str,
        url: str,
        headers: dict,
        body,
    ):

        data = {
            "id": self.counter,
            "time": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "headers": headers,
            "body": body,
        }

        filename = self.requests_dir / f"{self.counter:04}.json"

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
                "id": self.counter,
                "type": "request",
                "url": url,
            }
        )

        self.counter += 1

    def log_response(
        self,
        request_id: int,
        status: int,
        headers: dict,
    ):

        filename = self.requests_dir / f"{request_id:04}_response.json"

        filename.write_text(
            json.dumps(
                {
                    "status": status,
                    "headers": headers,
                },
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def log_cookies(
        self,
        cookies,
    ):

        filename = self.cookies_dir / "cookies.json"

        filename.write_text(
            json.dumps(
                cookies,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def save(self):

        (self.output_dir / "timeline.json").write_text(
            json.dumps(
                self.timeline,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )