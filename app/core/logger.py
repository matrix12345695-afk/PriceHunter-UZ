from pathlib import Path
import sys

from loguru import logger

from app.core.settings import settings


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

logger.add(
    LOG_DIR / "pricehunter.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level=settings.LOG_LEVEL,
    enqueue=True,
    backtrace=True,
    diagnose=True,
    encoding="utf-8",
)


def get_logger():
    """
    Return configured logger instance.
    """
    return logger
