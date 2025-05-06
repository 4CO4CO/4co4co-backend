import os
import shutil

from fastapi import APIRouter, UploadFile, File, Form, Request

from app.service.outpaint_service import run_outpaint

router = APIRouter()


@router.post("/outpaint")
async def outpaint_image(
    request: Request,
    image: UploadFile = File(...),
    prompt: str = Form("")
):
    # 저장 경로 설정
    input_path = f"temp_input/{image.filename}"
    output_path = f"temp_output/outpainted_{image.filename}"

    # 임시 폴더 생성
    os.makedirs("temp_input", exist_ok=True)
    os.makedirs("temp_output", exist_ok=True)

    # 업로드된 파일 저장
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # 모델 실행
    result_path = run_outpaint(
        pipe=request.app.state.outpaint_pipeline,
        input_path=input_path,
        output_path=output_path,
        prompt=prompt
    )

    return {
        "message": "Outpainting completed",
        "output_path": result_path
    }

