from contextlib import asynccontextmanager

import torch
from audiocraft.models import MusicGen
from diffusers import AutoencoderKL, TCDScheduler
from diffusers.models.model_loading_utils import load_state_dict
from fastapi import FastAPI
from huggingface_hub import hf_hub_download

from app.core.settings import settings
from app.service.outpaint.controlnet_union import ControlNetModel_Union
from app.service.outpaint.pipeline_fill_sd_xl import StableDiffusionXLFillPipeline

DEVICE = settings.DEVICE

# Model initialization (load once)
def load_pipeline():
    # Load ControlNet-Union model
    config_file = hf_hub_download(
        "xinsir/controlnet-union-sdxl-1.0",
        filename="config_promax.json",
    )
    config = ControlNetModel_Union.load_config(config_file)
    cnet = ControlNetModel_Union.from_config(config)
    model_file = hf_hub_download(
        "xinsir/controlnet-union-sdxl-1.0",
        filename="diffusion_pytorch_model_promax.safetensors",
    )
    state_dict = load_state_dict(model_file)
    loaded_keys = list(state_dict.keys())
    model_union, *_ = ControlNetModel_Union._load_pretrained_model(
        cnet, state_dict, model_file, "xinsir/controlnet-union-sdxl-1.0", loaded_keys
    )
    model_union.to(device=DEVICE, dtype=torch.float16)

    # Load VAE and pipeline
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
    ).to(DEVICE)
    pipe = StableDiffusionXLFillPipeline.from_pretrained(
        "SG161222/RealVisXL_V5.0_Lightning",
        torch_dtype=torch.float16,
        vae=vae,
        controlnet=model_union,
        variant="fp16",
    ).to(DEVICE)
    pipe.scheduler = TCDScheduler.from_config(pipe.scheduler.config)
    return pipe


@asynccontextmanager
async def lifespan(app: FastAPI):
    # MusicGen 모델 로드
    app.state.musicgen_model = MusicGen.get_pretrained('small')

    # 파노라마용 파이프라인 로드
    app.state.outpaint_pipeline = load_pipeline()

    yield
