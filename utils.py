import os
import json
import boto3
from pymongo import MongoClient
from logger import get_logger
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)
logger = get_logger()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "logs_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "logs")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]


s3 = boto3.client("s3")
LOGS_BUCKET = os.getenv("LOGS_BUCKET", "your-bucket-name")


def store_log_in_mongo(log_data):
    """Stores log entries asynchronously in MongoDB."""
    def insert():
        try:
            collection.insert_one(log_data)
        except Exception as e:
            logger.error(f"MongoDB Insertion Error: {str(e)}")

    executor.submit(insert)


def upload_log_to_s3(log_file):
    """Uploads log files asynchronously to AWS S3."""
    def upload():
        try:
            s3.upload_file(log_file, LOGS_BUCKET, os.path.basename(log_file))
            logger.info(f"Uploaded {log_file} to S3 bucket {LOGS_BUCKET}")
        except Exception as e:
            logger.error(f"S3 Upload Error: {str(e)}")

    executor.submit(upload)


def create_log_entry(level, message, user_id="anonymous", correlation_id=None):
    """Creates a structured log entry with metadata."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "message": message,
        "user_id": user_id,
        "correlation_id": correlation_id or os.urandom(16).hex(),
    }
    return log_entry


def log_and_store(level, message, user_id="anonymous", correlation_id=None):
    """Logs the message and stores it in MongoDB."""
    log_entry = create_log_entry(level, message, user_id, correlation_id)
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))
    store_log_in_mongo(log_entry)
