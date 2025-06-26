from pydantic import BaseModel
from typing import Any


class ResponseModel(BaseModel):
    status: str
    message: str
    data: Any = None


class ErrorResponseModel(BaseModel):
    status: str = "error"
    error_code: str
    message: str
