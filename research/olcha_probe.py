import asyncio
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


SEARCH_URL = "https://olcha.uz/ru/search?search={query}"


async def main():

    Path("research/samples").mkdir(
        parents=True,
        exist_ok=True,
    )

    Path("research/reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30,
        headers={
            "User-Agent":
            (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            )
        },
    ) as client:

        print("Downloading...")

        response = await client.get(
            SEARCH_URL.format(
                query="iphone"
            )
        )

        html = response.text

        Path(
            "research/samples/search.html"
        ).write_text(
            html,
            encoding="utf-8",
        )

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        report = []

        report.append(
            f"Status: {response.status_code}"
        )

        report.append(
            f"Title: {soup.title.text if soup.title else 'None'}"
        )

        report.append(
            f"Links: {len(soup.find_all('a'))}"
        )

        report.append(
            f"Images: {len(soup.find_all('img'))}"
        )

        report.append(
            f"Scripts: {len(soup.find_all('script'))}"
        )

        report.append(
            f"JSON-LD: {len(soup.find_all('script', type='application/ld+json'))}"
        )

        Path(
            "research/reports/report.txt"
        ).write_text(
            "\n".join(report),
            encoding="utf-8",
        )

        print()

        print("========== REPORT ==========")

        for line in report:
            print(line)

        print()

        print("HTML saved.")

        print("Report saved.")


if __name__ == "__main__":
    asyncio.run(main())
