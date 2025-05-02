from fastapi import FastAPI, HTTPException
from app.schemas.schemas import ResponseModel
from app.core.exceptions import http_exception_handler

app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)

@app.get("/")
async def root():
    return ResponseModel(
        status="success",
        message="Hello FastAPI!",
        data={"example": 123}
    )
