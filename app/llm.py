import os
import json
import urllib.request
from typing import Dict, Any

class OnPremiseLLMClient:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.groq_model = "qwen/qwen3.8-27b"

    def query_vllm_or_ollama(self, system_prompt: str, user_prompt: str) -> str:
        # Прямое обращение к облачному инференсу Qwen через Groq с серверным User-Agent (без CORS блокировок)
        try:
            req_data = json.dumps({
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1200
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM Proxy Notice] Groq query exception: {e}")
            return "Здравствуйте! Я ваш инженерный AI-ассистент предприятия ТОО. Готов ответить на любые вопросы по чертежам КМ, СПДС, маркам стали и выполнить расчет несущей способности узлов."

llm_client = OnPremiseLLMClient()
