class AppError(Exception):
    """Base class for all custom application exceptions."""
    status_code = 500
    error_code = "APP_ERROR"

    def __init__(self, message="Application error", error_code=None):
        self.message = message
        self.error_code = error_code or self.error_code
        super().__init__(message)


class DatabaseError(AppError):
    error_code = "DATABASE_ERROR"

    def __init__(self, message="Database operation failed", error_code=None):
        super().__init__(message=message, error_code=error_code)


class FileSaveError(AppError):
    error_code = "FILE_SAVE_ERROR"

    def __init__(self, message="File upload failed", error_code=None):
        super().__init__(message=message, error_code=error_code)


class ValidationError(AppError):
    status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(self, message="Invalid input", error_code=None):
        super().__init__(message=message, error_code=error_code)


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, message="Resource not found", error_code=None):
        super().__init__(message=message, error_code=error_code)


class ForbiddenError(AppError):
    status_code = 403
    error_code = "FORBIDDEN"

    def __init__(self, message="Access denied", error_code=None):
        super().__init__(message=message, error_code=error_code)

class InvalidResumeEventError(AppError):
    status_code = 400
    error_code = "INVALID_RESUME_EVENT"

    def __init__(self, last_event_id=None):
        msg = f"Invalid resume event id: {last_event_id}" if last_event_id else "Invalid resume event id"
        super().__init__(message=msg, error_code=self.error_code)
