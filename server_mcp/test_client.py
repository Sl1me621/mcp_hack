import asyncio
import json
from fastmcp import Client


def safe_parse(text):
    try:
        return json.loads(text)
    except Exception:
        return text


async def main():
    # ВАЖНО: меняешь URL на тот, что реально выдает твой сервер в логах
    SERVER_URL = "http://127.0.0.1:8000/mcp"

    print(f"Подключаюсь к MCP-серверу: {SERVER_URL}")
    client = Client(SERVER_URL)

    async with client:
        print("Соединение установлено.\n")

        # -------- TOOLS --------
        tools = await client.list_tools()
        # print(f"Tools: {len(tools)} найдено")
        # for t in tools:
            # print(f" - {t.name}: {t.description}")

        # -------- RESOURCES --------
        resources = await client.list_resources()
        # print(f"\nResources: {len(resources)} найдено")
        # for r in resources:
            # print(f" - {r.uri}")

        # -------- PROMPTS --------
        prompts = await client.list_prompts()
        # print(f"\nPrompts: {len(prompts)} найдено")
        # for p in prompts:
            # print(f" - {p.name}: {p.description}")

        # -------- CALL TEST TOOL --------
        print("\nТестируем вызов server_info...\n")
        result = await client.call_tool("server_info", {})
        raw = result.content[0].text
        parsed = safe_parse(raw)

        # print("Сырой ответ:")
        # print(raw)

        # print("\nРаспарсенный ответ:")
        # print(json.dumps(parsed, indent=2, ensure_ascii=False))

        # Если это ToolResult — красиво показать
        if isinstance(parsed, dict) and "status" in parsed:
            print("\nРазбор:")
            print("Статус:", parsed.get("status"))
            print("Сообщение:", parsed.get("message"))
            print("Данные:")
            print(json.dumps(parsed.get("data"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
