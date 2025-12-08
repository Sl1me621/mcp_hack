# agent_service/models.py

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field


class A2ARole(str, Enum):
    USER = "user"          # человек / внешний клиент
    AGENT = "agent"        # твой агент
    TOOL = "tool"          # MCP / внешнее действие
    SYSTEM = "system"      # системные сообщения, инструкции


class A2AContentType(str, Enum):
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class A2AContent(BaseModel):
    """
    Универсальный кусок контента внутри сообщения.
    Можно иметь несколько сегментов: текст + tool_call и т.п.
    """
    type: A2AContentType = Field(
        ...,
        description="Тип сегмента контента: text / tool_call / tool_result"
    )
    text: Optional[str] = Field(
        None,
        description="Текст ответа / запроса"
    )
    tool_name: Optional[str] = Field(
        None,
        description="Имя инструмента (для TOOL_CALL / TOOL_RESULT)"
    )
    tool_args: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Аргументы вызова инструмента (для TOOL_CALL)"
    )
    tool_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Структурированный результат инструмента (для TOOL_RESULT)"
    )


class A2AMessage(BaseModel):
    """
    Сообщение в диалоге A2A: пользователь, агент, tool, system.
    """
    id: Optional[str] = Field(
        default=None,
        description="Опциональный ID сообщения (для трассировки)"
    )
    role: A2ARole = Field(
        ...,
        description="Роль отправителя сообщения"
    )
    contents: List[A2AContent] = Field(
        ...,
        description="Сегменты контента сообщения"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Время создания сообщения"
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Произвольные метаданные (source, tool_id, latency и т.п.)"
    )
class A2ARequest(BaseModel):
    """
    Входной запрос в агента по протоколу A2A.
    Это то, что будет принимать твой FastAPI/Flask endpoint /a2a.
    """

    session_id: str = Field(
        ...,
        description="ID сессии диалога (устойчивый между вызовами)"
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="ID для трассировки (можно пробрасывать в логи/телеметрию)"
    )
    locale: Optional[str] = Field(
        default="ru-RU",
        description="Язык/локаль пользователя"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID пользователя в системе заказчика (если есть)"
    )
    messages: List[A2AMessage] = Field(
        ...,
        description="История диалога (в т.ч. текущий запрос пользователя)"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительный контекст (настройки, параметры сценария)"
    )
class TerminationReason(str, Enum):
    NORMAL = "normal"
    TOOL_ERROR = "tool_error"
    LLM_ERROR = "llm_error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"


class A2AError(BaseModel):
    code: str = Field(..., description="Код ошибки (внутренний или HTTP/LLM/MCP)")
    message: str = Field(..., description="Краткое описание ошибки")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Дополнительные детали (stack trace, payload, т.п.)"
    )


class A2AResponse(BaseModel):
    """
    Ответ агента в формате A2A.
    """

    session_id: str = Field(
        ...,
        description="ID сессии (должен совпадать с запросом)"
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="ID трассировки (копируем из запроса или генерируем)"
    )
    messages: List[A2AMessage] = Field(
        ...,
        description="Новые сообщения от агента и/или tools"
    )
    termination_reason: TerminationReason = Field(
        default=TerminationReason.NORMAL,
        description="Причина завершения шага диалога"
    )
    error: Optional[A2AError] = Field(
        default=None,
        description="Информация об ошибке, если есть"
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Технические метаданные (latency, использованные MCP, и т.п.)"
    )
