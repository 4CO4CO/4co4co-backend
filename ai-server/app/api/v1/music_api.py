from typing import Dict
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.core.exceptions import GenerationError
from app.music.run_musicgen import generate_music

router = APIRouter()


class GenerateMusicRequest(BaseModel):
    image: str
    description: str


class GenerateMusicResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, str]


@router.post(
    "/generate-music",
    response_model=GenerateMusicResponse,
)
async def generate_music_api(body: GenerateMusicRequest):
    try:
        result = await run_in_threadpool(
            generate_music,
            body.description,
            body.image,
            10
        )
        s3_key = result["s3_key"]

        return {
            "status": "success",
            "message": "Music generated successfully",
            "data": {"s3_key": s3_key}
        }

    except GenerationError as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "data": {"s3_key": ""}
            }
        )
