from fastapi import APIRouter

from app.api.v1 import lantern_api

api_router = APIRouter()

api_router.include_router(lantern_api.router, tags=["lanterns"])

