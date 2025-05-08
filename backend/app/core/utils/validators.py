import re
from bson import ObjectId


def is_valid_name(name: str) -> bool:
    return bool(re.match(r"^[가-힣a-zA-Z0-9 ]{1,50}$", name.strip()))


def is_valid_object_id(id_str: str) -> bool:
    return ObjectId.is_valid(id_str)


def is_allowed_image(filename: str) -> bool:
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def is_file_size_allowed(file_size: int, max_size_mb: int = 5) -> bool:
    return file_size <= max_size_mb * 1024 * 1024
