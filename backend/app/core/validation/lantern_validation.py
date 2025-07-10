import re
from typing import List
from fastapi import UploadFile

from app.core.exceptions.types import ValidationError

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_FILE_SIZE_MB = 5
VALID_NAME_REGEX = re.compile(r"^[가-힣a-zA-Z0-9 ]+$")


def validate_name(name: str):
    if not name.strip():
        raise ValidationError("입력값을 확인해주세요.", error_code="LANTERN_VALIDATION_FAILED")
    if not VALID_NAME_REGEX.match(name):
        raise ValidationError("입력값을 확인해주세요.", error_code="LANTERN_VALIDATION_FAILED")


def validate_images(images: List[UploadFile]):
    if len(images) !=3:
        raise ValidationError("이미지는 정확히 3장을 업로드해야 합니다.", error_code="INVALID_IMAGE_COUNT")

    for image in images:
        if not any(image.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValidationError("이미지 파일 형식이 유효하지 않습니다", error_code="INVALID_IMAGE_TYPE")

        image.file.seek(0, 2)
        file_size = image.file.tell()
        image.file.seek(0)

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError("파일 크기가 5MB를 초과합니다.", error_code="INVALID_FILE_SIZE")
