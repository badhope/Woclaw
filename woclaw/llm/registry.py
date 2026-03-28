"""
LLM 注册中心
"""

from typing import Any, Type
from woclaw.config import LLMConfig
from woclaw.llm.base import BaseLLM

_registry: dict[str, Type[BaseLLM]] = {}


def register_llm(name: str):
    """
    注册 LLM 提供者
    """
    def decorator(cls: Type[BaseLLM]) -> Type[BaseLLM]:
        _registry[name] = cls
        return cls
    return decorator


def get_llm(config: LLMConfig) -> BaseLLM:
    """
    获取 LLM 实例
    """
    provider = config.provider.lower()
    
    if provider not in _registry:
        raise ValueError(f"Unknown LLM provider: {provider}")
    
    return _registry[provider](config)
