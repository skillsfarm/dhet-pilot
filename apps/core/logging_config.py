"""
Logging configuration for different modes (Development, Testing, Production).

This module provides logging configurations with useful tracing tags including:
- Request ID for tracing requests across the application
- User information for audit trails
- Environment mode for context
- Structured logging for better analysis
"""

import logging
import sys
from typing import Any


class RequestFormatter(logging.Formatter):
    """
    Custom formatter that adds request context to log messages.
    Adds request_id, user, and mode to every log message.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Add request_id if available
        if not hasattr(record, "request_id"):
            record.request_id = "no-request"

        # Add user if available
        if not hasattr(record, "user"):
            record.user = "anonymous"

        # Add mode if available
        if not hasattr(record, "mode"):
            record.mode = "unknown"

        return super().format(record)


class ColoredFormatter(RequestFormatter):
    """
    Formatter with color coding for console output in development.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        return super().format(record)


def get_logging_config(mode: str, debug: bool = False) -> dict[str, Any]:
    """
    Get logging configuration based on mode.

    Args:
        mode: One of 'development', 'testing', 'production'
        debug: Whether DEBUG is enabled

    Returns:
        Dict containing logging configuration
    """
    mode = mode.lower()

    # Base configuration
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "filters": {
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {},
        "loggers": {
            "django": {
                "handlers": [],
                "level": "INFO",
            },
            "django.request": {
                "handlers": [],
                "level": "ERROR" if mode == "production" else "INFO",
                "propagate": False,
            },
            "django.security": {
                "handlers": [],
                "level": "WARNING",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": [],
                "level": "DEBUG" if mode == "development" and debug else "INFO",
                "propagate": False,
            },
            "apps": {
                "handlers": [],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": [],
            "level": "INFO",
        },
    }

    # DEVELOPMENT MODE
    if mode == "development":
        # Colored console output with detailed information
        config["formatters"]["colored"] = {
            "()": "apps.core.logging_config.ColoredFormatter",
            "format": "[{asctime}] {levelname} [{request_id}] [{user}] {name} - {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        }

        config["formatters"]["verbose"] = {
            "()": "apps.core.logging_config.RequestFormatter",
            "format": "[{asctime}] {levelname} [{request_id}] [{user}] {name}.{funcName}:{lineno} - {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        }

        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "stream": sys.stdout,
        }

        # Add handlers to loggers
        for logger in config["loggers"].values():
            logger["handlers"] = ["console"]
        config["root"]["handlers"] = ["console"]

    # TESTING MODE
    elif mode == "testing":
        # Minimal console output for testing
        config["formatters"]["simple"] = {
            "()": "apps.core.logging_config.RequestFormatter",
            "format": "[{levelname}] [{request_id}] {name} - {message}",
            "style": "{",
        }

        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": sys.stdout,
            "filters": ["require_debug_true"],
        }

        # Only log warnings and above during tests
        for logger in config["loggers"].values():
            logger["handlers"] = ["console"]
            logger["level"] = "WARNING"
        config["root"]["handlers"] = ["console"]
        config["root"]["level"] = "WARNING"

    # PRODUCTION MODE
    elif mode == "production":
        # Structured logging for production with JSON format
        config["formatters"]["json"] = {
            "()": "apps.core.logging_config.RequestFormatter",
            "format": '{"timestamp": "{asctime}", "level": "{levelname}", "request_id": "{request_id}", "user": "{user}", "mode": "{mode}", "logger": "{name}", "function": "{funcName}", "line": {lineno}, "message": "{message}"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "style": "{",
        }

        config["formatters"]["simple"] = {
            "()": "apps.core.logging_config.RequestFormatter",
            "format": "[{asctime}] {levelname} [{request_id}] [{user}] {name} - {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        }

        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": sys.stdout,
        }

        # Add handlers to loggers
        for logger in config["loggers"].values():
            logger["handlers"] = ["console"]
        config["root"]["handlers"] = ["console"]

        # Set production log levels
        config["loggers"]["django"]["level"] = "WARNING"
        config["loggers"]["apps"]["level"] = "INFO"

    return config
