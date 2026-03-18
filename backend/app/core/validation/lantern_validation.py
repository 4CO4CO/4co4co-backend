import re
from typing import List

from fastapi import UploadFile

from app.core.exceptions.types import ValidationError

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

MAX_FILE_SIZE_MB = 30

VALID_NAME_REGEX = re.compile(r"^[가-힣a-zA-Z0-9 ]+$")


def validate_name(name: str):

    if not name.strip():
        raise ValidationError("Please check your input.", error_code="LANTERN_VALIDATION_FAILED")
    if not VALID_NAME_REGEX.match(name):
        raise ValidationError("Please check your input.", error_code="LANTERN_VALIDATION_FAILED")


def validate_images(images: List[UploadFile]):

    if len(images) != 3:
        raise ValidationError("Exactly 3 images must be uploaded.", error_code="INVALID_IMAGE_COUNT")

    for image in images:
        if not any(image.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValidationError("Invalid image file type.", error_code="INVALID_IMAGE_TYPE")

        image.file.seek(0, 2)
        file_size = image.file.tell()
        image.file.seek(0)

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError("File size exceeds 5MB.", error_code="INVALID_FILE_SIZE")
