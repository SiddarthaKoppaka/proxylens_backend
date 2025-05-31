import logging
import time

# Configure Logging
logging.basicConfig(
    filename="rag_backend.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_event(event_type, details):
    """
    Logs system events to a file for debugging and optimization.

    Args:
        event_type (str): Type of event (e.g., "Retrieval Grading", "Query Processing", "API Calls").
        details (dict): Additional details to log.
    """
    log_message = f"{event_type}: {details}"
    logging.info(log_message)

def track_time(func):
    """
    Decorator for tracking function execution time.

    Args:
        func (function): The function to time.

    Returns:
        function: Wrapped function with execution timing.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = round(time.time() - start_time, 3)
        log_event("Execution Time", {"function": func.__name__, "time_taken": f"{execution_time}s"})
        return result
    return wrapper
