from fastapi import FastAPI

from app.api.v1.music_api import router
from app.core.exception_handlers import ai_server_error_handler
from app.core.exceptions import AIServerError

app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.add_exception_handler(AIServerError, ai_server_error_handler)


