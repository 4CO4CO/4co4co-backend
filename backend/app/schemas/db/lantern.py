from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class ImageInfo(BaseModel):
    s3_path: str
    original_filename: Optional[str]
    file_extension: Optional[str]
    file_size: Optional[int]


class MusicInfo(BaseModel):
    description: str
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
    is_public: bool
    created_at: datetime

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        return str(id_value)
