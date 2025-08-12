from typing import List, Optional
from datetime import datetime, date
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class MusicStatusInfo(BaseModel):
    image_s3: str
    task_id: str
    status: str  # "pending", "success", "failed" 등
    s3_key: Optional[str] = None


class ImageInfo(BaseModel):
    s3_path: str
    original_filename: Optional[str]
    file_extension: Optional[str]
    file_size: Optional[int]


class MusicInfo(BaseModel):
    s3_path: str
    created_at: datetime


class LanternDBModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    lantern_id: str
    user_name: str
    images: List[ImageInfo] = []
    musics: List[MusicInfo] = []
    music_tasks: List[str] = []
    music_statuses: List[MusicStatusInfo] = []
    is_public: bool
    event_date: Optional[date] = None
    created_at: datetime

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        return str(id_value)
