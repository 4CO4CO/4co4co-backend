from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    status: str
    message: str
    data: T


class ErrorResponseModel(BaseModel):
    status: str
    error_code: str
    message: str
