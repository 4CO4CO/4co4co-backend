from fastapi import APIRouter, Request, UploadFile, File, Form, Depends

from app.core.database import get_mongo_client
from app.services.user_service import UserService
from app.core.response import success_response

router = APIRouter()


@router.post("/")
async def create_user(
        name: str = Form(...),
        image: UploadFile = File(...),
        db=Depends(get_mongo_client)
):
    service = UserService(db)
    user_key = await service.create_user(name, image)
    return success_response(data={"user_key": user_key}, message="User Created")
