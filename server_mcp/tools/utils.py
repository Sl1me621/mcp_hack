import os
import json
import logging
from typing import Any, Dict, Iterable, Optional, Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """
    Единый формат ответа для всех MCP-инструментов.
    """

    status: Literal["ok", "error"] = Field(
        description="Статус выполнения инструмента: ok или error."
    )
    message: str = Field(
        description="Краткое человекочитаемое описание результата или ошибки."
    )
    data: Optional[Any] = Field(
        default=None,
        description="Структурированные данные результата (числа, списки, словари и т.д.).",
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Служебная информация: имя инструмента, длительность, тип ошибки и т.п.",
    )


def make_success_result(
    message: str,
    data: Any = None,
    *,
    meta: Optional[Dict[str, Any]] = None,
    as_json: bool = True,
) -> str | Dict[str, Any]:
    """
    Сформировать успешный результат.

    message — краткое человекочитаемое описание.
    data   — полезная структура (число, dict, список и т.п.).
    meta   — доп. информация (имя инструмента, duration и т.п.).
    as_json — если True, вернуть JSON-строку, иначе dict.
    """
    result = ToolResult(
        status="ok",
        message=message,
        data=data,
        meta=meta or {},
    ).model_dump()

    if as_json:
        return json.dumps(result, ensure_ascii=False)
    return result


def make_error_result(
    message: str,
    *,
    error: Optional[BaseException] = None,
    meta: Optional[Dict[str, Any]] = None,
    as_json: bool = True,
) -> str | Dict[str, Any]:
    """
    Сформировать ошибочный результат в едином формате.

    message — понятное пользователю описание ошибки.
    error   — сама ошибка (для логов / meta).
    meta    — доп. метаданные.
    as_json — если True, вернуть JSON-строку, иначе dict.
    """
    error_meta: Dict[str, Any] = meta.copy() if meta else {}

    if error is not None:
        error_meta.setdefault("error_type", type(error).__name__)
        error_meta.setdefault("error_detail", str(error))

    logger.warning("Tool returned error: %s", message, exc_info=error)

    result = ToolResult(
        status="error",
        message=message,
        data=None,
        meta=error_meta,
    ).model_dict()

    if as_json:
        return json.dumps(result, ensure_ascii=False)
    return result


def require_env_vars(names: Iterable[str]) -> None:
    """
    Проверяет, что все перечисленные переменные окружения заданы.
    Если какой-то переменной нет — кидает RuntimeError
    с понятным сообщением (можно поймать в инструменте и обернуть через make_error_result).
    """
    missing = [name for name in names if not os.getenv(name)]
    if not missing:
        return

    msg = f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}"
    logger.error(msg)
    raise RuntimeError(msg)
