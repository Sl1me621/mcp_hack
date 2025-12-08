# client_a2a.py

import json
import uuid
import requests

A2A_URL = "http://127.0.0.1:8001/a2a"  # адрес твоего A2A-агента


def pretty_print_response(resp_json: dict) -> None:
    """Красиво печатает ответ A2A: сначала tool, потом agent."""
    messages = resp_json.get("messages", [])

    # Сначала покажем, что сделал TOOL (если был)
    for msg in messages:
        if msg.get("role") == "tool":
            print("\n[TOOL]:")
            for c in msg.get("contents", []):
                if c.get("type") == "tool_result":
                    tool_name = c.get("tool_name")
                    tool_output = c.get("tool_output")
                    print(f"  инструмент: {tool_name}")
                    print("  результат MCP (сырой JSON):")
                    print(json.dumps(tool_output, indent=2, ensure_ascii=False))

    # Потом покажем ответ AGENT
    for msg in messages:
        if msg.get("role") == "agent":
            print("\n[AGENT]:")
            for c in msg.get("contents", []):
                if c.get("type") == "text" and c.get("text"):
                    print(c["text"])


def build_request_body(session_id: str, user_text: str) -> dict:
    """Собирает тело A2ARequest по нашей схеме."""
    return {
        "session_id": session_id,
        "trace_id": str(uuid.uuid4()),
        "locale": "ru-RU",
        "user_id": "local-user",
        "messages": [
            {
                "role": "user",
                "contents": [
                    {
                        "type": "text",
                        "text": user_text,
                    }
                ],
                "meta": {},
            }
        ],
        "context": {},
    }


def main() -> None:
    session_id = str(uuid.uuid4())
    print(f"Старт сессии: {session_id}")
    print("Подсказка: 'calc: 2 + 2 * 3' → агент вызовет MCP calculate_basic\n")

    while True:
        try:
            user_text = input("YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit", "q"}:
            print("Выход.")
            break

        body = build_request_body(session_id, user_text)

        try:
            resp = requests.post(A2A_URL, json=body, timeout=60)
        except Exception as e:
            print(f"Ошибка запроса к агенту: {e}")
            continue

        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}: {resp.text}")
            continue

        try:
            resp_json = resp.json()
        except Exception as e:
            print(f"Не удалось распарсить JSON-ответ агента: {e}")
            print(resp.text)
            continue

        pretty_print_response(resp_json)
        print()  # пустая строка для разделения диалога


if __name__ == "__main__":
    main()
