from fastapi import FastAPI

from app.api.v1.music_api import router as music_router
from app.emotion.main_library import model_load, _load_musicgen_model
from app.utils.exception_handlers import ai_server_error_handler
from app.utils.exceptions import AIServerError

app = FastAPI()

# 라우터 등록
app.include_router(music_router, prefix="/api/v1")

# 예외 핸들러 등록
app.add_exception_handler(AIServerError, ai_server_error_handler)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.

    - Preload all required models (YOLO, CLIP, Face, Color, Moondream, MusicGen)
    - Prevent high latency on the first real request
    """
    # 감정 분석 모델 로드
    model_load(
        yolo_model_path="model/yolo/yolov8s.pt",
        clip_model_path="model/clip/mlp.pt",
        moondream_model_path=None,
        face_experiment_path="model",
        face_model_dir="emotic",
        verbose=True,
    )

    # MusicGen 모델 로드
    _load_musicgen_model(verbose=True)