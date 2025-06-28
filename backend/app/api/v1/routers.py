from fastapi import APIRouter

from app.api.v1 import music_api, lantern_api

api_router = APIRouter()

api_router.include_router(music_api.router, tags=["music"])
api_router.include_router(lantern_api.router, tags=["lanterns"])

