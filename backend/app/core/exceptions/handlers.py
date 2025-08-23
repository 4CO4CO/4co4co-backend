import traceback
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config.settings import settings
from app.core.exceptions.types import AppError
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


# RequestValidationError 처리 핸들러 (400 Bad Request)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]["msg"] if exc.errors() else "입력 형식이 올바르지 않습니다."

    response_data = {
        "status": "error",
        "error_code": "INVALID_INPUT_FORMAT",
        "message": "입력 형식이 올바르지 않습니다."
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


# AppError (커스텀 예외) 처리 핸들러
async def app_error_handler(request: Request, exc: AppError):
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


# 500 Internal Server Error 처리 핸들러
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "[Unhandled Exception] %s %s - %s",
        request.method,
        request.url.path,
        str(exc)
    )

    response_data = {
        "status": "error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
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
