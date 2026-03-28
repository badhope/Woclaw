"""
Ollama 本地模型提供者
"""

from typing import Any, AsyncIterator

from woclaw.config import LLMConfig
from woclaw.llm.base import BaseLLM
from woclaw.llm.registry import register_llm


@register_llm("ollama")
class OllamaLLM(BaseLLM):
    """
    Ollama 本地模型封装
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
    
    async def _request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/{endpoint}",
                json=data
            ) as response:
                return await response.json()
    
    async def generate(self, prompt: str) -> dict[str, Any]:
        response = await self._request("generate", {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        })
        return {
            "content": response.get("response", ""),
            "usage": None
        }
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": True
                }
            ) as response:
                async for line in response.content:
                    import json
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
    
    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        response = await self._request("chat", {
            "model": self.config.model,
            "messages": messages,
            "stream": False
        })
        return {
            "content": response.get("message", {}).get("content", ""),
            "usage": None
        }
