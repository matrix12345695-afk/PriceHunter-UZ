from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict


AUTH_DIR = Path("research/auth")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def add_unique(lst: list, value):
    if value not in lst:
        lst.append(value)


def main():

    report = {
        "authorization": [],
        "x_iid": [],
        "cookies": [],
        "set_cookie": [],
        "graphql_operations": [],
        "graphql_endpoints": [],
        "interesting_requests": [],
        "status_codes": defaultdict(int),
    }

    #
    # ---------------- REQUESTS ----------------
    #

    request_dir = AUTH_DIR / "requests"

    if request_dir.exists():

        for file in sorted(request_dir.glob("*.json")):

            obj = load_json(file)

            if not obj:
                continue

            headers = {
                k.lower(): v
                for k, v in obj.get("headers", {}).items()
            }

            url = obj.get("url", "")

            auth = headers.get("authorization")
            if auth:
                add_unique(report["authorization"], auth)

            iid = headers.get("x-iid")
            if iid:
                add_unique(report["x_iid"], iid)

            if "graphql" in url.lower():
                add_unique(
                    report["graphql_endpoints"],
                    url,
                )

            body = obj.get("body")

            if body:

                try:

                    payload = json.loads(body)

                    op = payload.get("operationName")

                    if op:
                        add_unique(
                            report["graphql_operations"],
                            op,
                        )

                except Exception:
                    pass

            if (
                auth
                or iid
                or "graphql" in url.lower()
            ):
                report["interesting_requests"].append(
                    {
                        "method": obj.get("method"),
                        "url": url,
                    }
                )

    #
    # ---------------- RESPONSES ----------------
    #

    response_dir = AUTH_DIR / "responses"

    if response_dir.exists():

        for file in sorted(response_dir.glob("*.json")):

            obj = load_json(file)

            if not obj:
                continue

            status = obj.get("status")

            if status is not None:
                report["status_codes"][str(status)] += 1

            headers = {
                k.lower(): v
                for k, v in obj.get("headers", {}).items()
            }

            cookie = headers.get("set-cookie")

            if cookie:

                parts = cookie.split(",")

                for part in parts:

                    name = part.split("=")[0].strip()

                    if name:
                        add_unique(
                            report["set_cookie"],
                            name,
                        )

    #
    # ---------------- COOKIES ----------------
    #

    cookie_file = (
        AUTH_DIR
        / "cookies"
        / "cookies.json"
    )

    if cookie_file.exists():

        cookies = load_json(cookie_file)

        if cookies:

            for cookie in cookies:

                add_unique(
                    report["cookies"],
                    cookie["name"],
                )

    #
    # defaultdict -> dict
    #

    report["status_codes"] = dict(
        report["status_codes"]
    )

    output = AUTH_DIR / "auth_report.json"

    output.write_text(
        json.dumps(
            report,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("AUTH REPORT")
    print("=" * 60)

    print()

    print(
        "Authorization:",
        len(report["authorization"]),
    )

    print(
        "Cookies:",
        len(report["cookies"]),
    )

    print(
        "Set-Cookie:",
        len(report["set_cookie"]),
    )

    print(
        "GraphQL:",
        len(report["graphql_operations"]),
    )

    print()

    print(
        "Saved to:",
        output,
    )


if __name__ == "__main__":
    main()