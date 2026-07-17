from __future__ import annotations

import asyncio
import json

from app.providers.uzum import UzumProvider


async def main():

    provider = UzumProvider()

    try:

        print("=" * 80)
        print("UZUM TEST")
        print("=" * 80)

        items = await provider.search("iphone")

        print(f"Found: {len(items)} products")
        print()

        for i, item in enumerate(items[:10], start=1):

            print(f"{i}. {item['title']}")
            print(f"   ID      : {item['id']}")
            print(f"   Price   : {item['price']}")
            print(f"   Rating  : {item['rating']}")
            print(f"   Reviews : {item['reviews']}")
            print(f"   URL     : {item['url']}")
            print()

        with open(
            "uzum_search_result.json",
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                items,
                f,
                ensure_ascii=False,
                indent=4,
            )

        print("=" * 80)
        print("Saved to uzum_search_result.json")
        print("=" * 80)

    finally:

        await provider.close()


if __name__ == "__main__":

    asyncio.run(main())