from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from starlette.concurrency import run_in_threadpool

from app.core.response import success_response
from app.music.run_musicgen import generate_music

router = APIRouter()


class MultiPromptRequest(BaseModel):
    prompts: List[str]


@router.post("/generate-multiple-music")
async def generate_multiple_music_api(body: MultiPromptRequest):
    async def process_prompt(prompt: str) -> Dict[str, Any]:
        try:
            output = await run_in_threadpool(generate_music, prompt)
            return {"success": True, "s3_url": output["s3_url"], "prompt": prompt}
        except Exception as e:
            return {"success": False, "error": str(e), "prompt": prompt}

    results = await asyncio.gather(
        *[process_prompt(p) for p in body.prompts],
        return_exceptions=False
    )

    successful = [r["s3_url"] for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    return success_response(
        data={
            "music_urls": successful,
            "failures": failed
        },
        message="Music generation completed with partial results" if failed else "All music generated successfully"
    )
