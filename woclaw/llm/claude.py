"""
Claude LLM 提供者
"""

from typing import Any, AsyncIterator

from woclaw.config import LLMConfig
from woclaw.llm.base import BaseLLM
from woclaw.llm.registry import register_llm


@register_llm("claude")
class ClaudeLLM(BaseLLM):
    """
    Anthropic Claude API 封装
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Please install anthropic: pip install anthropic")
        return self._client
    
    async def generate(self, prompt: str) -> dict[str, Any]:
        response = await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "content": response.content[0].text,
            "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        }
    
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        response = await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=messages
        )
        return {
            "content": response.content[0].text,
            "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        }
