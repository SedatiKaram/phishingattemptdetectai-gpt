import os, json, httpx, asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMClientBase:
    async def call(self, system: str, user: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{self.base_url}/chat/completions",
                                  headers=headers, json=payload)
            if r.status_code != 200:
                print("\n--- OpenAI error details ---")
                print("Status:", r.status_code)
                print("Body:", r.text)
                print("--- end ---\n")
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]


    @staticmethod
    def parse_json(text: str) -> Dict[str, Any]:
        return json.loads(text)

class OpenAICompatibleClient(LLMClientBase):
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    async def call(self, system: str, user: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
def get_llm_client() -> LLMClientBase:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY environment variable is not set.\n"
            "Set LLM_API_KEY to your OpenAI API key or restore the mock at archive/app/llm_client_mock.py for local testing.\n"
            "To use the mock, copy archive/app/llm_client_mock.py into app/ and modify get_llm_client accordingly."
        )
    return OpenAICompatibleClient()
