from datetime import datetime
from typing import Dict, Any

from  server_mcp.mcp_instance import mcp
from  server_mcp.tools.utils import make_success_result, make_error_result


@mcp.tool()
async def server_info() -> str:
    """
    Информация о математическом MCP-сервере.

    Возвращает общие сведения о сервере, доступных возможностях и времени создания ответа.
    """
    try:
        # Здесь можно подтянуть версию/имя из отдельного места, если ты их где-то хранишь.
        name = "Mathematical Calculator & Tutor"
        version = "1.0.0"

        capabilities = {
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
        }

        data: Dict[str, Any] = {
            "name": name,
            "version": version,
            "description": "Полнофункциональный математический MCP-сервер",
            "capabilities": capabilities,
            # время формирования ответа, а не старта процесса — этого обычно достаточно
            "created_at": datetime.utcnow().isoformat(),
        }

        msg = (
            f"{name} (версия {version}). "
            "Сервер предоставляет математические инструменты, ресурсы и промпты."
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "server_info"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось получить информацию о сервере.",
            error=e,
            meta={"tool": "server_info"},
        )
