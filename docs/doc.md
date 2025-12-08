# Инструкция по запуску и развёртыванию Math MCP + A2A Agent

Док описывает, как поднять MCP-сервер и A2A-агент локально и в Docker.  
В проекте два сервиса:
- `server_mcp` — MCP-сервер на FastMCP (HTTP `/mcp`);
- `agent_mcp` — FastAPI A2A-агент, вызывает MCP и LLM Evolution API.

---

## 1. Предварительные требования

- Python 3.12+
- pip
- Docker, Docker Compose (для контейнеров)
- Git (если клонируете репо)

Проверка:
```bash
python --version
pip --version
docker --version
docker compose version
```

---

## 2. Структура проекта

```text
.
├── agent_mcp/           # A2A агент (FastAPI → LLM + MCP)
├── server_mcp/          # MCP-сервер (инструменты/ресурсы/промпты)
│   ├── tools/           # basic_math, geometry, statistics, resources, prompts, server_info, utils
│   ├── mcp_instance.py  # регистрация инструментов
│   ├── server.py        # точка входа MCP
│   └── test_client.py   # пример клиента fastmcp
├── client_a2a.py        # CLI-демо для агента
├── docs/                # Dockerfile, docker-compose примеры, catalog
├── requirements.txt
└── .env                 # локальные переменные (в git не коммитится)
```

---

## 3. Переменные окружения

### MCP-сервер
- `MCP_HOST` — адрес бинда (по умолчанию `127.0.0.1`)
- `MCP_PORT` — порт (по умолчанию `8000`)
- `MCP_NAME` — имя сервера (опционально)

### A2A-агент
- `EVOLUTION_API_KEY` — ключ Cloud.ru Evolution API (обязателен)
- `EVOLUTION_BASE_URL` — базовый URL API (опционально, по умолчанию `https://foundation-models.api.cloud.ru/v1`)
- `EVOLUTION_MODEL` — модель (по умолчанию `Qwen/Qwen3-235B-A22B-Instruct-2507`)
- `MATH_MCP_URL` — URL MCP-сервера (по умолчанию `http://math-mcp:8000/mcp`, локально ставьте `http://127.0.0.1:8000/mcp`)

Пример `.env` для локали:
```env
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_NAME="Mathematical Calculator & Tutor"

EVOLUTION_API_KEY=your_key_here
EVOLUTION_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507
MATH_MCP_URL=http://127.0.0.1:8000/mcp
```

---

## 4. Локальный запуск (оба сервиса)

### 4.1. Создать окружение и поставить зависимости
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.2. Запуск MCP-сервера
```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
python -m server_mcp.server
# endpoint будет: http://127.0.0.1:8000/mcp
```

### 4.3. Запуск A2A-агента
```bash
export EVOLUTION_API_KEY=...
export MATH_MCP_URL=http://127.0.0.1:8000/mcp
uvicorn agent_mcp.main:app --host 0.0.0.0 --port 8001
# endpoint: http://127.0.0.1:8001/a2a
```

### 4.4. Проверка
- MCP: `python -m server_mcp.test_client` (вызывает `server_info`)
- Агент: `python client_a2a.py` и ввести `calc: 2 + 2 * 3`

---

## 5. Docker и Docker Compose

В `docs/` лежат базовые файлы:
- `docs/Dockerfile` — сборка образа MCP-сервера
- `docs/docker-compose.yml` — пример compose (только MCP)

Пример сборки MCP:
```bash
docker build -f docs/Dockerfile -t math-mcp .
docker run -p 8000:8000 --env-file .env math-mcp
# проверка: curl -v http://localhost:8000/mcp
```

Пример через compose:
```bash
docker compose -f docs/docker-compose.yml --env-file .env up -d
docker compose -f docs/docker-compose.yml logs -f
```

Агент можно завернуть в отдельный контейнер аналогично (увидит MCP по `MATH_MCP_URL`).

---

## 6. Замечания

- Агент использует простое правило: сообщения `calc: ...` вызывают MCP `calculate_basic`, далее ответ формируется LLM.
- Все инструменты MCP возвращают унифицированный JSON `ToolResult` (`status`, `message`, `data`, `meta`), см. `server_mcp/tools/utils.py`.
- Если меняете порты/хосты, не забудьте обновить `MATH_MCP_URL` для агента и клиентских скриптов.
