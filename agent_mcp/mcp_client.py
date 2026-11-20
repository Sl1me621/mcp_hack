# agent_service/mcp_client.py

import os
import json
from typing import Any, Dict, List

from fastmcp import Client as MCPClient
from fastmcp.exceptions import ToolError, ClientError

# URL твоего MCP-сервера (внутренний адрес, если агент и MCP в одной сети)
MCP_URL = os.getenv("MATH_MCP_URL", "http://math-mcp:8000/mcp")


async def list_available_tools() -> List[Dict[str, Any]]:
    """
    Запрашиваем список инструментов у MCP-сервера.
    Возвращаем краткую структуру: [{name, description, schema}, ...]
    """
    client = MCPClient(MCP_URL)

    async with client:
        try:
            tools = await client.list_tools()
        except ClientError as e:
            # Вернём пустой список — агент подстрахуется и не упадёт.
            return []

        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "schema": tool.inputSchema,
            }
            for tool in tools
        ]


async def call_mcp_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Вызов инструмента MCP-сервера.

    Предполагаем, что MCP возвращает JSON-строку в content[0].text
    по тому формату ToolResult, который ты сделал.
    """
    client = MCPClient(MCP_URL)

    async with client:
        try:
            result = await client.call_tool(tool_name, args)
        except ToolError as e:
            return {
                "status": "error",
                "message": f"Ошибка валидации аргументов инструмента '{tool_name}': {e}",
                "meta": {"tool": tool_name, "args": args},
            }
        except ClientError as e:
            return {
                "status": "error",
                "message": f"Не удалось вызвать инструмент '{tool_name}': {e}",
                "meta": {"tool": tool_name, "args": args},
            }

        if not result.content:
            return {"status": "error", "message": "Пустой ответ MCP", "meta": {"tool": tool_name}}

        text = result.content[0].text

        try:
            data = json.loads(text)
        except Exception:
            # На всякий случай
            return {
                "status": "error",
                "message": "Некорректный JSON от MCP",
                "meta": {"tool": tool_name},
                "raw": text,
            }

        # если это твой ToolResult — просто вернуть как есть
        return data
