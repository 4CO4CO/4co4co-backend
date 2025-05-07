from types import GeneratorType

from PIL import Image, ImageDraw

from app.core.settings import settings

# These settings are environment-dependent and configurable via .env
WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT
DEVICE = settings.DEVICE
PROMPT_SUFFIX = settings.PROMPT_SUFFIX
RESIZE_OPTION = settings.RESIZE_OPTION

# These are fixed constants unlikely to change between environments
OVERLAP_PERCENTAGE = 10
CUSTOM_RESIZE_PERCENTAGE = 100  # not used when RESIZE_OPTION is Full
ALIGNMENT = "Middle"
OVERLAP_LEFT = True
OVERLAP_RIGHT = True
OVERLAP_TOP = True
OVERLAP_BOTTOM = True
NUM_INFERENCE_STEPS = 8


# Prepare image and mask for outpainting
def prepare_image_and_mask(image: Image.Image):
    # Resize to fit the 1920x1080 canvas
    scale = min(WIDTH / image.width, HEIGHT / image.height)
    w, h = int(image.width * scale), int(image.height * scale)
    src = image.resize((w, h), Image.LANCZOS)

    # Resize percentage (Full means 100%)
    rp = 100 if RESIZE_OPTION == "Full" else CUSTOM_RESIZE_PERCENTAGE
    w2, h2 = max(int(src.width * rp / 100), 64), max(int(src.height * rp / 100), 64)
    src = src.resize((w2, h2), Image.LANCZOS)

    # Calculate overlap (in pixels)
    ox = max(int(w2 * (OVERLAP_PERCENTAGE / 100)), 1)
    oy = max(int(h2 * (OVERLAP_PERCENTAGE / 100)), 1)

    # Compute margins by alignment
    if ALIGNMENT == "Middle":
        mx = (WIDTH - w2) // 2
        my = (HEIGHT - h2) // 2
    elif ALIGNMENT == "Left":
        mx, my = 0, (HEIGHT - h2) // 2
    elif ALIGNMENT == "Right":
        mx, my = WIDTH - w2, (HEIGHT - h2) // 2
    elif ALIGNMENT == "Top":
        mx, my = (WIDTH - w2) // 2, 0
    else:  # Bottom
        mx, my = (WIDTH - w2) // 2, HEIGHT - h2

    # Create background and paste source
    bg = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    bg.paste(src, (mx, my))

    # Build the mask (white=keep, black=fill)
    mask = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(mask)

    left = mx + (ox if OVERLAP_LEFT else 0)
    right = mx + w2 - (ox if OVERLAP_RIGHT else 0)
    top = my + (oy if OVERLAP_TOP else 0)
    bottom = my + h2 - (oy if OVERLAP_BOTTOM else 0)
    draw.rectangle([(left, top), (right, bottom)], fill=0)

    return bg, mask


# Execute outpainting
def run_outpaint(pipe, input_path, output_path, prompt=""):
    img = Image.open(input_path).convert("RGB")
    bg, mask = prepare_image_and_mask(img)

    # Create masked input for ControlNet
    masked = bg.copy()
    masked.paste(0, (0, 0), mask)

    # Build prompt string
    final_prompt = (prompt + PROMPT_SUFFIX).strip() if prompt else PROMPT_SUFFIX.strip(", ")

    # Encode prompt into embeddings
    (prompt_embeds,
     negative_prompt_embeds,
     pooled_prompt_embeds,
     negative_pooled_prompt_embeds) = pipe.encode_prompt(final_prompt, device=DEVICE, do_classifier_free_guidance=True)

    # Run the pipeline without output_type
    outputs = pipe(
        prompt_embeds=prompt_embeds,
        negative_prompt_embeds=negative_prompt_embeds,
        pooled_prompt_embeds=pooled_prompt_embeds,
        negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
        image=masked,
        num_inference_steps=NUM_INFERENCE_STEPS
    )

    # Extract result image
    if hasattr(outputs, 'images'):
        result_image = outputs.images[0]
    elif isinstance(outputs, GeneratorType):
        # Iterate through generator to get final image
        result_image = None
        for item in outputs:
            if isinstance(item, tuple):
                _, gen = item
                result_image = gen
            else:
                result_image = item
    else:
        raise RuntimeError(f"Unexpected pipeline output type: {type(outputs)}")

    # Composite the generated region back onto the background
    comp = bg.convert("RGBA")
    out_rgba = result_image.convert("RGBA")
    comp.paste(out_rgba, (0, 0), mask)

    # Convert the final composite image to RGB (to avoid issues with JPEG)
    comp_rgb = comp.convert("RGB")

    # Save as JPEG
    comp_rgb.save(output_path, "JPEG")
    return output_path
