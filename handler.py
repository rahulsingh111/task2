import runpod
import torch
from diffusers import FluxPipeline
import boto3
import os
import io

# Initialize S3 Client using environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
)

def load_model():
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16
    )
    pipe.enable_model_cpu_offload()
    return pipe

MODEL = load_model()

def upload_to_s3(image, job_id):
    bucket_name = "runpodimages"
    file_name = f"{job_id}.png"
    
    # Save image to an in-memory buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Upload to S3 with correct ContentType for browser viewing
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=buffer,
        ContentType='image/png'
    )
    
    return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

def handler(job):
    job_input = job['input']
    prompt = job_input.get('prompt', 'A cyberpunk cat')

    # Generate image
    result = MODEL(
        prompt,
        height=job_input.get('height', 1024),
        width=job_input.get('width', 1024),
        num_inference_steps=20
    ).images[0]

    # Upload to S3 and return URL
    try:
        image_url = upload_to_s3(result, job['id'])
        return {"image_url": image_url}
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

runpod.serverless.start({"handler": handler})