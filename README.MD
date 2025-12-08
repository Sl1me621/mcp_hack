# Mathematical Calculator & Tutor

Два сервиса:

- `server_mcp` — MCP-сервер на FastMCP (HTTP endpoint `/mcp`). Инструменты: `calculate_basic`, `solve_quadratic`, `factorial`, `analyze_dataset`, `correlation_coefficient`, `circle_properties`, `triangle_area`, `distance_between_points`, ресурсы `math://formulas/basic`, `math://constants/mathematical`, промпты `explain_solution`, `create_practice_problems`, `server_info`.
- `agent_mcp` — A2A-агент на FastAPI. Если пользователь пишет `calc: ...`, агент вызывает MCP-инструмент `calculate_basic`, добавляет результат в диалог и формирует ответ через LLM Evolution API.

## Быстрый старт (локально)

1) Установка
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) MCP-сервер
```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
python -m server_mcp.server
# endpoint: http://127.0.0.1:8000/mcp
```

3) Агент
```bash
export EVOLUTION_API_KEY=...           # обязателен
export EVOLUTION_BASE_URL=...          # при необходимости
export EVOLUTION_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507
export MATH_MCP_URL=http://127.0.0.1:8000/mcp
uvicorn agent_mcp.main:app --host 0.0.0.0 --port 8001
```

4) Проверить через CLI
```bash
python client_a2a.py
# пример: calc: 2 + 2 * 3
```

## Структура

```text
.
├── agent_mcp/           # FastAPI агент A2A → LLM + MCP
├── server_mcp/          # FastMCP сервер (инструменты, ресурсы, промпты)
├── client_a2a.py        # CLI для теста агента
├── docs/                # примеры Docker/compose/catalog
├── requirements.txt
├── README.MD
└── .env                 # локальные переменные (не коммитим)
```

Дополнительно: `server_mcp/test_client.py` — быстрый тест MCP; подробнее в `docs/doc.md`.
