import gc

import scipy.io.wavfile
import torch

from app.emotion.main_library import emotion, emotion_to_music_prompt, _MODELS


class AIEngine:
    """
    AI Model Lifecycle & Inference Manager
    - Lazy Loading: 요청 시 모델 로드 -> 추론 -> 메모리 해제
    - GPU Memory Optimization
    """

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False

    def load_models(self):
        """
        [Lazy Loading] 모델을 GPU/메모리에 로드합니다.
        기존 _MODELS 딕셔너리나 라이브러리 초기화 로직을 여기서 호출합니다.
        """
        if not self.is_loaded:
            print(f"[AI Engine] Loading models to {self.device}...")

            if _MODELS.get("music_model"):
                _MODELS["music_model"].to(self.device)

            self.is_loaded = True
            print("[AI Engine] Models loaded successfully.")

    def unload_models(self):
        """
        [Memory Optimization] 추론 후 GPU 메모리를 강제로 비웁니다.
        """
        print("[AI Engine] Unloading models...")

        if _MODELS.get("music_model"):
            _MODELS["music_model"].to("cpu")

        # 가비지 컬렉션 및 CUDA 캐시 정리
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()

        self.is_loaded = False
        print("[AI Engine] Memory cleared.")

    def generate(self, local_image_path: str, local_output_path: str, duration: int = 10) -> dict:
        """
        이미지 -> 감정 분석 -> 프롬프트 -> 음악 생성 -> 로컬 저장
        """
        try:
            # 1. 모델 로드
            self.load_models()

            # 2. 감정 분석 & 캡셔닝
            print(f"[AI Engine] Analyzing emotion from {local_image_path}...")
            # emotion 함수가 내부적으로 모델을 쓴다면 여기서 호출
            emotion_result = emotion(local_image_path, 0.5, 5)
            emotion_label = emotion_result["emotion"]
            caption = emotion_result["caption"]

            # 3. 프롬프트 생성
            prompt = emotion_to_music_prompt(emotion_label, caption)
            print(f"[AI Engine] Generated Prompt: {prompt}")

            # 4. MusicGen 추론
            processor = _MODELS["music_processor"]
            model = _MODELS["music_model"]

            inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(self.device)

            # GPU 추론
            with torch.no_grad():
                audio_values = model.generate(
                    **inputs,
                    max_new_tokens=int(duration * 50),  # 토큰 수 조정 필요시 수정
                    do_sample=True,
                    temperature=1.0,
                    top_k=250,
                    top_p=0.95,
                )

            # 5. 오디오 파일 로컬 저장
            sampling_rate = model.config.audio_encoder.sampling_rate
            audio_data = audio_values[0, 0].cpu().numpy()

            # wav 파일로 저장
            scipy.io.wavfile.write(local_output_path, rate=sampling_rate, data=audio_data)
            print(f"[AI Engine] Audio saved to {local_output_path}")

            return {
                "emotion": emotion_label,
                "caption": caption,
                "prompt": prompt
            }

        except Exception as e:
            print(f"[AI Engine] Generation Error: {e}")
            raise e

        finally:
            # 6. 메모리 해제
            self.unload_models()


ai_engine = AIEngine()