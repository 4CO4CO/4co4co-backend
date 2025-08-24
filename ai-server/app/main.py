from fastapi import FastAPI

from app.api.v1.music_api import router as music_router
from app.core.exception_handlers import ai_server_error_handler
from app.core.exceptions import AIServerError
from app.music.model import model, model_lock

app = FastAPI()

app.include_router(music_router, prefix="/api/v1")
app.add_exception_handler(AIServerError, ai_server_error_handler)


@app.on_event("startup")
async def startup_event():
    """
    앱 시작 시 모델 워밍업 
    """
    # 간단 워밍업: 1초짜리 더미 생성
    with model_lock:
        model.set_generation_params(duration=1)
        model.generate(["warm-up prompt"], progress=False)


