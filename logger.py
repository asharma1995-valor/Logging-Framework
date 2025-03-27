import logging
import logging.config
import yaml
import os
import json
import re
import uuid
import time
from datetime import datetime
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

try:
    import boto3
    from watchtower import CloudWatchLogHandler
    CLOUDWATCH_AVAILABLE = True
except ImportError:
    CLOUDWATCH_AVAILABLE = False

executor = ThreadPoolExecutor(max_workers=5)


class JsonFormatter(logging.Formatter):
    """Custom JSON Formatter with additional metadata."""

    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": record.levelname,
            "msg body": {
                "id": getattr(record, "id", "N/A"),
                "content": self._mask_sensitive_data(record.getMessage()),
            },
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "execution_time": getattr(record, "execution_time", "N/A"),
            "user_id": getattr(record, "user_id", "anonymous"),
            "correlation_id": getattr(record, "correlation_id", str(uuid.uuid4())),
        }
        return json.dumps(log_record)

    @staticmethod
    def _mask_sensitive_data(message):
        """Mask sensitive data like passwords and emails."""
        message = re.sub(r'("password":\s*")[^"]*"', r'\1*****"', message)
        message = re.sub(r'("email":\s*")[^"]*"', r'\1*****"', message)
        return message


class LoggerSingleton:
    """Singleton Logger with YAML configuration support."""

    _instance = None

    def __new__(cls, config_path):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance._initialize_logger(config_path)
        return cls._instance

    def _initialize_logger(self, config_path):
        """Loads logging configuration from YAML."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Logging config file not found: {config_path}")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        logging.config.dictConfig(config)
        self.logger = logging.getLogger("app")

        for handler in self.logger.handlers:
            handler.setFormatter(JsonFormatter())

        if os.getenv("ENV") in ["stage", "prod"]:
            self._add_cloudwatch_handler()

    def _add_cloudwatch_handler(self):
        """Adds AWS CloudWatch handler if enabled."""
        if not CLOUDWATCH_AVAILABLE:
            self.logger.warning("CloudWatch logging is not available (watchtower not installed).")
            return

        log_group = os.getenv("CLOUDWATCH_LOG_GROUP", "my-log-group")
        log_stream = os.getenv("CLOUDWATCH_LOG_STREAM", "my-log-stream")
        region = os.getenv("AWS_REGION", "us-east-1")

        cloudwatch_handler = CloudWatchLogHandler(
            log_group=log_group, stream_name=log_stream, region_name=region
        )
        cloudwatch_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(cloudwatch_handler)

    def get_logger(self):
        return self.logger


@lru_cache(maxsize=1)
def get_logger():
    """Returns the singleton logger instance based on environment."""
    env = os.getenv("ENV", "local")
    config_file = f"config/log_config_{env}.yaml"
    return LoggerSingleton(config_file).get_logger()


def async_log(message, level="info"):
    """Perform non-blocking logging."""
    future = executor.submit(lambda: getattr(get_logger(), level)(message))
    return future
