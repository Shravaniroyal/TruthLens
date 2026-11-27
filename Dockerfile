FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY truthlens ./truthlens
COPY app.py forensic_explainer.py ./
COPY models ./models

ENV TRUTHLENS_LOG_CONSOLE=true
EXPOSE 8000 8501

CMD ["python", "-m", "uvicorn", "truthlens.api:app", "--host", "0.0.0.0", "--port", "8000"]
