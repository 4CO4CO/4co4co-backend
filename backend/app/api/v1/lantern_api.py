from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from app.core.database import get_mongo_client
from app.core.response import success_response
from app.services.lantern_service import LanternService

router = APIRouter()


@router.post("/users")
async def create_user(
        name: str = Form(...),
        image: UploadFile = File(...),
        db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    user_key = await lantern_service.create_user(name, image)
    return success_response(data={"user_key": user_key}, message="User Created")


@router.get("/lanterns")
async def get_lanterns(
    current_lantern_id: str = Query(None),
    db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lanterns = await lantern_service.get_recent_lanterns(current_lantern_id=current_lantern_id)
    return success_response(
        data=[lantern.model_dump() for lantern in lanterns],
        message="Lantern list"
    )


@router.get("/lanterns/{lantern_id}")
async def get_lantern_detail(
    lantern_id: str,
    current_lantern_id: str = Query(None),
    db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lantern = await lantern_service.get_lantern_detail(lantern_id, current_lantern_id=current_lantern_id)

    if not lantern:
        return success_response(status="fail", message="Lantern not found", data={})

    return success_response(
        data=lantern.model_dump(),
        message="Lantern detail"
    )