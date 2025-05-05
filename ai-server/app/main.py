from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from audiocraft.models import MusicGen
import torchaudio

app = FastAPI()

# 모델 로드 (처음에 한 번만)
model = MusicGen.get_pretrained('small')


class PromptRequest(BaseModel):
    prompt: str


@app.post("/generate")
async def generate_music(request: PromptRequest):
    try:
        # 프롬프트로 음악 생성
        model.set_generation_params(duration=10)  # 생성 길이: 10초
        wav = model.generate([request.prompt])  # 리스트 형태로 입력

        # 파일로 저장
        output_path = f"output_{request.prompt.replace(' ', '_')}.wav"
        torchaudio.save(output_path, wav[0].cpu(), 32000)

        return {"message": "Music generated successfully!", "file_path": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
