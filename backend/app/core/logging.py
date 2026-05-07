import logging
import sys
from logging.config import dictConfig

from app.core.config import settings


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": (
                "%(asctime)s | %(levelname)-8s | "
                "%(name)s | %(message)s"
            ),
        },
        "detailed": {
            "format": (
                "%(asctime)s | %(levelname)-8s | "
                "%(name)s | %(filename)s:%(lineno)d | "
                "%(message)s"
            ),
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed" if settings.DEBUG else "default",
            "stream": sys.stdout,
        },
    },

    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console"],
    },

    "loggers": {
        "uvicorn": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "httpx": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


def setup_logging() -> None:
    """
    Configure application logging globally.
    """
    dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    """
    return logging.getLogger(name)