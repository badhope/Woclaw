"""
任务规划器
"""

import json
import re
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
        prompt = f"""你是一个任务规划专家。请将以下任务分解为具体步骤。

任务信息: {task_info}

可用工具:
- filesystem: 文件操作 (read, write, copy, move, delete, list, search)
- shell: 执行命令 (run)
- browser: 浏览器操作 (navigate, click, type, screenshot, content)
- web: HTTP请求 (get, post, download)
- data: 数据处理 (read_json, write_json, read_csv, write_csv)
- process: 进程管理 (list, find, start, kill)
- clipboard: 剪贴板 (read, write, clear)
- system: 系统信息 (info, cpu, memory, disk, network)
- network: 网络工具 (download, dns, port_scan, ping)
- screenshot: 截图 (full, region, window)
- automation: 键盘鼠标 (key_press, key_hotkey, mouse_click, mouse_move)
- archive: 压缩解压 (compress, extract)
- image: 图像处理 (resize, convert, crop, filter)

请严格返回以下 JSON 格式（不要包含其他文字）:
{{
    "steps": [
        {{
            "action": "动作描述",
            "tool": "工具名称",
            "params": {{"参数名": "参数值"}},
            "dependencies": []
        }}
    ]
}}
"""
        response = await self.llm.generate(prompt)
        return self._parse_steps(response)
    
    def _parse_steps(self, response: dict[str, Any] | str) -> list[Step]:
        """
        解析 LLM 返回的步骤
        """
        if isinstance(response, dict):
            content = response.get("content", "")
        else:
            content = str(response)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
        except json.JSONDecodeError:
            return [Step(
                id=0,
                action="直接执行任务",
                tool="shell",
                params={"command": content},
                dependencies=[]
            )]
        
        steps = []
        for i, step_data in enumerate(data.get("steps", [])):
            steps.append(Step(
                id=i,
                action=step_data.get("action", ""),
                tool=step_data.get("tool", ""),
                params=step_data.get("params", {}),
                dependencies=step_data.get("dependencies", [])
            ))
        return steps
