# agent_service/main.py

from typing import List, Optional

from fastapi import FastAPI
from agent_mcp.model import (
    A2ARequest,
    A2AResponse,
    A2AMessage,
    A2AContent,
    A2AContentType,
    A2ARole,
    TerminationReason,
    A2AError,
)
from agent_mcp.llm_client import ask_llm
from agent_mcp.mcp_client import call_mcp_tool


app = FastAPI(title="Math A2A Agent")


def _extract_user_text_from_messages(messages: List[A2AMessage]) -> str:
    """
    Забираем текст из последнего сообщения пользователя.
    """
    user_msg: Optional[A2AMessage] = next(
        (m for m in reversed(messages) if m.role == A2ARole.USER),
        None,
    )
    if not user_msg:
        return ""

    parts: List[str] = [
        c.text for c in user_msg.contents
        if c.type == A2AContentType.TEXT and c.text
    ]
    return "\n".join(parts).strip()


@app.post("/a2a", response_model=A2AResponse)
async def handle_a2a(req: A2ARequest) -> A2AResponse:
    user_text = _extract_user_text_from_messages(req.messages)

    if not user_text:
        return A2AResponse(
            session_id=req.session_id,
            trace_id=req.trace_id,
            messages=[],
            termination_reason=TerminationReason.VALIDATION_ERROR,
            error=A2AError(
                code="NO_USER_TEXT",
                message="В запросе отсутствует текст сообщения пользователя",
            ),
        )

    agent_messages: List[A2AMessage] = []

    # Простейшее правило: если пользователь пишет:
    # "calc: 2 + 2 * 3"
    # — вызываем MCP-инструмент calculate_basic
    tool_message: Optional[A2AMessage] = None
    if user_text.lower().startswith("calc:"):
        expression = user_text[len("calc:"):].strip()

        mcp_result = await call_mcp_tool(
            "calculate_basic",
            {"expression": expression},
        )

        tool_message = A2AMessage(
            role=A2ARole.TOOL,
            contents=[
                A2AContent(
                    type=A2AContentType.TOOL_RESULT,
                    tool_name="calculate_basic",
                    tool_output=mcp_result,
                )
            ],
            meta={"source": "math_mcp"},
        )

        agent_messages.append(tool_message)

    # Теперь формируем ответ агента через LLM, передавая (опционально) результат MCP.
    # Можно включить в промпт и user_text, и результат инструмента.
    llm_input_text = user_text
    if tool_message is not None and tool_message.contents:
        llm_input_text += (
            "\n\nРезультат вычисления от MCP:\n"
            f"{tool_message.contents[0].tool_output}"
        )

    llm_reply = ask_llm(
        [
            {
                "role": "system",
                "content": (
                    "Ты математический ассистент. "
                    "Отвечай понятно и по существу. "
                    "Если есть результат MCP-инструмента, используй его."
                ),
            },
            {
                "role": "user",
                "content": llm_input_text,
            },
        ]
    )

    agent_message = A2AMessage(
        role=A2ARole.AGENT,
        contents=[
            A2AContent(
                type=A2AContentType.TEXT,
                text=llm_reply,
            )
        ],
    )
    agent_messages.append(agent_message)

    return A2AResponse(
        session_id=req.session_id,
        trace_id=req.trace_id,
        messages=agent_messages,
        termination_reason=TerminationReason.NORMAL,
        error=None,
        meta={"used_mcp": tool_message is not None},
    )
