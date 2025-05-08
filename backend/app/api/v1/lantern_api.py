from fastapi import APIRouter, Depends
from app.core.database import get_mongo_client
from app.core.response import success_response
from app.services.lantern_service import LanternService

router = APIRouter()


@router.get("/users/{user_key}/lanterns")
async def get_lanterns(user_key: str, db=Depends(get_mongo_client)):
    lantern_service = LanternService(db)
    lanterns = await lantern_service.get_recent_lanterns(current_user_key=user_key)
    return success_response(
        data=[lantern.model_dump() for lantern in lanterns],
        message="Lantern list"
    )
