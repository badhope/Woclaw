"""
Agent 核心测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from woclaw.config import Config, LLMConfig
from woclaw.agent.core import Agent, TaskResult


@pytest.fixture
def config():
    return Config(
        llm=LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test-key"
        )
    )


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate = AsyncMock(return_value={
        "content": "测试响应",
        "usage": {"input_tokens": 10, "output_tokens": 20}
    })
    return llm


@pytest.mark.asyncio
async def test_agent_understand(config, mock_llm):
    """测试任务理解"""
    with patch("woclaw.agent.core.get_llm", return_value=mock_llm):
        agent = Agent(config)
        result = await agent._understand("测试任务")
        
        assert "content" in result
        mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_agent_run_success(config, mock_llm):
    """测试完整任务执行"""
    with patch("woclaw.agent.core.get_llm", return_value=mock_llm):
        agent = Agent(config)
        result = await agent.run("测试任务")
        
        assert isinstance(result, TaskResult)
        assert result.success is True
        assert len(result.steps) > 0


def test_agent_run_sync(config, mock_llm):
    """测试同步执行"""
    with patch("woclaw.agent.core.get_llm", return_value=mock_llm):
        agent = Agent(config)
        result = agent.run_sync("测试任务")
        
        assert isinstance(result, TaskResult)
