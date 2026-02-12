FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-devel
WORKDIR /
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY handler.py .
CMD ["python3", "-u", "handler.py"]