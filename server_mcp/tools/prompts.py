from typing import Dict, Any, Literal

from  server_mcp.mcp_instance import mcp
from  server_mcp.tools.utils import make_success_result, make_error_result


LevelType = Literal["beginner", "intermediate", "advanced"]


@mcp.prompt()
async def explain_solution(
    problem: str,
    solution: str,
    student_level: LevelType = "intermediate",
) -> str:
    """
    Промпт для объяснения математического решения.

    Возвращает структурированный объект с рекомендациями по объяснению решения
    для указанного уровня ученика.
    """
    try:
        # Здесь мы не генерим LLM-ответ, а подготавливаем структуру / подсказку.
        data: Dict[str, Any] = {
            "problem": problem,
            "solution": solution,
            "student_level": student_level,
            "guidelines": [
                "Объясни решение по шагам.",
                "Избегай избыточной терминологии, если уровень низкий.",
                "Приводи простые примеры и аналогии.",
            ],
        }

        if student_level == "beginner":
            data["tone"] = "очень простое, пошаговое объяснение"
        elif student_level == "advanced":
            data["tone"] = "более формальное и строгие математические формулировки"
        else:
            data["tone"] = "баланс простоты и строгости"

        msg = (
            "Шаблон объяснения решения задачи с учётом уровня ученика. "
            "Можно использовать как контекст для LLM."
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"prompt": "explain_solution"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось сформировать промпт для объяснения решения.",
            error=e,
            meta={"prompt": "explain_solution"},
        )


@mcp.prompt()
async def create_practice_problems(
    topic: str,
    difficulty: LevelType = "intermediate",
    count: int = 5,
) -> str:
    """
    Промпт для создания практических задач по теме.

    Возвращает структуру, которую можно передать LLM для генерации задач.
    """
    try:
        if count <= 0:
            return make_error_result(
                message="Количество задач должно быть положительным.",
                meta={"prompt": "create_practice_problems"},
            )

        data: Dict[str, Any] = {
            "topic": topic,
            "difficulty": difficulty,
            "count": count,
            "requirements": [
                "Задачи должны соответствовать уровню сложности.",
                "Каждая задача должна иметь однозначный ответ.",
                "При возможности добавляй практико-ориентированные формулировки.",
            ],
        }

        msg = (
            f"Шаблон для генерации {count} практических задач по теме '{topic}' "
            f"с уровнем сложности '{difficulty}'."
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"prompt": "create_practice_problems"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось сформировать промпт для создания задач.",
            error=e,
            meta={"prompt": "create_practice_problems"},
        )
