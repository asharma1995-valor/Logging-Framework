# Logging-Framework
A scalable, secure, and async logging framework with log rotation, contextual logging, AWS CloudWatch, S3 &amp; MongoDB support, and sensitive data masking for efficient debugging and monitoring. 

Enhancements & Use Case of the Logging System 
I have built a production-grade logging framework with the following enhancements:

🔹 Enhancements Added
✅ Log Rotation (Auto-delete old logs)

Uses TimedRotatingFileHandler to rotate logs daily and auto-delete old logs based on backupCount.

Helps manage log size without manual cleanup.

✅ Django Middleware (Logs API requests/responses)

Captures incoming requests, execution time, and outgoing responses.

Useful for tracking API performance and debugging issues.

✅ Contextual Logging (User ID, Function Name, Execution Time)

Adds user ID, function name, and execution time for better traceability.

Helps debug errors efficiently with precise context.

✅ Async Logging (Boosts Performance)

Uses ThreadPoolExecutor to log messages asynchronously.

Ensures logging doesn't block API requests, making the app faster.

✅ AWS CloudWatch, S3 & MongoDB (For Centralized Logging)

Logs can be stored in AWS CloudWatch, S3, and MongoDB for better monitoring.

Useful for debugging in cloud-based environments and centralized log storage.

✅ Security Features (Sensitive Data Masking)

Masks sensitive information like passwords and emails in logs.

Prevents security leaks in logs.

🔹 Use Cases & Benefits
🔸 Microservices & Distributed Systems

Centralized logging (AWS, MongoDB, S3) helps in tracking logs across services.

🔸 Real-time Monitoring & Debugging

CloudWatch logs help in tracking live production issues.

🔸 Performance Optimization & Profiling

Capturing execution time in middleware helps identify slow API endpoints.

🔸 Data Security & Compliance

Log masking ensures that sensitive user data isn’t leaked in logs.

🔸 Scalability & Maintainability

Auto log rotation ensures logs don’t overload the system.

✅ Summary
I built a high-performance, scalable, and secure logging system for local and cloud-based environments.
This setup ensures efficient debugging, security, and performance monitoring while following best practices!