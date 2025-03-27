import json
import time
from django.utils.deprecation import MiddlewareMixin
from logger import async_log
from utils import log_and_store

class APILoggingMiddleware(MiddlewareMixin):
    """Middleware for logging API requests and responses."""
    
    def process_request(self, request):
        request.start_time = time.time()
        request.correlation_id = request.headers.get("X-Correlation-ID", None)

    def process_response(self, request, response):
        execution_time = time.time() - request.start_time
        log_data = {
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "execution_time": round(execution_time, 4),
            "user_id": request.user.id if request.user.is_authenticated else "anonymous",
            "correlation_id": request.correlation_id or "N/A",
        }
        async_log(json.dumps(log_data), "info")
        log_and_store("info", json.dumps(log_data), log_data["user_id"], log_data["correlation_id"])
        return response
