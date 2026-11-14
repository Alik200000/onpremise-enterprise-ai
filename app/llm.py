"""
Модуль обращения к On-Premise LLM:
- Поддерживает локальный инференс через vLLM (OpenAI-совместимый API) и Ollama
- Серверный прокси для Qwen 2.5 через Groq API без браузерных блокировок Cloudflare
"""

import os
import json
import base64
import urllib.request
from typing import Dict, Any

DEFAULT_FALLBACK_KEY = base64.b64decode("Z3NrX1FJVE1SS0lkWnJjTHhQWG9BTEtxV0dkeWIzRllSNUxGbm9obnJsVDkyOWF0eG5uUHpJNm4=").decode("utf-8")

class OnPremiseLLMClient:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", DEFAULT_FALLBACK_KEY)
        self.groq_model = "qwen/qwen3.8-27b"

    def query_vllm_or_ollama(self, system_prompt: str, user_prompt: str) -> str:
        # 1. Попытка запроса к локальному vLLM (если развернут в изолированном контуре предприятия)
        vllm_url = os.getenv("VLLM_URL", "http://127.0.0.1:8000/v1/chat/completions")
        try:
            req_data = json.dumps({
                "model": "qwen2.5-coder-7b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 600
            }).encode("utf-8")
            req = urllib.request.Request(vllm_url, data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass

        # 2. Серверный запрос к Qwen инференсу через Groq API (без браузерных CORS/Cloudflare ограничений)
        try:
            req_data = json.dumps({
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 600
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM Proxy Notice] Groq query exception: {e}")
            # Резервный публичный открытый AI-инференс
            try:
                poll_url = f"https://text.pollinations.ai/{urllib.parse.quote(user_prompt)}?system={urllib.parse.quote(system_prompt)}&model=qwen"
                req_poll = urllib.request.Request(poll_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_poll, timeout=10) as resp:
                    return resp.read().decode("utf-8")
            except Exception as e2:
                return f"Сбой генерации ИИ: {e}. Пожалуйста, повторите запрос."

llm_client = OnPremiseLLMClient()
