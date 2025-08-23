import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form

from app.emotion.main   import ConditionalEmotionSystem
from app.emotion.utils import get_emotion_color

router = APIRouter()

system = ConditionalEmotionSystem(
    yolo_model_path="model/yolo/yolov8s.pt",
    clip_model_path="model/clip/mlp.pt",
    moondream_model_path=None,
    face_experiment_path="model",
    face_model_dir="emotic"
)

@router.post("/analyze/")
async def analyze_image(
    file: UploadFile = File(...),
    confidence: float = Form(0.5),
    colors: int = Form(5),
):
    """
    단일 이미지 감정 분석 API
    """
    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / file.filename
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = system.analyze_emotion(
        str(tmp_path),
        confidence_threshold=confidence,
        n_colors=colors
    )

    return {"result": result}
