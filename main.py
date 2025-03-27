import logging
from logger import get_logger, async_log
import time

logger = get_logger()

logger.info("Application started", extra={"user_id": 123, "correlation_id": "abc123"})

try:
    1 / 0  
except Exception as e:
    logger.error("Exception occurred", exc_info=True)

async_log("This is an async log message", level="debug")

time.sleep(2)  # To allow async log to complete
logger.info("Application finished")
