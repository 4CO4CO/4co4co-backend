from typing import Any
from app.schemas.common import ResponseModel, ErrorResponseModel

def success_response(data: Any, message: str = "Success") -> ResponseModel:
    """
    성공 응답 객체를 생성하여 반환합니다.
    """
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )

def error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> ErrorResponseModel:
    """
    에러 응답 객체를 생성하여 반환합니다.
    """
    return ErrorResponseModel(
        status="error",
        error_code=error_code,
        message=message
    )