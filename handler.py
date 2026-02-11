import runpod
import torch
import base64
from io import BytesIO
from diffusers import FluxPipeline

MODEL_ID = "black-forest-labs/FLUX.1-dev"

pipe = None

def load_model():
    global pipe
    if pipe is None:
        pipe = FluxPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16
        )
        pipe.to("cuda")


def handler(event):
    load_model()

    prompt = event["input"]["prompt"]
    height = event["input"].get("height", 1024)
    width = event["input"].get("width", 1024)

    image = pipe(
        prompt,
        height=height,
        width=width,
        guidance_scale=3.5,
        num_inference_steps=28
    ).images[0]

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return {
        "image_base64": base64.b64encode(buffer.getvalue()).decode()
    }


runpod.serverless.start({"handler": handler})
