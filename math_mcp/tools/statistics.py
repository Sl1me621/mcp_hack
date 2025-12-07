# routes/statistics.py
import statistics
from typing import Any, Dict, List

from fastmcp import FastMCP


def setup_statistics_routes(server: FastMCP) -> None:
    """Настройка статистических функций."""

    @server.tool
    async def analyze_dataset(numbers: List[float]) -> Dict[str, Any]:
        """
        Полный статистический анализ набора данных.
        """
        if not numbers:
            return {
                "ok": False,
                "error": "Пустой набор данных",
            }

        n = len(numbers)

        result: Dict[str, Any] = {
            "ok": True,
            "dataset": numbers,
            "count": n,
            "sum": sum(numbers),
            "mean": statistics.mean(numbers),
            "median": statistics.median(numbers),
            "range": max(numbers) - min(numbers),
            "min": min(numbers),
            "max": max(numbers),
        }

        # Мода
        if len(set(numbers)) < n:
            try:
                result["mode"] = statistics.mode(numbers)
            except Exception:
                result["mode"] = "Нет однозначной моды"
        else:
            result["mode"] = "Нет моды"

        # Дисперсия и ст. отклонение
        if n > 1:
            result["variance"] = statistics.variance(numbers)
            result["std_deviation"] = statistics.stdev(numbers)
        else:
            result["variance"] = 0
            result["std_deviation"] = 0

        # Квартиль
        if n >= 4:
            quarts = statistics.quantiles(numbers, n=4)
            result["quartiles"] = {
                "q1": quarts[0],
                "q2": statistics.median(numbers),
                "q3": quarts[2],
            }
        else:
            result["quartiles"] = {
                "q1": None,
                "q2": statistics.median(numbers),
                "q3": None,
            }

        return result

    @server.tool
    async def correlation_coefficient(
        x_values: List[float],
        y_values: List[float],
    ) -> Dict[str, Any]:
        """
        Вычислить коэффициент корреляции Пирсона между двумя наборами данных.
        """
        if len(x_values) != len(y_values):
            return {
                "ok": False,
                "error": "Наборы данных должны быть одинакового размера",
                "len_x": len(x_values),
                "len_y": len(y_values),
            }

        if len(x_values) < 2:
            return {
                "ok": False,
                "error": "Нужно минимум 2 точки данных",
                "len": len(x_values),
            }

        try:
            corr = statistics.correlation(x_values, y_values)
            abs_corr = abs(corr)

            if abs_corr >= 0.8:
                strength = "очень сильная"
            elif abs_corr >= 0.6:
                strength = "сильная"
            elif abs_corr >= 0.4:
                strength = "умеренная"
            elif abs_corr >= 0.2:
                strength = "слабая"
            else:
                strength = "очень слабая"

            direction = "положительная" if corr > 0 else "отрицательная"

            return {
                "ok": True,
                "x_values": x_values,
                "y_values": y_values,
                "correlation_coefficient": corr,
                "interpretation": {
                    "strength": strength,
                    "direction": direction,
                    "description": f"{strength} {direction} корреляция",
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "error": f"Ошибка вычисления: {str(e)}",
            }
