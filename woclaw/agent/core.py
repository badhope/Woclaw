"""
Woclaw Agent 核心
"""

import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field

from woclaw.config import Config
from woclaw.agent.planner import Planner
from woclaw.agent.memory import Memory
from woclaw.agent.executor import Executor
from woclaw.llm import get_llm
from woclaw.tools import ToolRegistry


@dataclass
class TaskResult:
    success: bool
    output: Any
    error: Optional[str] = None
    steps: list[dict[str, Any]] = field(default_factory=list)


class Agent:
    """
    自主智能体核心类
    
    工作流程:
    1. 理解任务 (Understand)
    2. 规划步骤 (Plan)
    3. 执行操作 (Execute)
    4. 验证结果 (Verify)
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = get_llm(config.llm)
        self.planner = Planner(self.llm)
        self.memory = Memory(config.database)
        self.executor = Executor(config.concurrency)
        self.tools = ToolRegistry()
        
    async def run(self, task: str) -> TaskResult:
        """
        执行任务的主入口
        """
        steps = []
        
        try:
            understood = await self._understand(task)
            steps.append({"phase": "understand", "result": understood})
            
            plan = await self.planner.plan(understood)
            steps.append({"phase": "plan", "result": [step.__dict__ for step in plan]})
            
            executed = await self.executor.execute(plan, self.tools)
            steps.append({"phase": "execute", "result": executed})
            
            verified = await self._verify(executed)
            steps.append({"phase": "verify", "result": verified})
            
            await self.memory.save(task, steps)
            
            return TaskResult(
                success=True,
                output=verified,
                steps=steps
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                output=None,
                error=str(e),
                steps=steps
            )
    
    async def _understand(self, task: str) -> dict[str, Any]:
        """
        理解任务意图和上下文
        """
        prompt = f"""分析以下任务，提取关键信息：
        
任务: {task}

请返回 JSON 格式:
{{
    "task_type": "任务类型",
    "required_tools": ["需要的工具列表"],
    "expected_output": "预期输出",
    "potential_risks": ["潜在风险"]
}}
"""
        return await self.llm.generate(prompt)
    
    async def _verify(self, result: Any) -> Any:
        """
        验证执行结果
        """
        return result
    
    def run_sync(self, task: str) -> TaskResult:
        """
        同步执行任务
        """
        return asyncio.run(self.run(task))
