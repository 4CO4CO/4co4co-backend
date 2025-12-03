import re
from typing import List

from fastapi import UploadFile

from app.core.exceptions.types import ValidationError

# Allowed image file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # 검색 속도를 위해 set으로 변경

# [Fix] API 명세와 일치하도록 30MB -> 5MB로 수정
MAX_FILE_SIZE_MB = 5

# Valid name regex: allows Korean, English letters, numbers, and spaces
VALID_NAME_REGEX = re.compile(r"^[가-힣a-zA-Z0-9 ]+$")


def validate_name(name: str):
    """
    Validate lantern name input.
    - Must not be empty or whitespace
    - Must match the allowed character pattern
    """
    if not name or not name.strip():
        raise ValidationError(
            "이름을 입력해주세요.",
            error_code="LANTERN_NAME_EMPTY"
        )

    if not VALID_NAME_REGEX.match(name):
        raise ValidationError(
            "이름에는 한글, 영문, 숫자, 공백만 사용할 수 있습니다.",
            error_code="LANTERN_NAME_INVALID"
        )


def validate_images(images: List[UploadFile]):
    """
    Validate uploaded image files.
    - Exactly 3 images must be provided
    - File extension must be one of the allowed types
    - File size must not exceed MAX_FILE_SIZE_MB
    """
    # 1. 개수 검사
    if len(images) != 3:
        raise ValidationError(
            f"이미지는 정확히 3장을 업로드해야 합니다. (현재 {len(images)}장)",
            error_code="INVALID_IMAGE_COUNT"
        )

    for image in images:
        filename = image.filename.lower() if image.filename else ""

        # 2. 확장자 검사
        if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValidationError(
                f"지원하지 않는 파일 형식입니다: {image.filename} (허용: jpg, png, webp)",
                error_code="INVALID_IMAGE_TYPE"
            )

        # 3. 용량 검사
        # SpooledTemporaryFile의 사이즈를 체크하기 위해 커서를 끝으로 이동
        image.file.seek(0, 2)
        file_size = image.file.tell()
        image.file.seek(0)  # [중요] 다시 읽을 수 있도록 커서를 처음으로 되돌림

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"파일 크기는 {MAX_FILE_SIZE_MB}MB를 초과할 수 없습니다: {image.filename}",
                error_code="INVALID_FILE_SIZE"
            )