from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
import os
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
load_dotenv()


@tool
async def get_random_user_name(gender: str) -> str:
    """
    Возвращает случайное мужское или женское имя в зависимости от условия:
    male - мужчина, female - женщина
    """
    faker = Faker("ru_RU")
    gender = gender.lower()
    if gender == "male":
        return f"{faker.first_name_male()} {faker.last_name_male()}"
    return f"{faker.first_name_female()} {faker.last_name_female()}"

custom_tools = [get_random_user_name]

async def get_all_tools():
    """Получение всех инструментов: ваших + MCP"""
    # Настройка MCP клиента
    mcp_client = MultiServerMCPClient(
        {
            "filesystem": {
                "command": "/usr/bin/npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
                "transport": "stdio",
            },
            "context7": {
                "transport": "streamable_http",
                "url": "https://mcp.context7.com/mcp",
            },
        }
    )

    # Получаем MCP инструменты
    mcp_tools = await mcp_client.get_tools()

    # Объединяем ваши инструменты с MCP инструментами
    return custom_tools + mcp_tools



async def main():
    all_tools = await get_all_tools()


    agent = create_react_agent(
        model=ChatDeepSeek(model="deepseek-chat"),
        tools=all_tools,
        prompt="Ты дружелюбный ассистент, который может генерировать фейковых пользователей, \
    выполнять вычисления и делиться интересными фактами.",
    )
    # Простейший вызов
    result = await agent.ainvoke({"messages": [{"role": "user", "content": "Твой запрос"}]})
    print(result["messages"][-1].content)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
