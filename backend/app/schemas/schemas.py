from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: str
    message: str
    data: Any = None


class ErrorResponseModel(BaseModel):
    status: str
    error_code: str
    message: str