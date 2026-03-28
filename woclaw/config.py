"""
Woclaw 配置模块
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "woclaw"
    user: str = "postgres"
    password: str = ""


@dataclass
class BrowserConfig:
    headless: bool = True
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    timeout: int = 30000


@dataclass
class ConcurrencyConfig:
    max_workers: int = 4
    task_timeout: int = 300
    retry_times: int = 3
    retry_delay: float = 1.0


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    concurrency: ConcurrencyConfig = field(default_factory=ConcurrencyConfig)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        return cls(
            llm=LLMConfig(**data.get("llm", {})),
            database=DatabaseConfig(**data.get("database", {})),
            browser=BrowserConfig(**data.get("browser", {})),
            concurrency=ConcurrencyConfig(**data.get("concurrency", {})),
        )
