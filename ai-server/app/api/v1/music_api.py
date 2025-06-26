from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from starlette.concurrency import run_in_threadpool

from app.core.response import success_response
from app.music.run_musicgen import generate_music

router = APIRouter()


class MultiPromptRequest(BaseModel):
    prompts: List[str]


@router.post("/generate-multiple-music")
async def generate_multiple_music_api(body: MultiPromptRequest):
    music_urls = []

    for prompt in body.prompts:
        output = await run_in_threadpool(generate_music, prompt)
        music_urls.append(output["s3_url"])

    return success_response(
        data={"music_urls": music_urls},
        message="Multiple music generated"
    )
