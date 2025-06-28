import re
from typing import List
from fastapi import UploadFile

from app.core.exceptions.types import ValidationError

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_FILE_SIZE_MB = 5
VALID_NAME_REGEX = re.compile(r"^[가-힣a-zA-Z0-9 ]+$")


def validate_name(name: str):
    if not name.strip():
        raise ValidationError("이름은 공백만으로 구성될 수 없습니다.", error_code="LANTERN_VALIDATION_FAILED")
    if not VALID_NAME_REGEX.match(name):
        raise ValidationError("이름에는 한글, 영문, 숫자, 공백만 사용할 수 있습니다.", error_code="LANTERN_VALIDATION_FAILED")


def validate_description(description: str):
    if not description.strip():
        raise ValidationError("설명은 공백만으로 구성될 수 없습니다.", error_code="LANTERN_VALIDATION_FAILED")


def validate_images(images: List[UploadFile]):
    if len(images) != 3:
        raise ValidationError("이미지는 정확히 3장을 업로드해야 합니다.", error_code="INVALID_IMAGE_COUNT")

    for image in images:
        if not any(image.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValidationError("이미지 파일 형식이 유효하지 않습니다.", error_code="INVALID_IMAGE_TYPE")

        image.file.seek(0, 2)  # 파일 끝으로 이동
        file_size = image.file.tell()
        image.file.seek(0)    # 다시 처음으로

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"파일 크기가 {MAX_FILE_SIZE_MB}MB를 초과합니다.", error_code="LANTERN_VALIDATION_FAILED")
