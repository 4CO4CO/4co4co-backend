from typing import Dict
from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.exceptions import AIServerError, GenerationError
from app.services.music_service import generate_music_pipeline

router = APIRouter(tags=["music"])


class GenerateMusicRequest(BaseModel):
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

    try:
        result = await generate_music_pipeline(body.image_path, duration=10)

        if not result or not result.get("s3_key"):
            raise GenerationError("Pipeline did not return a valid s3_key")

        return GenerateMusicResponse(
            status="success",
            message="Music generated successfully",
            data=result,
        )

    except AIServerError:
        raise
    except Exception as e:
        raise AIServerError(f"Unexpected error during pipeline execution: {e}")
