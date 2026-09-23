import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    Ideal for structured logging in production environments.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra"):
            log_record["extra"] = record.extra

        return json.dumps(log_record)

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a structured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger

# Default application logger
logger = setup_logger("cognitiveos.api")
