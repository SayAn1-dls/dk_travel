"""Structured logging utility for Wanderly."""

import logging
import sys
from datetime import datetime
from typing import Any, Optional


class WanderlyFormatter(logging.Formatter):
    """Custom log formatter with structured output."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = record.levelname
        module = record.module
        message = record.getMessage()

        if self.use_colors:
            color = self.COLORS.get(level, "")
            return f"{timestamp} | {color}{level:8s}{self.RESET} | {module:15s} | {message}"
        return f"{timestamp} | {level:8s} | {module:15s} | {message}"


def get_logger(
    name: str,
    level: int = logging.INFO,
    use_colors: bool = True,
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level
        use_colors: Whether to use ANSI colors

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(WanderlyFormatter(use_colors=use_colors))
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False

    return logger


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    client_ip: Optional[str] = None,
) -> None:
    """Log an HTTP request with structured data."""
    parts = [f"{method} {path} -> {status_code} ({duration_ms:.1f}ms)"]
    if client_ip:
        parts.append(f"client={client_ip}")
    logger.info(" | ".join(parts))


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[dict] = None,
) -> None:
    """Log an error with optional context."""
    msg = f"{type(error).__name__}: {str(error)}"
    if context:
        ctx_str = " | ".join(f"{k}={v}" for k, v in context.items())
        msg += f" | {ctx_str}"
    logger.error(msg, exc_info=True)


def log_db_operation(
    logger: logging.Logger,
    operation: str,
    collection: str,
    duration_ms: float,
    result_count: Optional[int] = None,
) -> None:
    """Log a database operation."""
    msg = f"DB {operation} on {collection} ({duration_ms:.1f}ms)"
    if result_count is not None:
        msg += f" -> {result_count} docs"
    logger.debug(msg)
