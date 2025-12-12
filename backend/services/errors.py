from typing import Any, Optional


# Class: ServiceError
class ServiceError(Exception):
    """Exception raised by services to provide structured error information.

    Attributes:
        code: a short machine-friendly error code (e.g., 'DASHBOARD_INVALID_GPS')
        message: human-readable message
        details: optional additional data
    """

    # Function: __init__
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details

    # Function: to_dict
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
