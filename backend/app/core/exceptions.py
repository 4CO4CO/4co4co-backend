class AppError(Exception):
    """Base class for all custom application exceptions."""
    status_code = 500

    def __init__(self, message="Application error"):
        self.message = message
        super().__init__(message)


class DatabaseError(AppError):
    """Raised when a database operation fails."""
    def __init__(self, message="Database operation failed"):
        super().__init__(message)


class FileSaveError(AppError):
    """Raised when file saving fails."""
    def __init__(self, message="File saving failed"):
        super().__init__(message)


class ValidationError(AppError):
    """Raised when input validation fails."""
    status_code = 400

    def __init__(self, message="Validation error"):
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    status_code = 404

    def __init__(self, message="Resource not found"):
        super().__init__(message)
