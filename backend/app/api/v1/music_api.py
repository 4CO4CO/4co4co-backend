from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.db.database import get_mongo_client
from app.core.response.response import success_response
from app.services.music_service import MusicService

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str


@router.post("/lanterns/{lantern_id}/music")
async def generate_music(
        lantern_id: str,
        request: PromptRequest,
        db=Depends(get_mongo_client)
):
    music_service = MusicService(db)
    result = await music_service.generate_music(prompt=request.prompt, lantern_id=lantern_id)
    return success_response(data=result, message="Music Generated")
