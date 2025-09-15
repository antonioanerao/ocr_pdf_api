FROM python:3.11-slim AS base

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ocrmypdf \
        tesseract-ocr \
        tesseract-ocr-por \
        tesseract-ocr-eng \
        ghostscript \
        qpdf \
        # utilitários úteis
        curl ca-certificates \
        redis-tools \
        && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py
COPY worker.py /app/worker.py
COPY tasks.py /app/tasks.py
COPY .env /app/.env

EXPOSE 8000

# usuário sem privilégios
# RUN useradd -m appuser
# USER appuser

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
