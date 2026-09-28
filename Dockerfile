FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04

WORKDIR /app

RUN apt-get update && apt-get install -y     python3     python3-pip     git     && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .

RUN pip3 install --no-cache-dir -r requirements-api.txt

COPY api.py .
COPY agent ./agent
COPY models/agentguard-qlora /models/agentguard-qlora

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
