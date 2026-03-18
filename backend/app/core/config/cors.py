from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config.settings import settings  # settings 임포트


def setup_cors(app: FastAPI):
    """
    Setup CORS middleware using configurations from settings.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )