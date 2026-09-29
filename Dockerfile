FROM python:3.10-slim

# Установка системных утилит для healthcheck и сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка переменных окружения Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода, базы знаний и векторного индекса
COPY terms_map.json .
COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/
COPY index/ ./index/

# Проверка работоспособности сервиса
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Запуск FastAPI REST сервера через Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
