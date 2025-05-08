from fastapi import APIRouter
from app.api.v1 import user_api, music_api, lantern_api

api_router = APIRouter()

api_router.include_router(user_api.router, prefix="/users", tags=["users"])
api_router.include_router(music_api.router, tags=["music"])
api_router.include_router(lantern_api.router, tags=["lanterns"])

