import logging
import logging.config
import yaml
import os
import json
import re
import uuid
from datetime import datetime
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
import boto3
import watchtower
import time

ENV = "local"  

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
            "correlation_id": str(uuid.uuid4()),  # Generate a new correlation ID for every log entry
        }
        return json.dumps(log_record)

    @staticmethod
    def _mask_sensitive_data(message):
        """Mask sensitive data like passwords and emails from logs."""
        if isinstance(message, dict):
            message = json.dumps(message)

        message = re.sub(r'(["\']?password["\']?\s*[:=]\s*["\']?)[^"\',]+(["\']?)', r'\1*****\2', message, flags=re.IGNORECASE)
        message = re.sub(r'(["\']?email["\']?\s*[:=]\s*["\']?)[^"\',]+(["\']?)', r'\1*****\2', message, flags=re.IGNORECASE)
        message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '*****', message) 
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

        enable_file_logging = config.get("enable_file_logging", False)
        log_file_path = "logs/local_app.log"

        # Ensure logs folder and file exist if file logging is enabled
        if enable_file_logging:
            log_dir = os.path.dirname(log_file_path)
            os.makedirs(log_dir, exist_ok=True)

        # Modify handlers based on `enable_file_logging`
        if enable_file_logging:
            config["loggers"]["app"]["handlers"].append("file")
            config["root"]["handlers"].append("file")
        else:
            # Remove file handler if logging is disabled
            config["handlers"].pop("file", None)
            if "file" in config["loggers"]["app"]["handlers"]:
                config["loggers"]["app"]["handlers"].remove("file")
            if "file" in config["root"]["handlers"]:
                config["root"]["handlers"].remove("file")

        # Apply the modified logging config
        logging.config.dictConfig(config)
        self.logger = logging.getLogger("app")

        # Apply JSON formatter to all handlers
        for handler in self.logger.handlers:
            handler.setFormatter(JsonFormatter())

        # Feature: Enable/Disable CloudWatch logging
        if config.get("enable_cloudwatch_logging", False):
            self._add_cloudwatch_handler()

    def _add_cloudwatch_handler(self):
        """Adds AWS CloudWatch handler if enabled."""
        if not CLOUDWATCH_AVAILABLE:
            self.logger.warning("CloudWatch logging is not available (watchtower not installed).")
            return

        log_group = "my-log-group"
        log_stream = "my-log-stream"
        region = "us-east-1"

        cloudwatch_handler = CloudWatchLogHandler(
            log_group=log_group, stream_name=log_stream, region_name=region
        )
        cloudwatch_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(cloudwatch_handler)

    def get_logger(self):
        return self.logger

@lru_cache(maxsize=1)
def get_logger():
    """Returns the singleton logger instance based on the hardcoded ENV variable."""
    config_file = f"config/log_config_{ENV}.yaml"
    return LoggerSingleton(config_file).get_logger()

def async_log(message, level="info"):
    """Perform non-blocking logging."""
    future = executor.submit(lambda: getattr(get_logger(), level)(message))
    return future
