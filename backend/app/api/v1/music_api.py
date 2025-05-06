from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.music_service import MusicService
from app.core.database import get_mongo_client

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/users/{user_key}/music")
async def generate_music(
        user_key: str,
        request: PromptRequest,
        db=Depends(get_mongo_client)
):
    music_service = MusicService(db)
    return await music_service.generate_music(prompt=request.prompt, user_key=user_key)
