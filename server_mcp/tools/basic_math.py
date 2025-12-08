import math
from typing import Any, Dict

from server_mcp.mcp_instance import mcp
from server_mcp.tools.utils   import make_success_result, make_error_result


def _safe_eval(expression: str) -> float:
    """
    Очень простой и ограниченный eval для математических выражений.
    Можно заменить на свою реализацию, если уже была.
    """

    # Разрешённые имена из math
    allowed_names: Dict[str, Any] = {
        k: v for k, v in math.__dict__.items() if not k.startswith("_")
    }
    # Добавим несколько констант/функций явно
    allowed_names.update(
        {
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "round": round,
        }
    )

    # Никаких __builtins__ внутрь не даём
    return eval(expression, {"__builtins__": {}}, allowed_names)


@mcp.tool()
async def calculate_basic(expression: str) -> str:
    """
    ВЫЧИСЛЕНИЕ БАЗОВОГО МАТЕМАТИЧЕСКОГО ВЫРАЖЕНИЯ (АСИНХРОННО)

    Примеры:
    - "2 + 2 * 3"
    - "sin(pi / 2)"
    - "sqrt(2) ** 2"
    """
    try:
        expression_clean = expression.strip()
        if not expression_clean:
            return make_error_result(
                message="Пустое выражение. Укажите математическое выражение для вычисления.",
                meta={"tool": "calculate_basic"},
            )

        result = _safe_eval(expression_clean)

        data = {
            "expression": expression_clean,
            "result": result,
        }

        return make_success_result(
            message=f"Результат вычисления выражения: {expression_clean} = {result}",
            data=data,
            meta={"tool": "calculate_basic"},
        )

    except SyntaxError as e:
        return make_error_result(
            message="Синтаксическая ошибка в выражении. Проверьте корректность записи.",
            error=e,
            meta={"tool": "calculate_basic"},
        )
    except NameError as e:
        return make_error_result(
            message="Выражение содержит неизвестные имена. Разрешены только функции/константы из модуля math.",
            error=e,
            meta={"tool": "calculate_basic"},
        )
    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить выражение из-за непредвиденной ошибки.",
            error=e,
            meta={"tool": "calculate_basic"},
        )


@mcp.tool()
async def solve_quadratic(a: float, b: float, c: float) -> str:
    """
    РЕШЕНИЕ КВАДРАТНОГО УРАВНЕНИЯ ax² + bx + c = 0 (АСИНХРОННО)

    Возвращает корни (действительные или комплексные) и дискриминант.
    """
    try:
        if a == 0:
            return make_error_result(
                message="Коэффициент 'a' не может быть равен 0 для квадратного уравнения.",
                meta={"tool": "solve_quadratic"},
            )

        # D = b^2 - 4ac
        discriminant = b * b - 4 * a * c

        if discriminant > 0:
            root1 = (-b + math.sqrt(discriminant)) / (2 * a)
            root2 = (-b - math.sqrt(discriminant)) / (2 * a)
            roots_type = "real_distinct"
        elif discriminant == 0:
            root1 = root2 = -b / (2 * a)
            roots_type = "real_equal"
        else:
            # Комплексные корни
            real_part = -b / (2 * a)
            imag_part = math.sqrt(-discriminant) / (2 * a)
            root1 = complex(real_part, imag_part)
            root2 = complex(real_part, -imag_part)
            roots_type = "complex"

        data = {
            "a": a,
            "b": b,
            "c": c,
            "discriminant": discriminant,
            "roots_type": roots_type,
            "root1": root1,
            "root2": root2,
        }

        msg_parts = [f"Решение уравнения {a}x² + {b}x + {c} = 0."]
        if roots_type == "real_distinct":
            msg_parts.append(f"Два действительных корня: x₁ = {root1}, x₂ = {root2}.")
        elif roots_type == "real_equal":
            msg_parts.append(f"Один действительный корень (кратный): x = {root1}.")
        else:
            msg_parts.append(
                f"Два комплексных корня: x₁ = {root1}, x₂ = {root2}."
            )
        msg_parts.append(f"Дискриминант D = {discriminant}.")

        return make_success_result(
            message(" ").join(msg_parts),
            data=data,
            meta={"tool": "solve_quadratic"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось решить квадратное уравнение из-за ошибки.",
            error=e,
            meta={"tool": "solve_quadratic"},
        )


@mcp.tool()
async def factorial(n: int) -> str:
    """
    ВЫЧИСЛЕНИЕ ФАКТОРИАЛА (АСИНХРОННО)

    Ограничения:
    - n >= 0
    - n не слишком большой (иначе результат будет огромным и может быть медленно).
    """
    try:
        if n < 0:
            return make_error_result(
                message="Факториал определён только для неотрицательных целых чисел.",
                meta={"tool": "factorial"},
            )

        if n > 10000:
            return make_error_result(
                message="Слишком большое значение n для вычисления факториала. Уменьшите n.",
                meta={"tool": "factorial"},
            )

        value = math.factorial(n)
        data = {
            "n": n,
            "factorial": value,
        }

        return make_success_result(
            message=f"Факториал числа {n} равен {value}.",
            data=data,
            meta={"tool": "factorial"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить факториал из-за ошибки.",
            error=e,
            meta={"tool": "factorial"},
        )
