import base64
from io import BytesIO

import torch
from diffusers import FluxPipeline

MODEL_ID = "black-forest-labs/FLUX.1-dev"

# Load once (cold start optimization)
pipe = FluxPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16
)
pipe.to("cuda" if torch.cuda.is_available() else "cpu")


def handler(event, context):
    try:
        prompt = event.get("prompt") or event.get("inputs")
        if not prompt:
            return {"statusCode": 400, "body": "Missing 'prompt' field"}

        height = int(event.get("height", 1024))
        width = int(event.get("width", 1024))

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
            "statusCode": 200,
            "body": {
                "image_base64": base64.b64encode(buffer.getvalue()).decode(),
                "format": "png"
            }
        }

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
