import os
import uuid
from datetime import datetime
import torchaudio


def generate_music_service(prompt: str, model) -> str:
    os.makedirs("output", exist_ok=True)

    model.set_generation_params(duration=10)
    wav = model.generate([prompt])

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_prompt = prompt.replace(' ', '_').lower()

    filename = f"{safe_prompt}_{timestamp}_{unique_id}.wav"
    output_path = f"output/{filename}"

    torchaudio.save(output_path, wav[0].cpu(), 32000)
    return output_path
