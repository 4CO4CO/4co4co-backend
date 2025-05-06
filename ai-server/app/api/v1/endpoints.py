from fastapi import APIRouter, Depends
from pydantic import BaseModel
from audiocraft.models import MusicGen

from app.core.response import success_response
from app.service.music_service import generate_music_service

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


def get_musicgen_model():
    if not hasattr(get_musicgen_model, "model"):
        get_musicgen_model.model = MusicGen.get_pretrained('small')
    return get_musicgen_model.model


@router.post("/generate-music")
async def generate_music(request: PromptRequest, model=Depends(get_musicgen_model)):
    output_path = await generate_music_service(request.prompt, model)
    return success_response(
        data={"file_path": output_path},
        message="Music generated"
    )
