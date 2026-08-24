from loguru import logger
import sys


def configure_logging():
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level}</level> | {message}",
    )
