import os

import uvicorn
from loguru import logger


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting PriceHunter UZ Web Server on {host}:{port}")

    uvicorn.run(
        "app.web.server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
