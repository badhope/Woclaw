"""
OpenAI LLM 适配
支持 GPT-4o、GPT-4、GPT-3.5 等
"""

import os
from typing import Any

from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """OpenAI LLM"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = "gpt-4o"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))
            temperature = kwargs.pop("temperature", self.config.get("temperature", 0.7))
            max_tokens = kwargs.pop("max_tokens", self.config.get("max_tokens", 4096))

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            }

        except ImportError:
            return await self._mock_generate(prompt)
        except Exception as e:
            return {"content": f"OpenAI API 错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
            }

        except ImportError:
            return {"content": "请安装 openai: pip install openai"}
        except Exception as e:
            return {"content": f"OpenAI API 错误: {str(e)}", "error": True}

    async def _mock_generate(self, prompt: str) -> dict:
        """模拟生成（未安装 openai 时）"""
        return {
            "content": f"[模拟响应] 收到消息: {prompt[:100]}...",
            "model": "mock",
            "note": "请安装 openai: pip install openai"
        }


class ClaudeLLM(BaseLLM):
    """Claude LLM (Anthropic)"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = "claude-3-5-sonnet-20241022"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=self.api_key or self.config.get("api_key"))

            model = kwargs.pop("model", self.config.get("model", self.model))
            max_tokens = kwargs.pop("max_tokens", self.config.get("max_tokens", 4096))

            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return {
                "content": response.content[0].text,
                "model": model,
                "stop_reason": response.stop_reason,
            }

        except ImportError:
            return {"content": "请安装 anthropic: pip install anthropic"}
        except Exception as e:
            return {"content": f"Claude API 错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        # 转换消息格式
        anthropic_messages = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "assistant"
            anthropic_messages.append({"role": role, "content": msg.get("content", "")})

        return await self.generate("\n".join([m["content"] for m in anthropic_messages]), **kwargs)


class OllamaLLM(BaseLLM):
    """Ollama 本地模型"""

    def __init__(self):
        super().__init__()
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = "llama3.2"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            import aiohttp

            model = kwargs.pop("model", self.config.get("model", self.model))

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "content": data.get("response", ""),
                            "model": model,
                            "done": data.get("done", True),
                        }
                    else:
                        error = await resp.text()
                        return {"content": f"Ollama 错误: {error}", "error": True}

        except ImportError:
            return {"content": "请安装 aiohttp: pip install aiohttp"}
        except Exception as e:
            return {"content": f"Ollama 连接错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        try:
            import aiohttp

            model = kwargs.pop("model", self.config.get("model", self.model))

            # 转换消息格式
            ollama_messages = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={"model": model, "messages": ollama_messages, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "content": data.get("message", {}).get("content", ""),
                            "model": model,
                        }
                    else:
                        error = await resp.text()
                        return {"content": f"Ollama 错误: {error}", "error": True}

        except ImportError:
            return {"content": "请安装 aiohttp: pip install aiohttp"}
        except Exception as e:
            return {"content": f"Ollama 连接错误: {str(e)}", "error": True}

    async def list_models(self) -> list[str]:
        """列出可用模型"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m.get("name", "") for m in data.get("models", [])]
                    return []
        except Exception:
            return []


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except ImportError:
            return {"content": "请安装 openai: pip install openai"}
        except Exception as e:
            return {"content": f"DeepSeek API 错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except Exception as e:
            return {"content": f"DeepSeek API 错误: {str(e)}", "error": True}


class KimiLLM(BaseLLM):
    """Kimi (Moonshot) LLM"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("MOONSHOT_API_KEY", "")
        self.base_url = "https://api.moonshot.cn/v1"
        self.model = "moonshot-v1-8k"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except ImportError:
            return {"content": "请安装 openai: pip install openai"}
        except Exception as e:
            return {"content": f"Kimi API 错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except Exception as e:
            return {"content": f"Kimi API 错误: {str(e)}", "error": True}


class QwenLLM(BaseLLM):
    """通义千问 LLM"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-plus"

    async def generate(self, prompt: str, **kwargs) -> Any:
        """生成响应"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except ImportError:
            return {"content": "请安装 openai: pip install openai"}
        except Exception as e:
            return {"content": f"通义千问 API 错误: {str(e)}", "error": True}

    async def chat(self, messages: list[dict], **kwargs) -> Any:
        """多轮对话"""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key or self.config.get("api_key"), base_url=self.base_url)

            model = kwargs.pop("model", self.config.get("model", self.model))

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": model,
            }

        except Exception as e:
            return {"content": f"通义千问 API 错误: {str(e)}", "error": True}
