import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import time

from ..config import settings

def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL)
    
    # Format for logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            RotatingFileHandler(
                filename=os.path.join(log_dir, f"app_{time.strftime('%Y%m%d')}.log"),
                maxBytes=10485760,  # 10 MB
                backupCount=10,
                encoding="utf-8",
            ),
        ],
    )
    
    # Set specific levels for some loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Return root logger
    return logging.getLogger()


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger


def log_exception(logger, exc_info=True):
    """Decorator to log exceptions raised by functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=exc_info)
                raise
        return wrapper
    return decorator