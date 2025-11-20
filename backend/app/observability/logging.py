import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from app.config import settings

def setup_logging():
    # 1. Ensure log directory exists
    log_path = settings.LOG_FILE
    if log_path:
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    # 2. Define Formatters
    # JSON for files (easier parsing)
    json_format = '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
    json_formatter = logging.Formatter(json_format)
    
    # Standard for console (easier reading)
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_formatter = logging.Formatter(console_format)

    # 3. Create Handlers
    handlers = []

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File Handler
    file_handler = None
    if log_path:
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(json_formatter)
        handlers.append(file_handler)

    # 4. Configure Root Logger
    # This captures app-level logs (logger.info("..."))
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        handlers=handlers,
        force=True
    )

    # 5. PATCH: Attach FileHandler to Third-Party Loggers
    # This captures Uvicorn (requests), SQLAlchemy (queries), and Celery logs
    if file_handler:
        loggers_to_patch = [
            "uvicorn",          # Uvicorn startup/shutdown
            "uvicorn.access",   # HTTP Request logs (GET / 200 OK)
            "uvicorn.error",    # Uvicorn errors
            "sqlalchemy.engine",# SQL Queries (only if LOG_LEVEL=DEBUG usually)
            "celery",           # Celery worker logs
            "celery.task",      # Task execution logs
            "celery.worker",    # Worker process logs
        ]

        for logger_name in loggers_to_patch:
            logger = logging.getLogger(logger_name)
            # Prevent duplicate logs if the logger already has handlers
            if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
                logger.addHandler(file_handler)
            
            # Ensure the logger level allows capturing
            # (uvicorn.access is often INFO, even if app is WARNING)
            if logger_name == "uvicorn.access":
                logger.setLevel(logging.INFO)