from fastapi import APIRouter
from pydantic import BaseModel

from app.core.response import success_response
from app.music.run_musicgen import generate_music

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/generate-music")
async def generate_music_api(body: PromptRequest):
    output_path = generate_music(body.prompt)
    return success_response(
        data={"file_path": output_path},
        message="Music generated"
    )
