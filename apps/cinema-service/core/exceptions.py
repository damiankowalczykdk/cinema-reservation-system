from fastapi import status


class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "error") -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class NotFoundException(APIException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND")


class ConflictException(APIException):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, error_code="CONFLICT")


class ValidationException(APIException):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, error_code="VALIDATION_ERROR")

