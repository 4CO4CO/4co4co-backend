from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from app.core.db.database import get_mongo_client
from app.core.response.response import success_response
from app.services.lantern_service import LanternService

router = APIRouter()


@router.post("/lanterns")
async def create_lanterns(
        name: str = Form(...),
        image: UploadFile = File(...),
        db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(name, image)
    return success_response(data={"lantern_id": lantern_id}, message="Lantern Created")


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