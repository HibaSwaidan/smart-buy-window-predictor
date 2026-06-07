FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=120 --retries=10 --prefer-binary -r requirements-api.txt

COPY src ./src
COPY models ./models

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]