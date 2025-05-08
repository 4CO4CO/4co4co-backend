from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.services.user_service import UserService
from app.core.database import get_mongo_client
from app.core.response import success_response

router = APIRouter()


@router.post("/users")
async def create_user(
        name: str = Form(...),
        image: UploadFile = File(...),
        db=Depends(get_mongo_client)
):
    user_service = UserService(db)
    user_key = await user_service.create_user(name, image)
    return success_response(data={"user_key": user_key}, message="User Created")
