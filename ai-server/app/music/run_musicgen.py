import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import boto3
from pathlib import Path

# S3 설정
s3_bucket_name = "your-bucket-name"
s3_prefix = "generated/"
s3_client = boto3.client("s3")

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 모델 불러오기
model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)


def upload_to_s3(file_path: Path, s3_key: str) -> str:
    s3_client.upload_file(str(file_path), s3_bucket_name, s3_key)
    return f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_key}"


def generate_music(prompt: str, duration: int = 10) -> str:
    model.set_generation_params(duration=duration)
    wav = model.generate([prompt], progress=False)
    tensor = wav[0].cpu()

    # 임시 파일로 저장
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "sample.wav"
        audio_write(
            stem_name=str(tmp_path).replace(".wav", ""),
            wav=tensor,
            sample_rate=model.sample_rate,
            format="wav",
            strategy="loudness"
        )

        # S3로 업로드
        s3_key = f"{s3_prefix}sample.wav"
        s3_url = upload_to_s3(tmp_path, s3_key)
        return s3_url
