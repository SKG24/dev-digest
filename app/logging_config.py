# File: app/logging_config.py
import logging
import logging.handlers
import os
from pathlib import Path
from app.config import get_settings

def setup_logging():
    """Configure application logging"""
    settings = get_settings()
    
    # Create logs directory
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_dir / settings.LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Application logger
    app_logger = logging.getLogger("dev_digest")
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    return app_logger