from typing import List

from pydantic import BaseModel


class LanternDetailResponseModel(BaseModel):
    lantern_id: str
    owner_name: str
    images: List[str]
    background_sounds: List[str]
