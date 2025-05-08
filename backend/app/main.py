from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.v1.routers import api_router
from app.core.config.settings import settings
from app.core.db.database import lifespan
from app.core.exceptions.handlers import http_exception_handler, validation_exception_handler, app_error_handler
from app.core.exceptions.types import AppError

app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_PREFIX)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppError, app_error_handler)


