"""
LLM 注册表
统一管理所有 LLM 适配器
"""

from typing import Optional
from .base import BaseLLM
from .openai_llm import OpenAILLM, ClaudeLLM, OllamaLLM, DeepSeekLLM, KimiLLM, QwenLLM


class LLMRegistry:
    """
    LLM 注册表
    提供统一的 LLM 获取接口
    """

    _providers = {
        "openai": OpenAILLM,
        "claude": ClaudeLLM,
        "anthropic": ClaudeLLM,
        "ollama": OllamaLLM,
        "deepseek": DeepSeekLLM,
        "kimi": KimiLLM,
        "moonshot": KimiLLM,
        "qwen": QwenLLM,
        "dashscope": QwenLLM,
        "gemini": None,  # 暂不支持
    }

    _instances = {}

    @classmethod
    def get(cls, provider: str) -> BaseLLM:
        """
        获取 LLM 实例

        Args:
            provider: 提供商名称
                - openai: OpenAI GPT 系列
                - claude / anthropic: Claude 系列
                - ollama: 本地 Ollama 模型
                - deepseek: DeepSeek
                - kimi / moonshot: Kimi
                - qwen / dashscope: 通义千问
        """
        provider = provider.lower()

        if provider not in cls._instances:
            llm_class = cls._providers.get(provider)
            if llm_class:
                cls._instances[provider] = llm_class()
            else:
                # 默认使用 Ollama（如果可用）
                cls._instances[provider] = OllamaLLM()

        return cls._instances[provider]

    @classmethod
    def list_providers(cls) -> list[str]:
        """列出支持的提供商"""
        return list(cls._providers.keys())

    @classmethod
    def get_info(cls, provider: str) -> dict:
        """获取提供商信息"""
        info = {
            "openai": {
                "name": "OpenAI",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                "requires_api_key": True,
                "api_env": "OPENAI_API_KEY",
                "description": "OpenAI 的 GPT 系列模型",
            },
            "claude": {
                "name": "Claude",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                "requires_api_key": True,
                "api_env": "ANTHROPIC_API_KEY",
                "description": "Anthropic 的 Claude 系列模型",
            },
            "ollama": {
                "name": "Ollama (本地)",
                "models": ["llama3.2", "qwen2.5", "codellama", "mistral", "phi3"],
                "requires_api_key": False,
                "api_env": None,
                "description": "本地运行的模型，完全免费",
            },
            "deepseek": {
                "name": "DeepSeek",
                "models": ["deepseek-chat", "deepseek-coder"],
                "requires_api_key": True,
                "api_env": "DEEPSEEK_API_KEY",
                "description": "DeepSeek 的经济实惠模型",
            },
            "kimi": {
                "name": "Kimi",
                "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
                "requires_api_key": True,
                "api_env": "MOONSHOT_API_KEY",
                "description": "月之暗面的 Kimi 模型",
            },
            "qwen": {
                "name": "通义千问",
                "models": ["qwen-plus", "qwen-max", "qwen-turbo"],
                "requires_api_key": True,
                "api_env": "DASHSCOPE_API_KEY",
                "description": "阿里云的通义千问模型",
            },
        }

        return info.get(provider.lower(), {})

    @classmethod
    def reset(cls):
        """重置所有实例"""
        cls._instances = {}
