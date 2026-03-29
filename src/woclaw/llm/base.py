"""
LLM 适配层基类
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseLLM(ABC):
    """LLM 基类"""

    def __init__(self):
        self.config = {}

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Any:
        """
        生成响应

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            响应内容
        """
        pass

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """
        多轮对话

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]

        Returns:
            响应内容
        """
        pass

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式生成（可选实现）"""
        response = await self.generate(prompt, **kwargs)
        yield response

    def configure(self, config: dict):
        """配置"""
        self.config.update(config)
