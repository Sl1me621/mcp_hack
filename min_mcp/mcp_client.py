import asyncio
import json
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()


def safe_parse_json(text):
    """Безопасно парсит JSON или возвращает исходный текст"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


async def test_demo_server():
    """Полноценное тестирование Demo Assistant MCP-сервера."""

    print("🤖 Подключаемся к Demo Assistant серверу...")
    client = Client("http://127.0.0.1:8000/mcp/")

    async with client:
        try:
            # Проверяем соединение
            print("✅ Сервер запущен!\n")

            # Получаем возможности сервера
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()

            # Отображаем что доступно
            print(f"🔧 Доступно инструментов: {len(tools)}")
            for tool in tools:
                print(f"   • {tool.name}: {tool.description}")

            print(f"\n📚 Доступно ресурсов: {len(resources)}")
            for resource in resources:
                print(f"   • {resource.uri}")

            print(f"\n💭 Доступно промптов: {len(prompts)}")
            for prompt in prompts:
                print(f"   • {prompt.name}: {prompt.description}")

            print("\n🧪 ТЕСТИРУЕМ ФУНКЦИОНАЛ:")
            print("-" * 50)

            # === ТЕСТИРУЕМ ИНСТРУМЕНТЫ ===

            # 1. Тест расчета возраста
            print("1️⃣ Тестируем calculate_age:")
            result = await client.call_tool("calculate_age", {"birth_year": 1990})
            age_data = safe_parse_json(result.content[0].text)
            print(f"   Возраст человека 1990 г.р.: {age_data} лет")

            # 2. Тест генерации пароля
            print("\n2️⃣ Тестируем generate_password:")
            result = await client.call_tool("generate_password", {"length": 16})
            password_data = safe_parse_json(result.content[0].text)
            print(f"   Сгенерированный пароль (16 символов): {password_data}")

            # === ТЕСТИРУЕМ РЕСУРСЫ ===

            # 3. Тест системного статуса
            print("\n3️⃣ Читаем system://status:")
            resource = await client.read_resource("system://status")
            status_content = resource[0].text
            status_data = safe_parse_json(status_content)
            print(f"   Статус системы: {status_data['status']}")
            print(f"   Время: {status_data['timestamp']}")
            print(f"   Версия: {status_data['version']}")

            # 4. Тест динамического ресурса помощи
            print("\n4️⃣ Читаем help://password:")
            resource = await client.read_resource("help://password")
            help_content = resource[0].text
            print(f"   Справка: {help_content}")

            # === ТЕСТИРУЕМ ПРОМПТЫ ===

            # 5. Тест промпта безопасности
            print("\n5️⃣ Генерируем security_check промпт:")
            prompt = await client.get_prompt("security_check", {
                "action": "открыть порт 3000 на сервере"
            })
            security_prompt = prompt.messages[0].content.text
            print(f"   Промпт создан (длина: {len(security_prompt)} символов)")
            print(f"   Начало: {security_prompt[:100]}...")

            # 6. Тест промпта объяснения
            print("\n6️⃣ Генерируем explain_result промпт:")
            prompt = await client.get_prompt("explain_result", {
                "tool_name": "generate_password",
                "result": "Tj9$mK2pL8qX"
            })
            explain_prompt = prompt.messages[0].content.text
            print(f"   Промпт создан (длина: {len(explain_prompt)} символов)")
            print(f"   Начало: {explain_prompt[:100]}...")

            print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("📊 Статистика:")
            print(f"   ✅ Инструментов протестировано: 2/{len(tools)}")
            print(f"   ✅ Ресурсов протестировано: 2/{len(resources)}")
            print(f"   ✅ Промптов протестировано: 2/{len(prompts)}")

        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_demo_server())
