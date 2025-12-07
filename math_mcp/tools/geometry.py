# routes/geometry.py
import math
from typing import Any, Dict

from fastmcp import FastMCP


def setup_geometry_routes(server: FastMCP) -> None:
    """Настройка геометрических функций."""

    @server.tool
    async def circle_properties(radius: float) -> Dict[str, Any]:
        """
        Вычислить свойства окружности по радиусу.
        """
        if radius <= 0:
            return {
                "ok": False,
                "error": "Радиус должен быть положительным числом",
                "radius": radius,
            }

        return {
            "ok": True,
            "radius": radius,
            "diameter": 2 * radius,
            "circumference": 2 * math.pi * radius,
            "area": math.pi * radius**2,
            "formulas": {
                "circumference": "2πr",
                "area": "πr²",
            },
        }

    @server.tool
    async def triangle_area(base: float, height: float) -> Dict[str, Any]:
        """
        Вычислить площадь треугольника.
        """
        if base <= 0 or height <= 0:
            return {
                "ok": False,
                "error": "Основание и высота должны быть положительными",
                "base": base,
                "height": height,
            }

        area = 0.5 * base * height
        return {
            "ok": True,
            "base": base,
            "height": height,
            "area": area,
            "formula": "½ × основание × высота",
        }

    @server.tool
    async def distance_between_points(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> Dict[str, Any]:
        """
        Вычислить расстояние между двумя точками.
        """
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        return {
            "ok": True,
            "point1": {"x": x1, "y": y1},
            "point2": {"x": x2, "y": y2},
            "distance": distance,
            "formula": "√[(x₂-x₁)² + (y₂-y₁)²]",
        }
