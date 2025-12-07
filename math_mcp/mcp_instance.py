# mcp_instance.py
from datetime import datetime

from fastmcp import FastMCP

from tools.basic_math import setup_basic_math_routes
from tools.statistics import setup_statistics_routes
from tools.geometry import setup_geometry_routes
from tools.resources import setup_math_resources
from tools.prompts import setup_math_prompts


def create_math_server() -> FastMCP:
    """Создать и настроить математический MCP-сервер."""
    server = FastMCP("Mathematical Calculator & Tutor")

    # Подключаем все модули-инструменты
    setup_basic_math_routes(server)
    setup_statistics_routes(server)
    setup_geometry_routes(server)
    setup_math_resources(server)
    setup_math_prompts(server)

    # Дополнительный общий инструмент
    @server.tool
    def server_info() -> dict:
        """Информация о математическом сервере."""
        return {
            "name": "Mathematical Calculator & Tutor",
            "version": "1.0.0",
            "description": "Полнофункциональный математический MCP-сервер",
            "capabilities": {
                "tools": [
                    "Базовые вычисления",
                    "Решение квадратных уравнений",
                    "Статистический анализ",
                    "Геометрические вычисления",
                    "Факториалы",
                ],
                "resources": [
                    "Математические формулы",
                    "Константы",
                    "Справка по статистике",
                    "Примеры решений",
                ],
                "prompts": [
                    "Объяснение решений",
                    "Создание задач",
                    "Репетиторство",
                    "Анализ ошибок",
                ],
            },
            "created_at": datetime.now().isoformat(),
        }

    return server


# Готовый экземпляр MCP-сервера, который импортируется в server.py
mcp = create_math_server()
