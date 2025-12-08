import math
from typing import Dict, Any

from  server_mcp.mcp_instance import mcp
from  server_mcp.tools.utils import make_success_result, make_error_result


@mcp.tool()
async def circle_properties(radius: float) -> str:
    """
    ВЫЧИСЛЕНИЕ СВОЙСТВ ОКРУЖНОСТИ ПО РАДИУСУ.

    Возвращает:
    - длину окружности;
    - площадь круга.
    """
    try:
        if radius <= 0:
            return make_error_result(
                message="Радиус должен быть положительным числом.",
                meta={"tool": "circle_properties"},
            )

        circumference = 2 * math.pi * radius
        area = math.pi * radius * radius

        data: Dict[str, Any] = {
            "radius": radius,
            "circumference": circumference,
            "area": area,
        }

        msg = (
            f"Для окружности с радиусом {radius}:\n"
            f"- длина окружности: {circumference}\n"
            f"- площадь круга: {area}"
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "circle_properties"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить свойства окружности из-за ошибки.",
            error=e,
            meta={"tool": "circle_properties"},
        )


@mcp.tool()
async def triangle_area(a: float, b: float, c: float) -> str:
    """
    ВЫЧИСЛЕНИЕ ПЛОЩАДИ ТРЕУГОЛЬНИКА ПО ТРЁМ СТОРОНАМ (ФОРМУЛА ГЕРОНА).

    Ограничения:
    - a, b, c > 0
    - треугольник должен существовать (сумма двух сторон > третьей).
    """
    try:
        if a <= 0 or b <= 0 or c <= 0:
            return make_error_result(
                message="Все стороны треугольника должны быть положительными.",
                meta={"tool": "triangle_area"},
            )

        if a + b <= c or a + c <= b or b + c <= a:
            return make_error_result(
                message=(
                    "Треугольник с такими сторонами не существует. "
                    "Сумма любых двух сторон должна быть больше третьей."
                ),
                meta={"tool": "triangle_area"},
            )

        # Формула Герона
        s = (a + b + c) / 2.0
        area_sq = s * (s - a) * (s - b) * (s - c)

        if area_sq < 0:
            # На всякий случай отлов численных артефактов
            return make_error_result(
                message="Не удалось корректно вычислить площадь треугольника (численная ошибка).",
                meta={"tool": "triangle_area", "s": s, "area_sq": area_sq},
            )

        area = math.sqrt(area_sq)

        data: Dict[str, Any] = {
            "a": a,
            "b": b,
            "c": c,
            "semi_perimeter": s,
            "area": area,
        }

        msg = (
            f"Треугольник со сторонами a={a}, b={b}, c={c}:\n"
            f"- полупериметр: {s}\n"
            f"- площадь по формуле Герона: {area}"
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "triangle_area"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить площадь треугольника из-за ошибки.",
            error=e,
            meta={"tool": "triangle_area"},
        )


@mcp.tool()
async def distance_between_points(
    x1: float, y1: float, x2: float, y2: float
) -> str:
    """
    ВЫЧИСЛЕНИЕ РАССТОЯНИЯ МЕЖДУ ДВУМЯ ТОЧКАМИ НА ПЛОСКОСТИ.

    Точки: (x1, y1) и (x2, y2).
    """
    try:
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        data: Dict[str, Any] = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "dx": dx,
            "dy": dy,
            "distance": distance,
        }

        msg = (
            f"Расстояние между точками A({x1}, {y1}) и B({x2}, {y2}) "
            f"равно {distance}."
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "distance_between_points"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить расстояние между точками из-за ошибки.",
            error=e,
            meta={"tool": "distance_between_points"},
        )
