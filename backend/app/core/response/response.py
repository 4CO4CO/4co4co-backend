from typing import Any

from fastapi.responses import JSONResponse

from app.schemas.response.schemas import ResponseModel, ErrorResponseModel


def success_response(data: Any, message: str = "Success"):
    """
    Return a standardized success response.
    - Wraps data inside ResponseModel
    - Provides a default "Success" message
    """
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )


def error_response(message: str = "An error occurred", error_code: str = "UNKNOWN_ERROR"):
    """
    Return a standardized error response.
    - Wraps error details inside ErrorResponseModel
    - Provides default error_code and message if not specified
    """
    return ErrorResponseModel(
        status="error",
        error_code=error_code,
        message=message
    )


def success_no_cache_response(data: Any, message: str = "Success"):
    """
    Return a success response as a JSONResponse with no-cache headers.
    - Ensures client/browser does not cache the response
    - Useful for dynamic or frequently changing data
    """
    model = success_response(data=data, message=message)
    return JSONResponse(
        content=model.model_dump(),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
