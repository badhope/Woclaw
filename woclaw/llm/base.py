"""
LLM 基类
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseLLM(ABC):
    """
    LLM 抽象基类
    """
    
    @abstractmethod
    async def generate(self, prompt: str) -> dict[str, Any]:
        """
        生成响应
        """
        pass
    
    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """
        流式生成响应
        """
        pass
    
    @abstractmethod
    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """
        多轮对话
        """
        pass
