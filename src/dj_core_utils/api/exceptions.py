class APIClientError(Exception):
    """Base exception for API errors"""

    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(message)


class ServiceTimeoutError(APIClientError):
    """Timeout when calling another service"""

    def __init__(self):
        super().__init__('Service timeout', 504)
