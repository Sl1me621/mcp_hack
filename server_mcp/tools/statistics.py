import math
from statistics import mean, median, pstdev, pvariance
from typing import List, Dict, Any, Optional

from  server_mcp.mcp_instance import mcp
from  server_mcp.tools.utils import make_success_result, make_error_result


def _validate_dataset(values: List[float]) -> Optional[str]:
    if not isinstance(values, list):
        return "Ожидался список чисел."
    if len(values) == 0:
        return "Набор данных не должен быть пустым."
    for v in values:
        if not isinstance(v, (int, float)):
            return "Все элементы набора данных должны быть числами."
    return None


@mcp.tool()
async def analyze_dataset(values: List[float]) -> str:
    """
    Полный статистический анализ набора данных.

    Принимает список чисел и возвращает:
    - количество элементов;
    - минимум, максимум;
    - среднее, медиану;
    - дисперсию, стандартное отклонение;
    - несколько квантилей.
    """
    try:
        err = _validate_dataset(values)
        if err:
            return make_error_result(
                message=err,
                meta={"tool": "analyze_dataset"},
            )

        n = len(values)
        values_sorted = sorted(values)

        data: Dict[str, Any] = {
            "count": n,
            "min": min(values_sorted),
            "max": max(values_sorted),
            "mean": mean(values_sorted),
            "median": median(values_sorted),
        }

        # Дисперсия / СКО (по генеральной совокупности)
        if n > 1:
            data["variance"] = pvariance(values_sorted)
            data["std_dev"] = pstdev(values_sorted)
        else:
            data["variance"] = None
            data["std_dev"] = None

        # Простейшие квантили
        def _quantile(sorted_vals: List[float], q: float) -> float:
            if len(sorted_vals) == 1:
                return sorted_vals[0]
            idx = q * (len(sorted_vals) - 1)
            lower = int(math.floor(idx))
            upper = int(math.ceil(idx))
            if lower == upper:
                return sorted_vals[lower]
            frac = idx - lower
            return sorted_vals[lower] * (1 - frac) + sorted_vals[upper] * frac

        data["quantiles"] = {
            "q0": values_sorted[0],
            "q25": _quantile(values_sorted, 0.25),
            "q50": _quantile(values_sorted, 0.5),
            "q75": _quantile(values_sorted, 0.75),
            "q100": values_sorted[-1],
        }

        msg = (
            f"Статистический анализ набора из {n} значений.\n"
            f"- минимум: {data['min']}\n"
            f"- максимум: {data['max']}\n"
            f"- среднее: {data['mean']}\n"
            f"- медиана: {data['median']}\n"
            f"- стандартное отклонение: {data['std_dev']}"
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "analyze_dataset"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось выполнить статистический анализ набора данных.",
            error=e,
            meta={"tool": "analyze_dataset"},
        )


@mcp.tool()
async def correlation_coefficient(
    x: List[float],
    y: List[float],
) -> str:
    """
    Вычислить коэффициент корреляции Пирсона между двумя наборами данных.

    Ограничения:
    - x и y — списки чисел одинаковой длины;
    - длина >= 2;
    - стандартное отклонение обоих наборов > 0.
    """
    try:
        err_x = _validate_dataset(x)
        if err_x:
            return make_error_result(
                message=f"Ошибка в первом наборе данных: {err_x}",
                meta={"tool": "correlation_coefficient", "dataset": "x"},
            )

        err_y = _validate_dataset(y)
        if err_y:
            return make_error_result(
                message=f"Ошибка во втором наборе данных: {err_y}",
                meta={"tool": "correlation_coefficient", "dataset": "y"},
            )

        if len(x) != len(y):
            return make_error_result(
                message="Наборы данных x и y должны иметь одинаковую длину.",
                meta={
                    "tool": "correlation_coefficient",
                    "len_x": len(x),
                    "len_y": len(y),
                },
            )

        n = len(x)
        if n < 2:
            return make_error_result(
                message="Для вычисления корреляции нужно минимум 2 пары значений.",
                meta={"tool": "correlation_coefficient", "n": n},
            )

        mean_x = mean(x)
        mean_y = mean(y)

        # Ковариация
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / (n - 1)

        # Стандартные отклонения (выборочные)
        def _sample_std(vals: List[float]) -> float:
            m = mean(vals)
            return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))

        std_x = _sample_std(x)
        std_y = _sample_std(y)

        if std_x == 0 or std_y == 0:
            return make_error_result(
                message=(
                    "Стандартное отклонение одного из наборов равно 0. "
                    "Корреляция не определена."
                ),
                meta={
                    "tool": "correlation_coefficient",
                    "std_x": std_x,
                    "std_y": std_y,
                },
            )

        r = cov / (std_x * std_y)

        # Простая интерпретация
        abs_r = abs(r)
        if abs_r < 0.1:
            interpretation = "практически отсутствует линейная связь"
        elif abs_r < 0.3:
            interpretation = "слабая линейная связь"
        elif abs_r < 0.5:
            interpretation = "умеренная линейная связь"
        elif abs_r < 0.7:
            interpretation = "заметная линейная связь"
        elif abs_r < 0.9:
            interpretation = "сильная линейная связь"
        else:
            interpretation = "очень сильная линейная связь"

        data: Dict[str, Any] = {
            "n": n,
            "mean_x": mean_x,
            "mean_y": mean_y,
            "covariance": cov,
            "std_x": std_x,
            "std_y": std_y,
            "pearson_r": r,
            "interpretation": interpretation,
        }

        msg = (
            f"Коэффициент корреляции Пирсона r = {r}. "
            f"Интерпретация: {interpretation}."
        )

        return make_success_result(
            message=msg,
            data=data,
            meta={"tool": "correlation_coefficient"},
        )

    except Exception as e:
        return make_error_result(
            message="Не удалось вычислить коэффициент корреляции Пирсона.",
            error=e,
            meta={"tool": "correlation_coefficient"},
        )
