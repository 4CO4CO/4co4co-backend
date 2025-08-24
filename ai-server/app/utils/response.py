from typing import Any

from app.schemas.schemas import ResponseModel, ErrorResponseModel


def success_response(data: Any, message: str = "Success"):
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )


def error_response(message: str, error_code: str = "UNKNOWN_ERROR"):
    return ErrorResponseModel(
        status="error",
        error_code=error_code,
        message=message
    )

