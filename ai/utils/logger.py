"""
Structured logging utility for the Smart Ambulance AI Service.

Provides a pre-configured logger that respects the ``AI_LOG_LEVEL``
environment variable (default: ``INFO``).  Import ``get_logger`` in any
module to obtain a named logger with a consistent format.
"""

import logging
import os
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a named logger configured with console output.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A :class:`logging.Logger` instance with a StreamHandler attached
        (idempotent — re-calling with the same name is safe).
    """
    logger = logging.getLogger(name)

    # Only attach handlers once to avoid duplicate log lines
    if logger.handlers:
        return logger

    log_level_str: str = os.getenv("AI_LOG_LEVEL", "INFO").upper()
    log_level: int = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
