# routes/basic_math.py
import math
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP


def setup_basic_math_routes(server: FastMCP) -> None:
    """Настройка базовых математических операций."""

    @server.tool
    async def calculate_basic(expression: str) -> Dict[str, Any]:
        """
        ВЫЧИСЛЕНИЕ БАЗОВОГО МАТЕМАТИЧЕСКОГО ВЫРАЖЕНИЯ (АСИНХРОННО)

        Пример:
        - "2 + 2 * 3"
        - "sin(pi / 2)"
        """
        try:
            # Разрешаем только безопасные математические функции
            allowed_names = {
                k: v for k, v in math.__dict__.items()
                if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round, "pow": pow})

            result = eval(expression, {"__builtins__": {}}, allowed_names)

            return {
                "ok": True,
                "expression": expression,
                "result": result,
                "result_type": type(result).__name__,
                "calculated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "ok": False,
                "expression": expression,
                "error": str(e),
                "calculated_at": datetime.now().isoformat(),
            }

    @server.tool
    async def solve_quadratic(a: float, b: float, c: float) -> Dict[str, Any]:
        """
        РЕШЕНИЕ КВАДРАТНОГО УРАВНЕНИЯ ax² + bx + c = 0 (АСИНХРОННО)
        """
        discriminant = b**2 - 4 * a * c

        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2 * a)
            x2 = (-b - math.sqrt(discriminant)) / (2 * a)
            roots = [x1, x2]
            root_type = "two_real_roots"
        elif discriminant == 0:
            x = -b / (2 * a)
            roots = [x]
            root_type = "one_real_root"
        else:
            real_part = -b / (2 * a)
            imaginary_part = math.sqrt(abs(discriminant)) / (2 * a)
            roots = [
                f"{real_part} + {imaginary_part}i",
                f"{real_part} - {imaginary_part}i",
            ]
            root_type = "complex_roots"

        return {
            "ok": True,
            "equation": f"{a}x² + {b}x + {c} = 0",
            "discriminant": discriminant,
            "roots": roots,
            "type": root_type,
        }

    @server.tool
    async def factorial(n: int) -> Dict[str, Any]:
        """
        ВЫЧИСЛЕНИЕ ФАКТОРИАЛА (АСИНХРОННО)
        """
        if n < 0:
            return {
                "ok": False,
                "error": "Факториал не определен для отрицательных чисел",
                "number": n,
            }

        result = math.factorial(n)
        return {
            "ok": True,
            "number": n,
            "factorial": result,
            "formula": f"{n}!",
            "steps": " × ".join(str(i) for i in range(1, n + 1)) if n > 0 else "1",
        }
