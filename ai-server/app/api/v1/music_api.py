from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.response import success_response
from app.service.music_service import generate_music_service

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/generate-music")
async def generate_music(request: Request, body: PromptRequest):
    model = request.app.state.musicgen_model
    output_path = await generate_music_service(body.prompt, model)
    return success_response(
        data={"file_path": output_path},
        message="Music generated"
    )
