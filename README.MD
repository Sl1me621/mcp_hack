# Mathematical Calculator & Tutor MCP Server

Математический MCP-сервер на базе FastMCP.

Даёт агентам доступ к:

- базовым вычислениям:
  - `calculate_basic`
  - `solve_quadratic`
  - `factorial`
- статистике:
  - `analyze_dataset`
  - `correlation_coefficient`
- геометрии:
  - `circle_properties`
  - `triangle_area`
  - `distance_between_points`
- справочникам:
  - `math://formulas/basic`
  - `math://constants/mathematical`
- промптам:
  - `explain_solution`
  - `create_practice_problems`

Сервер поднимается как HTTP MCP endpoint и может вызываться любым MCP-клиентом.

---

## Структура проекта

```text
.
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
├── min_mcp            # черновики / эксперименты (в бою не используются)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── mcp-server-catalog.yaml
├── mcp_tools.json
├── env_options.json
├── .dockerignore
└── .env               # ЛОКАЛЬНЫЙ, в git не коммитится
