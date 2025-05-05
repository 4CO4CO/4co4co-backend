from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import http_exception_handler, validation_exception_handler
from app.api.v1 import user_api
from app.core.database import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(user_api.router)


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

