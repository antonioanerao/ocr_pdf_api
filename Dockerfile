# ========== Base ==========
FROM python:3.11-slim AS base

# Evita prompts e melhora logs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências do sistema para o ocrmypdf e Tesseract
# (inclui ghostscript, qpdf e idiomas pt/en)
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

# ========== App ==========
WORKDIR /app

# Copia requirements primeiro para aproveitar cache de camadas
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copia o código da API (ajuste se tiver mais arquivos)
COPY app.py /app/app.py
COPY worker.py /app/worker.py
COPY tasks.py /app/tasks.py
COPY .env /app/.env

# Exponha a porta do Uvicorn
EXPOSE 8000

# Opcional: usuário sem privilégios
# RUN useradd -m appuser
# USER appuser

# Healthcheck simples (tente GET /health se você adicionou esse endpoint)
# HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1

# Comando padrão (ajuste host/port conforme seu ambiente)
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
