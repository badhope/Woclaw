"""
任务执行器
"""

import asyncio
from typing import Any
from concurrent.futures import ProcessPoolExecutor

from woclaw.agent.planner import Step
from woclaw.config import ConcurrencyConfig


class Executor:
    """
    任务执行调度器
    """
    
    def __init__(self, config: ConcurrencyConfig):
        self.config = config
        self._pool = ProcessPoolExecutor(max_workers=config.max_workers)
    
    async def execute(self, steps: list[Step], tools) -> dict[str, Any]:
        """
        执行步骤列表
        """
        results = {}
        completed = set()
        
        while len(completed) < len(steps):
            for step in steps:
                if step.id in completed:
                    continue
                
                if not all(dep in completed for dep in step.dependencies):
                    continue
                
                result = await self._execute_step(step, tools)
                results[step.id] = result
                completed.add(step.id)
        
        return results
    
    async def _execute_step(self, step: Step, tools) -> Any:
        """
        执行单个步骤
        """
        tool = tools.get(step.tool)
        if not tool:
            raise ValueError(f"Tool not found: {step.tool}")
        
        for attempt in range(self.config.retry_times):
            try:
                return await tool.execute(**step.params)
            except Exception as e:
                if attempt == self.config.retry_times - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
