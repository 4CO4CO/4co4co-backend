import traceback
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config.settings import settings
from app.core.exceptions.types import AppError
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


# Handler for RequestValidationError (400 Bad Request)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle FastAPI's built-in validation errors (e.g., invalid request body/query).
    - Returns a 400 Bad Request with standardized error response.
    - Includes debug info if running in development mode.
    """
    first_error = exc.errors()[0]["msg"] if exc.errors() else "Invalid input format."

    response_data = {
        "status": "error",
        "error_code": "INVALID_INPUT_FORMAT",
        "message": "Invalid input format."
    }

    if settings.APP_ENV == "development":
        response_data["debug_info"] = {
            "location": f"{request.method} {request.url.path}",
            "exception": type(exc).__name__,
            "stack_trace": traceback.format_exc()
        }

    logger.warning(
        "[ValidationError] %s %s | Error: %s | Response: %s",
        request.method,
        request.url.path,
        first_error,
        response_data
    )

    return JSONResponse(
        status_code=400,
        content=response_data
    )


# Handler for custom AppError
async def app_error_handler(request: Request, exc: AppError):
    """
    Handle application-defined exceptions (AppError).
    - Returns the status_code and error_code defined in the exception
    - Falls back to 500 INTERNAL_SERVER_ERROR if not specified
    """
    status_code = getattr(exc, "status_code", 500)
    error_code = getattr(exc, "error_code", "UNKNOWN_ERROR")
    message = str(exc)

    response_data = {
        "status": "error",
        "error_code": error_code,
        "message": message
    }

    if settings.APP_ENV == "development":
        response_data["debug_info"] = {
            "location": f"{request.method} {request.url.path}",
            "exception": type(exc).__name__,
            "stack_trace": traceback.format_exc()
        }

    logger.error(
        "[AppError] %s %s | ErrorCode: %s | Message: %s | Response: %s",
        request.method,
        request.url.path,
        error_code,
        message,
        response_data,
        exc_info=True
    )

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


# Handler for uncaught generic exceptions (500 Internal Server Error)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected/unhandled exceptions.
    - Always returns a 500 Internal Server Error
    - Logs stack trace and exception details
    - Includes debug info in development mode
    """
    logger.exception(
        "[Unhandled Exception] %s %s - %s",
        request.method,
        request.url.path,
        str(exc)
    )

    response_data = {
        "status": "error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "An internal server error occurred. Please try again later."
    }

    if settings.APP_ENV == "development":
        response_data["debug_info"] = {
            "location": f"{request.method} {request.url.path}",
            "exception": type(exc).__name__,
            "stack_trace": traceback.format_exc()
        }

    return JSONResponse(
        status_code=500,
        content=response_data
    )
