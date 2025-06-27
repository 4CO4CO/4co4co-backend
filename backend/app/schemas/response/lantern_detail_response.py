from pydantic import BaseModel
from typing import List


class LanternDetailResponseModel(BaseModel):
    lantern_id: str
    owner_name: str
    images: List[str]
    background_sounds: List[str]
