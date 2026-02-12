import runpod
import torch
from diffusers import FluxPipeline
import base64
from io import BytesIO


# Optimization: Load model once for all requests
def load_model():
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16
    )
    # This helps fit the model in GPU memory
    pipe.enable_model_cpu_offload()
    return pipe


MODEL = load_model()


def handler(job):
    job_input = job['input']
    prompt = job_input.get('prompt', 'A cyberpunk cat')

    # Generate image
    image = MODEL(
        prompt,
        height=job_input.get('height', 1024),
        width=job_input.get('width', 1024),
        num_inference_steps=20
    ).images[0]

    # Convert to base64 so you can see it in your browser
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {"image": img_str}


runpod.serverless.start({"handler": handler})