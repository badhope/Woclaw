"""
Woclaw 配置示例
复制此文件为 config.py 并填入你的 API Key
"""

from woclaw import Config

# 方式1: 使用 OpenAI
config = Config(
    llm={
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-your-openai-api-key-here",
    }
)

# 方式2: 使用 Claude
# config = Config(
#     llm={
#         "provider": "claude",
#         "model": "claude-3-opus-20240229",
#         "api_key": "sk-ant-your-claude-api-key-here",
#     }
# )

# 方式3: 使用 Ollama 本地模型
# config = Config(
#     llm={
#         "provider": "ollama",
#         "model": "llama2",
#         "base_url": "http://localhost:11434",
#     }
# )
