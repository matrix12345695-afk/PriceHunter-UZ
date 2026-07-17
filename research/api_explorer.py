from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from toolkit.explorer import Explorer


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

logger = logging.getLogger(__name__)


# ==========================================================
# ARGUMENTS
# ==========================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="PriceHunter Developer Toolkit",
    )

    parser.add_argument(
        "url",
        help="URL для исследования",
    )

    return parser.parse_args()


# ==========================================================
# MAIN
# ==========================================================

async def main():

    args = parse_args()

    logger.info("=" * 80)
    logger.info("PriceHunter Developer Toolkit")
    logger.info("=" * 80)
    logger.info("Target : %s", args.url)

    explorer = Explorer(
        url=args.url,
    )

    await explorer.explore()

    logger.info("=" * 80)
    logger.info("Done.")
    logger.info("=" * 80)


# ==========================================================
# ENTRY
# ==========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        logger.warning(
            "Interrupted by user."
        )

        sys.exit(130)