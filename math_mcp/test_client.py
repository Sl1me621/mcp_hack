

import asyncio
from fastmcp import Client
import json


def safe(text):
    """Попытка распарсить JSON, иначе вернуть строку"""
    try:
        return json.loads(text)
    except:
        return text


async def main():

    print("🚀 Подключаюсь к математическому MCP-серверу...")

    # URL твоего сервера — ТОЧНО такой, как показало при запуске server.py
    client = Client("http://127.0.0.1:8000/mcp")

    # Контекстный менеджер — внутри client подключается
    async with client:

        print("✅ Соединение установлено!\n")

        # === Инструменты ===
        tools = await client.list_tools()
        print(f"🔧 Найдено инструментов: {len(tools)}")
        for t in tools:
            print(f"  • {t.name}: {t.description}")

        # === Ресурсы ===
        resources = await client.list_resources()
        print(f"\n📚 Найдено ресурсов: {len(resources)}")
        for r in resources:
            print(f"  • {r.uri}")

        # === Промпты ===
        prompts = await client.list_prompts()
        print(f"\n💬 Найдено промптов: {len(prompts)}")
        for p in prompts:
            print(f"  • {p.name}: {p.description}")

        print("\n🧪 ТЕСТ: вызываем инструмент 'server_info'...\n")
        result = await client.call_tool("server_info", {})
        content = result.content[0].text
        parsed = safe(content)

        print("📄 Ответ сервера:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))

        print("\n🎉 Клиент успешно пообщался с MCP-сервером!")


if __name__ == "__main__":
    asyncio.run(main())
