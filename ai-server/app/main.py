from fastapi import FastAPI

from app.api.v1.music_api import router as music_router
from app.utils.exception_handlers import ai_server_error_handler
from app.utils.exceptions import AIServerError
from app.music.model import model, model_lock

app = FastAPI()

app.include_router(music_router, prefix="/api/v1")
app.add_exception_handler(AIServerError, ai_server_error_handler)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.

    Performs a lightweight model warm-up to:
    - Preload model weights into GPU memory
    - Trigger JIT compilation and CUDA kernel initialization
    - Prevent high latency or errors on the first real request
    """
    with model_lock:
        model.set_generation_params(duration=1)
        model.generate(["warm-up prompt"], progress=False)
