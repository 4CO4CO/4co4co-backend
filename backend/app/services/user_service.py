import os
from uuid import uuid4
from fastapi import HTTPException
from app.schemas.user import UserDBModel
from app.repositories.user_repository import UserRepository

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UserService:
    def __init__(self, request):
        self.db = request.app.database
        self.user_repo = UserRepository(self.db)

    async def create_user(self, name, image):
        if not name.strip():
            raise HTTPException(status_code=400, detail="Name is required")

        file_path = await self._save_file(image)
        user_key = str(uuid4())

        user_model = UserDBModel(
            user_key=user_key,
            name=name,
            image_path=file_path
        )

        try:
            await self.user_repo.insert_user(user_model.model_dump())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return user_key

    async def _save_file(self, image):
        file_extension = os.path.splitext(image.filename)[1]
        saved_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        try:
            content = await image.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File saving failed: {e}")

        return file_path