# Базовый образ Python
FROM python:3.12-slim

# Не писать .pyc и буферизовать вывод
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости при необходимости (по минимуму)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходники MCP-сервера
COPY math_mcp ./math_mcp

# Переходим в директорию сервера
WORKDIR /app/math_mcp

# Значения по умолчанию для контейнера
ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

# Открываем порт
EXPOSE 8000

# Команда по умолчанию — запуск MCP-сервера
CMD ["python", "server.py"]
