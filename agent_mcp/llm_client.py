# agent_service/llm_client.py

import os
from typing import List, Dict, Any

from openai import OpenAI

# Ключ и базовый URL берём из env
API_KEY = os.getenv("EVOLUTION_API_KEY")
BASE_URL = os.getenv("EVOLUTION_BASE_URL", "https://foundation-models.api.cloud.ru/v1")
MODEL_NAME = os.getenv("EVOLUTION_MODEL", "Qwen/Qwen3-235B-A22B-Instruct-2507")

if not API_KEY:
    raise RuntimeError("Переменная окружения EVOLUTION_API_KEY не задана")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def ask_llm(
    messages: List[Dict[str, Any]],
    max_tokens: int = 1024,
    temperature: float = 0.3,
    top_p: float = 0.95,
) -> str:
    """
    Вызов Evolution Foundation Models через OpenAI SDK.
    messages — список [{role: 'system'|'user'|'assistant', content: '...'}, ...]
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        presence_penalty=0,
        messages=messages,
    )
    return response.choices[0].message.content
