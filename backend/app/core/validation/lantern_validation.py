import re
from typing import List

from fastapi import UploadFile

from app.core.exceptions.types import ValidationError

# Allowed image file extensions
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

# Maximum file size (in MB)
MAX_FILE_SIZE_MB = 30

# Valid name regex: allows Korean, English letters, numbers, and spaces
VALID_NAME_REGEX = re.compile(r"^[가-힣a-zA-Z0-9 ]+$")


def validate_name(name: str):
    """
    Validate lantern name input.
    - Must not be empty or whitespace
    - Must match the allowed character pattern
    """
    if not name.strip():
        raise ValidationError("Please check your input.", error_code="LANTERN_VALIDATION_FAILED")
    if not VALID_NAME_REGEX.match(name):
        raise ValidationError("Please check your input.", error_code="LANTERN_VALIDATION_FAILED")


def validate_images(images: List[UploadFile]):
    """
    Validate uploaded image files.
    - Exactly 3 images must be provided
    - File extension must be one of the allowed types
    - File size must not exceed MAX_FILE_SIZE_MB
    """
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
