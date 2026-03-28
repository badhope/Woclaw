"""
配置测试
"""

import pytest

from woclaw.config import Config, LLMConfig, DatabaseConfig, BrowserConfig, ConcurrencyConfig


def test_default_config():
    """测试默认配置"""
    config = Config()
    
    assert config.llm.provider == "openai"
    assert config.llm.model == "gpt-4"
    assert config.database.host == "localhost"
    assert config.database.port == 5432
    assert config.browser.headless is True
    assert config.concurrency.max_workers == 4


def test_config_from_dict():
    """测试从字典创建配置"""
    data = {
        "llm": {
            "provider": "claude",
            "model": "claude-3-opus",
            "api_key": "test-key"
        },
        "database": {
            "host": "db.example.com",
            "port": 5433
        }
    }
    
    config = Config.from_dict(data)
    
    assert config.llm.provider == "claude"
    assert config.llm.model == "claude-3-opus"
    assert config.llm.api_key == "test-key"
    assert config.database.host == "db.example.com"
    assert config.database.port == 5433


def test_llm_config():
    """测试 LLM 配置"""
    config = LLMConfig(
        provider="ollama",
        model="llama2",
        base_url="http://localhost:11434"
    )
    
    assert config.provider == "ollama"
    assert config.model == "llama2"
    assert config.base_url == "http://localhost:11434"


def test_concurrency_config():
    """测试并发配置"""
    config = ConcurrencyConfig(
        max_workers=8,
        task_timeout=600,
        retry_times=5
    )
    
    assert config.max_workers == 8
    assert config.task_timeout == 600
    assert config.retry_times == 5
