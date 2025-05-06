from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import music_service

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/")
async def generate_music(request: PromptRequest):
    return music_service.generate_music(request.prompt)


