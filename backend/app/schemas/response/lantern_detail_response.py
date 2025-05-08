from pydantic import BaseModel


class LanternDetailResponseModel(BaseModel):
    id: int
    owner_name: str
    panorama: str
    background_sound: str
