# Используем slim версию: она легче обычной, но стабильнее alpine для python-пакетов
FROM python:3.11-slim

WORKDIR /app

# Настройка окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Устанавливаем системные зависимости (нужны для сборки некоторых библиотек, например lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Ставим зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .


# Запускаем миграции Alembic, а затем сам сервер
CMD sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"

