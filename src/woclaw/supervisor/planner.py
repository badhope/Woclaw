"""
Planner - 任务规划器
将复杂任务拆解为可执行步骤
"""

import json
import re
from typing import Any


class Planner:
    """
    任务规划器
    使用 ReAct + ToT 混合模式
    """

    def __init__(self, llm: Any):
        self.llm = llm

    async def plan(self, task_description: str, available_tools: list[str]) -> dict:
        """
        规划任务执行步骤

        Args:
            task_description: 任务描述
            available_tools: 可用工具列表

        Returns:
            执行计划字典
        """
        tools_desc = self._format_tools(available_tools)

        prompt = f"""你是一个任务规划专家。请将复杂任务拆解为简单步骤。

任务：{task_description}

可用工具：
{tools_desc}

要求：
1. 每个步骤尽量简单，只做一件事
2. 考虑步骤之间的依赖关系
3. 预估每个步骤的执行时间
4. 识别潜在风险点

请返回详细的执行计划（JSON 格式）：
{{
    "goal": "任务目标",
    "steps": [
        {{
            "id": 1,
            "description": "步骤描述",
            "tool": "使用的工具",
            "params": {{"参数"}},
            "depends_on": [],
            "estimated_time": 5,
            "risk": "low/medium/high"
        }}
    ],
    "total_estimated_time": 60,
    "overall_risk": "low/medium/high"
}}
"""

        try:
            response = await self.llm.generate(prompt)
            content = self._extract_json(response)

            if content:
                return json.loads(content)
        except Exception as e:
            print(f"规划失败: {e}")

        # 默认回退计划
        return {
            "goal": task_description,
            "steps": [
                {
                    "id": 1,
                    "description": f"执行命令: {task_description}",
                    "tool": "shell",
                    "params": {"command": task_description},
                    "depends_on": [],
                    "estimated_time": 30,
                    "risk": "medium"
                }
            ],
            "total_estimated_time": 30,
            "overall_risk": "medium"
        }

    def _format_tools(self, tools: list[str]) -> str:
        """格式化工具列表"""
        tool_docs = {
            "shell": "shell - 执行系统命令",
            "file_worker": "file_worker - 文件操作（读、写、移动、删除）",
            "gui_worker": "gui_worker - GUI 操控（点击、输入、窗口操作）",
            "code_worker": "code_worker - 代码执行和调试",
            "web_worker": "web_worker - HTTP 请求、网页抓取",
            "sys_worker": "sys_worker - 系统信息、进程管理",
            "browser_worker": "browser_worker - 浏览器自动化",
        }

        lines = []
        for tool in tools:
            lines.append(f"- {tool_docs.get(tool, tool)}")
        return "\n".join(lines)

    def _extract_json(self, response: Any) -> str:
        """从响应中提取 JSON"""
        if isinstance(response, dict):
            content = response.get("content", str(response))
        else:
            content = str(response)

        # 尝试找到 JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json_match.group()

        return content

    async def should_retry(self, failed_step: dict, error: str) -> tuple[bool, str]:
        """
        判断是否应该重试

        Returns:
            (是否重试, 替代方案描述)
        """
        prompt = f"""分析以下失败情况，决定是否重试：

失败步骤：{failed_step.get('description')}
错误信息：{error}

可选方案：
1. 重试 - 原样重试
2. 重试(改进) - 改进参数重试
3. 跳过 - 放弃这个步骤继续下一步
4. 终止 - 任务无法完成

请分析并给出建议：
- 这个错误是什么原因？
- 应该重试还是换方案？
- 如果重试，怎么改进？
"""
        try:
            response = await self.llm.generate(prompt)
            content = self._extract_json(response)

            if content:
                data = json.loads(content)
                should_retry = data.get("retry", True)
                alternative = data.get("alternative", "")
                return should_retry, alternative
        except Exception:
            pass

        return True, "原样重试"
