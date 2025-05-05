from fastapi import APIRouter, Request, UploadFile, File, Form
from app.services.user_service import UserService
from app.core.response import success_response

router = APIRouter(prefix="/api/v1/users")


@router.post("/")
async def create_user(
    request: Request,
    name: str = Form(...),
    image: UploadFile = File(...)
):
    service = UserService(request)
    user_key = await service.create_user(name, image)
    return success_response(data={"user_key": user_key}, message="User Created")
