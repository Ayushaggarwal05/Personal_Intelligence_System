import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.settings import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logger = logging.getLogger("peis")
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers if setup multiple times
    if logger.handlers:
        return logger

    # Format definition
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Stdout Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. Rotating File Handler
    log_file_path = os.path.join(settings.LOGS_DIR, "peis.log")
    try:
        # Keep logs up to 5MB, backing up last 3 logs
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback console warn if folder creation/permissions fail
        print(f"Warning: Failed to initialize file logger at {log_file_path}: {e}", file=sys.stderr)
    
    # Configure third-party loggers to use the same output streams
    logging.getLogger("uvicorn.error").handlers = logger.handlers
    logging.getLogger("uvicorn.access").handlers = logger.handlers
    
    return logger

logger = setup_logging()
