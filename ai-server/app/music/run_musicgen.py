import os
import tempfile
import torch
import torchaudio
from threading import Lock

from app.core.exceptions import GenerationError
from app.core.s3 import upload_file_to_s3
from audiocraft.models import MusicGen

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# lazy load
model = None
model_lock = Lock()

def init_model():
    global model
    if model is None:
        model = MusicGen.get_pretrained("facebook/musicgen-small", device=device)
        model.compression_model.to(device)

def generate_music(image: str, duration: int = 10) -> dict:
    init_model()
    model.set_generation_params(duration=duration)
    hardcoded_prompt = "a soothing ambient track"

    try:
        with model_lock:
            wav = model.generate([hardcoded_prompt], progress=False)
    except Exception as e:
        raise GenerationError(f"Music generation failed: {e}") from e

    tensor = wav[0].cpu()
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            torchaudio.save(
                tmp.name,
                tensor,
                sample_rate=model.sample_rate,
                format="wav"
            )
            tmp_path = tmp.name

        return upload_file_to_s3(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)