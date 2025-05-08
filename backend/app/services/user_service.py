import os
from datetime import datetime
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

        file_path, original_filename, file_extension, file_size = await self._save_file(image)
        user_key = str(uuid4())

        user_model = UserDBModel(
            user_key=user_key,
            name=name,
            image_path=file_path,
            original_filename=original_filename,
            file_extension=file_extension,
            file_size=file_size,
            created_at=datetime.utcnow()
        )

        await self.user_repo.insert_user(user_model.model_dump(exclude={'id'}))
        return user_key

    async def _save_file(self, image):
        original_filename = image.filename
        file_extension = os.path.splitext(original_filename)[1]
        saved_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        try:
            content = await image.read()
            file_size = len(content)
            await image.seek(0)

            with open(file_path, "wb") as buffer:
                buffer.write(content)
        except Exception as e:
            raise FileSaveError(f"File saving failed: {e}") from e

        return file_path, original_filename, file_extension, file_size
