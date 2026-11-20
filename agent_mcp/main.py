# agent_service/main.py

import os
from typing import List, Optional, Dict, Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
import json
from agent_mcp.llm_client import ask_llm
from agent_mcp.mcp_client import call_mcp_tool, list_available_tools


app = FastAPI(title="Math A2A Agent")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")

# Разрешаем вызовы с фронта (Vite 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

def _error_response(
    req: A2ARequest,
    code: str,
    message: str,
    reason: TerminationReason,
    details: Optional[Dict[str, Any]] = None,
    messages: Optional[List[A2AMessage]] = None,
) -> A2AResponse:
    """
    Унифицированный ответ об ошибке, чтобы не ронять сервер.
    """
    return A2AResponse(
        session_id=req.session_id,
        trace_id=req.trace_id,
        messages=messages or [],
        termination_reason=reason,
        error=A2AError(
            code=code,
            message=message,
            details=details,
        ),
    )


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

    try:
        agent_messages: List[A2AMessage] = []
        available_tools: List[dict] = []
        try:
            available_tools = await list_available_tools()
        except Exception:
            available_tools = []

        def select_tool(text: str) -> Optional[Dict[str, Any]]:
            """
            Просим LLM выбрать подходящий MCP-инструмент и аргументы (JSON).
            Возвращаем dict | None.
            """
            if not available_tools:
                return None

            def _schema_line(t: Dict[str, Any]) -> str:
                return f"- {t['name']}: {t.get('description','')} | schema: {json.dumps(t.get('schema') or {}, ensure_ascii=False)}"

            tools_block = "\n".join(_schema_line(t) for t in available_tools)

            llm_plan = ask_llm(
                [
                    {
                        "role": "system",
                        "content": (
                            "Ты планировщик MCP. "
                            "Есть инструменты ниже. Выбери один, который лучше подходит, "
                            "и предложи JSON с именем и аргументами строго по inputSchema. "
                            "Соблюдай имена полей и типы (например, для analyze_dataset нужен массив чисел в поле 'values'). "
                            "Не придумывай инструменты, которых нет. "
                            "Если нет подходящего инструмента — верни tool_name: null. "
                            "Ответ ТОЛЬКО JSON без лишнего текста."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Доступные инструменты:\n{tools_block}\n\n"
                            f"Запрос пользователя:\n{text}\n\n"
                            "Формат ответа:\n"
                            '{"tool_name": "name|null", "arguments": {...}, "reason": "кратко"}'
                        ),
                    },
                ],
                max_tokens=400,
                temperature=0,
            )

            try:
                plan = json.loads(llm_plan)
            except Exception:
                return None

            name = plan.get("tool_name")
            if not name or name == "null":
                return None

            # Проверяем, что имя реально существует
            if name not in {t["name"] for t in available_tools}:
                return None

            args = plan.get("arguments") or {}
            return {"name": name, "arguments": args, "reason": plan.get("reason")}

        # Простейшее правило: если пользователь пишет:
        # - по ключевому слову calc вызываем calculate_basic
        # - иначе пытаемся подобрать инструмент из списка MCP через LLM-планировщик
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
        else:
            plan = select_tool(user_text)
            if plan:
                if not isinstance(plan.get("arguments"), dict):
                    return _error_response(
                        req,
                        code="INVALID_PLAN_ARGS",
                        message="Планировщик вернул неверный формат аргументов для инструмента.",
                        reason=TerminationReason.VALIDATION_ERROR,
                        details={"plan": plan},
                    )
                mcp_result = await call_mcp_tool(plan["name"], plan["arguments"])
                tool_message = A2AMessage(
                    role=A2ARole.TOOL,
                    contents=[
                        A2AContent(
                            type=A2AContentType.TOOL_RESULT,
                            tool_name=plan["name"],
                            tool_output=mcp_result,
                        )
                    ],
                    meta={"source": "math_mcp", "reason": plan.get("reason")},
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
                        "Используй ТОЛЬКО данные, которые пришли от пользователя и MCP-инструментов. "
                        "Никаких внешних знаний, домыслов или подсказок. "
                        "Если есть результат MCP-инструмента, опирайся на него. "
                        "Если нет результата инструмента, попроси использовать формат 'calc: <выражение>' "
                        "и поясни, что ты работаешь только с доступными MCP-инструментами."
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


# Отдаём статический фронт (Vite build) только если он присутствует в контейнере.
if os.path.isdir(FRONTEND_DIR):
    assets_dir = os.path.join(FRONTEND_DIR, "assets")

    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    except Exception as e:
        return _error_response(
            req,
            code="UNHANDLED_ERROR",
            message="Произошла внутренняя ошибка агента.",
            reason=TerminationReason.LLM_ERROR,
            details={"error": str(e)},
        )
