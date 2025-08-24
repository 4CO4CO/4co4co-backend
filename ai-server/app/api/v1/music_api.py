from typing import Dict
from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.exceptions import AIServerError, GenerationError
from app.services.music_service import generate_music_pipeline

router = APIRouter(tags=["music"])


class GenerateMusicRequest(BaseModel):
    """
    Request schema for music generation.
    For now, just an image path (later could be an uploaded file or S3 key).
    """
    image_path: str


class GenerateMusicResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, str]


@router.post(
    "/generate-music",
    response_model=GenerateMusicResponse,
    summary="Generate background music from an image",
)
async def generate_music_api(body: GenerateMusicRequest):
    """
    Orchestrator API for background music generation.

    Steps:
    1. Extract emotion from image (dummy for now)
    2. Generate music using MusicGen (GPU, lock protected)
    3. Upload to S3 and return the key
    """
    try:
        s3_key = await generate_music_pipeline(body.image_path, duration=10)

        if not s3_key:
            raise GenerationError("Pipeline did not return a valid s3_key")

        return GenerateMusicResponse(
            status="success",
            message="Music generated successfully",
            data={"s3_key": s3_key},
        )

    except AIServerError:
        raise
    except Exception as e:
        raise AIServerError(f"Unexpected error during pipeline execution: {e}")