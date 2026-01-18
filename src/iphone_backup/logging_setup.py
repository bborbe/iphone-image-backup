"""Logging configuration."""

import logging


def configure_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d] %(message)s",
        level=getattr(logging, level.upper()),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
