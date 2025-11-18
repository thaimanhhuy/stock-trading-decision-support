"""Logging utilities for the trading system."""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional
import yaml


def setup_logging(
    config_path: str = "config/logging_config.yaml",
    default_level: int = logging.INFO,
) -> None:
    """Setup logging configuration.

    Args:
        config_path: Path to logging configuration file
        default_level: Default logging level if config file not found
    """
    # Create log directories if they don't exist
    log_dirs = [
        "logs/application",
        "logs/trading",
        "logs/audit",
    ]
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Load logging configuration
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        except Exception as e:
            logging.basicConfig(level=default_level)
            logging.error(f"Error loading logging configuration: {e}")
            logging.info("Using basic logging configuration")
    else:
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.warning(f"Logging config file not found: {config_path}")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name or __name__)


class LoggerMixin:
    """Mixin class to add logging capability to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger
