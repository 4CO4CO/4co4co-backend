from typing import Any

from app.schemas.schemas import ResponseModel

def success_response(data: Any, message: str = "Success"):
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )

def error_response(message: str = "An error occurred"):
    return ResponseModel(
        status="error",
        message=message,
        data=None
    )
