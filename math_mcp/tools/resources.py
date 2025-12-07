# routes/resources.py
import json
import math
from typing import Any

from fastmcp import FastMCP


def setup_math_resources(server: FastMCP) -> None:
    """Настройка математических ресурсов-справочников."""

    @server.resource("math://formulas/basic")
    async def basic_formulas() -> str:
        """Основные математические формулы (JSON-строка)."""
        formulas: dict[str, Any] = {
            "Алгебра": {
                "Квадратное уравнение": "ax² + bx + c = 0, x = (-b ± √(b²-4ac)) / 2a",
                "Разность квадратов": "a² - b² = (a + b)(a - b)",
                "Квадрат суммы": "(a + b)² = a² + 2ab + b²",
                "Квадрат разности": "(a - b)² = a² - 2ab + b²",
            },
            "Геометрия": {
                "Площадь круга": "S = πr²",
                "Длина окружности": "C = 2πr",
                "Площадь треугольника": "S = ½ × основание × высота",
                "Теорема Пифагора": "c² = a² + b²",
                "Площадь прямоугольника": "S = длина × ширина",
            },
            "Тригонометрия": {
                "Основное тригонометрическое тождество": "sin²α + cos²α = 1",
                "Формула синуса двойного угла": "sin(2α) = 2sin(α)cos(α)",
                "Формула косинуса двойного угла": "cos(2α) = cos²α - sin²α",
            },
        }
        return json.dumps(formulas, ensure_ascii=False, indent=2)

    @server.resource("math://constants/mathematical")
    async def math_constants() -> str:
        """Математические константы (JSON-строка)."""
        constants: dict[str, Any] = {
            "π (Пи)": {
                "value": math.pi,
                "description": "Отношение длины окружности к её диаметру",
                "approximation": "3.14159",
            },
            "e (Число Эйлера)": {
                "value": math.e,
                "description": "Основание натурального логарифма",
                "approximation": "2.71828",
            },
            "φ (Золотое сечение)": {
                "value": (1 + math.sqrt(5)) / 2,
                "description": "Золотое сечение",
                "approximation": "1.61803",
            },
            "√2": {
                "value": math.sqrt(2),
                "description": "Квадратный корень из 2",
                "approximation": "1.41421",
            },
        }
        return json.dumps(constants, ensure_ascii=False, indent=2)
