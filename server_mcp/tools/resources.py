from typing import Dict, Any

from  server_mcp.mcp_instance import mcp
from  server_mcp.tools.utils import make_success_result, make_error_result


@mcp.resource("math://formulas/basic")
async def basic_formulas() -> str:
    """
    Ресурс: базовые математические формулы.

    Возвращает структурированный набор формул (как JSON в едином формате).
    """
    try:
        data: Dict[str, Any] = {
            "arithmetic": {
                "sum": "a + b",
                "difference": "a - b",
                "product": "a * b",
                "division": "a / b (b ≠ 0)",
            },
            "powers_and_roots": {
                "square": "a²",
                "cube": "a³",
                "square_root": "√a",
            },
            "trigonometry": {
                "sin^2 + cos^2": "sin²(x) + cos²(x) = 1",
                "tan_definition": "tan(x) = sin(x) / cos(x) (cos(x) ≠ 0)",
            },
            "geometry": {
                "triangle_area": "S = 1/2 * a * h",
                "circle_area": "S = πr²",
                "circle_circumference": "C = 2πr",
            },
        }

        msg = "Базовые математические формулы: арифметика, степени, корни, тригонометрия и геометрия."

        return make_success_result(
            message=msg,
            data=data,
            meta={"resource": "math://formulas/basic"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось получить ресурс с базовыми формулами.",
            error=e,
            meta={"resource": "math://formulas/basic"},
        )


@mcp.resource("math://constants/mathematical")
async def mathematical_constants() -> str:
    """
    Ресурс: основные математические константы.

    Возвращает значения и краткие описания (как JSON в едином формате).
    """
    try:
        data: Dict[str, Any] = {
            "pi": {
                "value": 3.141592653589793,
                "description": "Отношение длины окружности к её диаметру.",
            },
            "e": {
                "value": 2.718281828459045,
                "description": "Основание натурального логарифма.",
            },
            "golden_ratio": {
                "value": 1.618033988749895,
                "description": "Золотое сечение φ.",
            },
            "sqrt2": {
                "value": 1.4142135623730951,
                "description": "Квадратный корень из 2.",
            },
        }

        msg = "Основные математические константы: π, e, φ, √2 и их описания."

        return make_success_result(
            message=msg,
            data=data,
            meta={"resource": "math://constants/mathematical"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось получить ресурс с математическими константами.",
            error=e,
            meta={"resource": "math://constants/mathematical"},
        )
