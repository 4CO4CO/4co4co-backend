from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LanternResponseModel(BaseModel):
    user_key: str
    user_name: str
    user_image_path: str
    music_s3_path: Optional[str]
    panorama_s3_path: Optional[str]
    created_at: datetime
