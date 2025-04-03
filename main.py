import time
import os
from logs import get_logger
import json

# Set environment for testing
os.environ["ENV"] = "local"

# Initialize logs
logs = get_logger()

def execution_time_logging():
    """Execution Time Logging - Tracks function execution time"""
    start_time = time.time()
    time.sleep(1.2)  # Simulate a slow process
    execution_time = round(time.time() - start_time, 4)

    logs.info(
        "Function execution completed.",
        extra={"execution_time": execution_time}
    )

def api_logging():
    """API Request Logging - Simulating an API call with execution time"""
    api_endpoint = "/api/v1/get-user"
    start_time = time.time()
    
    logs.info(f"API Request: {api_endpoint}", extra={"user_id": "789", "correlation_id": "xyz-456"})

    # Simulating API response delay
    time.sleep(0.5)
    execution_time = round(time.time() - start_time, 4)

    logs.info(f"API Response: Success for {api_endpoint}", extra={"status": "200 OK", "execution_time": execution_time})

def database_logging():
    """Database Logging - Simulating a DB query log with execution time"""
    db_query = "SELECT * FROM users WHERE id=1;"
    start_time = time.time()

    logs.info(f"Executing DB Query: {db_query}", extra={"db": "MongoDB", "query_status": "executing"})

    # Simulating DB execution
    time.sleep(0.3)
    execution_time = round(time.time() - start_time, 4)

    logs.info(f"DB Query Successful: {db_query}", extra={"query_status": "completed", "execution_time": execution_time})

def test_sensitive_data_logging():
    """Test if passwords and emails are masked in logs."""

    user_data = {
        "username": "john_doe",
        "password": "SuperSecret123",
        "email": "john.doe@example.com"
    }

    # Convert the dictionary to a JSON string before logging
    log_message = f"User login attempt: {json.dumps(user_data)}"  
    logs.info(log_message)
if __name__ == "__main__":
    logs.info("Starting Logging Framework")

    execution_time_logging()
    api_logging()
    database_logging()
    test_sensitive_data_logging()  

    logs.info("Logging Completed Successfully!")
