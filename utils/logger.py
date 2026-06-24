"""Logging sozlamasi (loguru)."""
import sys

from loguru import logger


def setup_logger() -> None:
    logger.remove()
    # diagnose=False — traceback'da o'zgaruvchilar qiymatini (token h.k.) ko'rsatmaydi.
    # Maxfiy ma'lumot log faylga sizib chiqmasligi uchun MUHIM.
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
        backtrace=True,
        diagnose=False,
    )
    logger.add(
        "logs/bot.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        backtrace=True,
        diagnose=False,
    )
