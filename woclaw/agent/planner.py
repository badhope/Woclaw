"""
任务规划器
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class Step:
    id: int
    action: str
    tool: str
    params: dict[str, Any]
    dependencies: list[int]


class Planner:
    """
    任务分解与规划
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    async def plan(self, task_info: dict[str, Any]) -> list[Step]:
        """
        将任务分解为可执行的步骤
        """
        prompt = f"""将以下任务分解为具体步骤：

任务信息: {task_info}

请返回 JSON 格式的步骤列表，每个步骤包含:
- action: 动作描述
- tool: 使用的工具名称
- params: 工具参数
- dependencies: 依赖的步骤ID列表
"""
        response = await self.llm.generate(prompt)
        return self._parse_steps(response)
    
    def _parse_steps(self, response: dict[str, Any]) -> list[Step]:
        """
        解析 LLM 返回的步骤
        """
        steps = []
        for i, step_data in enumerate(response.get("steps", [])):
            steps.append(Step(
                id=i,
                action=step_data.get("action", ""),
                tool=step_data.get("tool", ""),
                params=step_data.get("params", {}),
                dependencies=step_data.get("dependencies", [])
            ))
        return steps
