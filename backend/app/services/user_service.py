import os
from uuid import uuid4

from app.core.exceptions import FileSaveError, ValidationError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserDBModel

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UserService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)

    async def create_user(self, name, image):
        if not name.strip():
            raise ValidationError("Name is required")

        file_path = await self._save_file(image)
        user_key = str(uuid4())

        user_model = UserDBModel(
            user_key=user_key,
            name=name,
            image_path=file_path
        )

        await self.user_repo.insert_user(user_model.model_dump())
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
            raise FileSaveError(f"File saving failed: {e}") from e

        return file_path
