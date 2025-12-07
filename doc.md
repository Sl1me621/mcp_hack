Инстукция по сборке

---

````markdown
# Инструкция по запуску и развёртыванию Mathematical MCP

Этот документ описывает, как запустить и развернуть математический MCP-сервер тремя способами:

1. Локально (Python + venv)  
2. В Docker  
3. Через Docker Compose  

---

## 1. Предварительные требования

Необходимо, чтобы были установлены:

- Python 3.12+  
- pip  
- Docker  
- Docker Compose  
- Git (если проект клонируется)

Проверка:

```bash
python --version
pip --version
docker --version
docker compose version
````

---

## 2. Структура проекта

```
mcp/
├── math_mcp
│   ├── routes
│   │   ├── basic_math.py
│   │   ├── geometry.py
│   │   ├── prompts.py
│   │   ├── resources.py
│   │   └── statistics.py
│   ├── mcp_instance.py
│   ├── server.py
│   └── test_client.py
├── min_mcp
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── mcp-server-catalog.yaml
├── mcp_tools.json
├── env_options.json
├── .dockerignore
└── .env
```

---

## 3. Файл `.env`

Создайте `.env` в корне проекта:

```env
MCP_NAME="Mathematical Calculator & Tutor"
MCP_HOST=0.0.0.0
MCP_PORT=8000
LOG_LEVEL=DEBUG
```

---

## 4. Локальный запуск

### 4.1. Создать виртуальное окружение

```bash
cd mcp
python -m venv venv
source venv/bin/activate
```

### 4.2. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3. Запустить MCP-сервер

```bash
cd math_mcp
python server.py
```

После старта появится строка:

```
Server URL: http://127.0.0.1:8000/mcp
```

### 4.4. Тестовый клиент

```bash
cd math_mcp
python test_client.py
```

---

## 5. Запуск в Docker

### 5.1. Сборка образа

```bash
docker build -t math-mcp .
```

или принудительно без кеша:

```bash
docker build --no-cache -t math-mcp .
```

### 5.2. Запуск контейнера

```bash
docker run \
  --env MCP_HOST=0.0.0.0 \
  --env MCP_PORT=8000 \
  -p 8000:8000 \
  math-mcp
```

Сервер будет доступен по адресу:

```
http://localhost:8000/mcp
```

---

## 6. Запуск через Docker Compose

Файл `docker-compose.yml` расположен в корне (`mcp/`):

```yaml
version: "3.9"

services:
  math-mcp:
    build: .
    container_name: math-mcp
    env_file:
      - .env
    ports:
      - "8000:8000"
    restart: unless-stopped
```

### 6.1. Поднять сервис

```bash
docker compose up -d
```

### 6.2. Логи

```bash
docker compose logs -f
```

### 6.3. Остановка

```bash
docker compose down
```

После поднятия сервер доступен по:

```
http://localhost:8000/mcp
```

---

## 7. Проверка доступности MCP-endpoint

```bash
curl -v http://localhost:8000/mcp
```

Ожидается отсутствие ошибок соединения (`Connection refused`).

---

## 8. Чек-лист перед деплоем или пушем

### Локально

* `python server.py` запускается без ошибок
* `test_client.py` успешно вызывает инструменты MCP

### Docker

* `docker build -t math-mcp .` проходит успешно
* `docker run -p 8000:8000 math-mcp` поднимает сервер

### Docker Compose

* `docker compose up -d` запускает контейнер
* `docker compose logs` не содержит критических ошибок
* `http://localhost:8000/mcp` доступен

---

