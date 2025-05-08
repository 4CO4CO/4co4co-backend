from pydantic import BaseModel


class LanternDetailResponseModel(BaseModel):
    lantern_id: str
    owner_name: str
    panorama: str
    background_sound: str
    is_current_lantern: bool
