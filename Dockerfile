FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY handler.py .

# HuggingFace token passed at build time
ARG HF_TOKEN
ENV HUGGINGFACE_HUB_TOKEN=$HF_TOKEN

# Pre-download model at build time
RUN python3 -c "from diffusers import FluxPipeline; import torch; \
FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-dev', torch_dtype=torch.bfloat16)"

CMD ["python3", "-u", "handler.py"]
