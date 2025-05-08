from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from app.core.db.database import get_mongo_client
from app.core.exceptions.types import ValidationError
from app.core.response.response import success_response, error_response
from app.services.lantern_service import LanternService

router = APIRouter()

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_FILE_SIZE_MB = 5


@router.post("/lanterns")
async def create_lanterns(
        name: str = Form(...),
        image: UploadFile = File(...),
        db=Depends(get_mongo_client)
):
    if not name.strip():
        raise ValidationError("Lantern name cannot be blank.")

    if len(name) > 50:
        raise ValidationError("Lantern name must be 50 characters or less.")

    if not any(image.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValidationError("Unsupported image format. Allowed: jpg, jpeg, png, webp.")

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")

    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(name, image)
    return success_response(data={"lantern_id": lantern_id}, message="Lantern Created")


@router.get("/lanterns")
async def get_lanterns(
        current_lantern_id: str = Query(...),
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
        current_lantern_id: str = Query(...),
        db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lantern = await lantern_service.get_lantern_detail(lantern_id, current_lantern_id=current_lantern_id)

    if not lantern:
        return error_response(message="Lantern not found")

    return success_response(
        data=lantern.model_dump(),
        message="Lantern detail"
    )
