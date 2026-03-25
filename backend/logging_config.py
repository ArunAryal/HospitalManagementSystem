"""
Logging configuration for the application.

This module sets up structured logging with appropriate levels and formats,
enabling better debugging and monitoring.
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


# Module-level logger
logger = get_logger(__name__)


class RequestLogger:
    """Utility class for logging HTTP requests and responses."""

    @staticmethod
    def log_request(method: str, path: str, user_id: Optional[int] = None):
        """Log incoming request."""
        logger.debug(f"[REQUEST] {method} {path} | User: {user_id or 'Anonymous'}")

    @staticmethod
    def log_response(status_code: int, duration_ms: float):
        """Log response."""
        level = logging.DEBUG if 200 <= status_code < 300 else logging.WARNING
        logger.log(
            level, f"[RESPONSE] Status: {status_code} | Duration: {duration_ms}ms"
        )

    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None):
        """Log error with context."""
        logger.error(
            f"[ERROR] {context or 'An error occurred'}: {str(error)}", exc_info=True
        )


class DatabaseLogger:
    """Utility class for logging database operations."""

    @staticmethod
    def log_query(query: str, duration_ms: float):
        """Log database query."""
        logger.debug(f"[DB_QUERY] Duration: {duration_ms}ms | {query[:100]}...")

    @staticmethod
    def log_transaction(
        operation: str, model_name: str, record_id: Optional[int] = None
    ):
        """Log database transaction."""
        logger.debug(f"[DB_TRANSACTION] {operation} on {model_name} (ID: {record_id})")

    @staticmethod
    def log_error(error: Exception):
        """Log database error."""
        logger.error(f"[DB_ERROR] {str(error)}", exc_info=True)


class BusinessLogger:
    """Utility class for logging business logic events."""

    @staticmethod
    def log_operation(operation: str, details: Optional[str] = None):
        """Log business operation."""
        logger.info(f"[BUSINESS] {operation} | {details or ''}")

    @staticmethod
    def log_validation_error(field: str, error: str):
        """Log validation error."""
        logger.warning(f"[VALIDATION] Field '{field}': {error}")

    @staticmethod
    def log_duplicate_detection(resource_type: str, field: str):
        """Log duplicate resource detection."""
        logger.warning(
            f"[DUPLICATE] Attempted to create duplicate {resource_type} ({field})"
        )
