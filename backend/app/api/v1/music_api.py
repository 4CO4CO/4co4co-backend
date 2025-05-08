from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.database import get_mongo_client
from app.core.response import success_response
from app.services.music_service import MusicService

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
    result = await music_service.generate_music(prompt=request.prompt, user_key=user_key)
    return success_response(data=result, message="Music Generated")
