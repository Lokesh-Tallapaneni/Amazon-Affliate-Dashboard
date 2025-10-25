"""
Logging configuration for the application.

This module sets up logging with proper formatters and handlers.
"""

import logging
import logging.handlers
import os
from typing import Optional


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    log_dir: str = 'logs'
) -> None:
    """
    Configure application logging.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Name of log file (None for no file logging)
        log_dir (str): Directory for log files
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, log_file)

        # Rotating file handler (10MB max, 5 backup files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Log startup message
    root_logger.info(f"Logging configured (level: {log_level})")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name (str): Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
