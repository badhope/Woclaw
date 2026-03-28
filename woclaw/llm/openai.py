"""
OpenAI LLM 提供者
"""

from typing import Any, AsyncIterator

from woclaw.config import LLMConfig
from woclaw.llm.base import BaseLLM
from woclaw.llm.registry import register_llm


@register_llm("openai")
class OpenAILLM(BaseLLM):
    """
    OpenAI API 封装
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url
                )
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    async def generate(self, prompt: str) -> dict[str, Any]:
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.model_dump() if response.usage else None
        }
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.model_dump() if response.usage else None
        }
