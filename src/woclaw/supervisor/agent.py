"""
Woclaw Supervisor Agent - 启明星的核心决策者
负责任务理解、规划、审批、执行调度
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from ..llm.registry import LLMRegistry
from ..learning.memory import LearningMemory


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"      # 直接执行
    MEDIUM = "medium"  # 需要确认
    HIGH = "high"    # 禁止或需密码


class TaskType(Enum):
    """任务类型"""
    CHAT = "chat"           # 闲聊/问答
    FILE_OP = "file_op"      # 文件操作
    GUI_OP = "gui_op"       # GUI 操控
    CODE_EXEC = "code_exec" # 代码执行
    WEB_OP = "web_op"       # 网络操作
    SYS_OP = "sys_op"       # 系统操作
    UNKNOWN = "unknown"     # 未知


@dataclass
class Task:
    """任务"""
    id: str
    description: str
    task_type: TaskType = TaskType.UNKNOWN
    raw_message: str = ""
    context: dict = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """执行计划"""
    task_id: str
    steps: list[dict]
    risk_level: RiskLevel = RiskLevel.LOW
    estimated_time: int = 60
    worker: str = "shell"
    reasoning: str = ""


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    plan: Optional[ExecutionPlan] = None
    steps: list[dict] = field(default_factory=list)


class Supervisor:
    """
    启明星的核心决策者
    工作流程：
    1. 理解用户意图
    2. 判断任务类型
    3. 简单任务直接回复，复杂任务拆解规划
    4. 审批 Worker 的执行计划
    5. 调度执行
    6. 验证结果
    7. 整合返回
    """

    def __init__(self, config: dict):
        self.config = config
        self.llm = LLMRegistry.get(config.get("llm", {}).get("provider", "openai"))
        self.llm.configure(config.get("llm", {}))
        
        # 加载学习记忆
        self.memory = LearningMemory()
        self._learnings_loaded = False
        
        # 任务历史
        self.task_history: list[Task] = []
        
        # Worker 注册
        self.workers: dict[str, Any] = {}
        
    async def load_learnings(self):
        """加载学习记忆"""
        if not self._learnings_loaded:
            await self.memory.load()
            self._learnings_loaded = True
            
    def register_worker(self, name: str, worker: Any):
        """注册 Worker"""
        self.workers[name] = worker
        
    async def process(self, message: str) -> TaskResult:
        """
        处理用户消息
        """
        # 确保学习记忆已加载
        await self.load_learnings()
        
        # 生成任务 ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. 理解意图
        task = await self._understand_intent(message, task_id)
        
        # 2. 判断任务类型
        if task.task_type == TaskType.CHAT:
            # 闲聊直接回复
            response = await self._chat_response(message)
            return TaskResult(success=True, output=response)
        
        # 3. 生成执行计划
        plan = await self._create_plan(task)
        
        # 4. 检查风险
        if plan.risk_level == RiskLevel.HIGH:
            return TaskResult(
                success=False,
                error="⚠️ 这个操作风险较高，已被禁止执行。如需执行，请联系管理员调整安全设置。",
                plan=plan
            )
        
        # 5. 执行计划
        result = await self._execute_plan(plan)
        
        # 6. 学习总结
        await self._learn_from_result(task, result)
        
        return result
        
    async def _understand_intent(self, message: str, task_id: str) -> Task:
        """
        理解用户意图
        """
        prompt = f"""你是一个任务分析专家。请分析用户的消息，判断：
1. 用户的意图是什么？
2. 需要执行什么操作？

用户消息：{message}

{self.memory.get_context_prompt()}

请返回 JSON 格式：
{{
    "intent": "意图描述",
    "task_type": "chat/file_op/gui_op/code_exec/web_op/sys_op",
    "context": {{"相关上下文"}}
}}
"""
        try:
            response = await self.llm.generate(prompt)
            if isinstance(response, dict):
                task_type_str = response.get("task_type", "chat")
                try:
                    task_type = TaskType[task_type_str.upper()]
                except KeyError:
                    task_type = TaskType.UNKNOWN
                return Task(
                    id=task_id,
                    description=response.get("intent", message),
                    task_type=task_type,
                    raw_message=message,
                    context=response.get("context", {})
                )
        except Exception:
            pass
        
        # 默认当作需要执行的任务
        return Task(
            id=task_id,
            description=message,
            task_type=TaskType.UNKNOWN,
            raw_message=message
        )
        
    async def _chat_response(self, message: str) -> str:
        """闲聊回复"""
        learnings_context = self.memory.get_conversation_prompt()
        
        prompt = f"""你是星灵，Woclaw 启明星 AI 助手。

你的特点：
- 你是用户电脑上的智能助手，像太空中的启明星一样为他们指引方向
- 友好、温暖、有耐心
- 回答简洁有力，不啰嗦
- 必要时可以主动提供帮助建议

{learnings_context}

用户说：{message}

请用星灵的身份回复。
"""
        
        try:
            response = await self.llm.generate(prompt)
            if isinstance(response, dict):
                return response.get("content", response.get("text", str(response)))
            return str(response)
        except Exception as e:
            return f"✨ 星星暂时有点困惑，没能理解你的意思... {str(e)}"
            
    async def _create_plan(self, task: Task) -> ExecutionPlan:
        """
        创建执行计划
        """
        # 获取可用工具
        tools = list(self.workers.keys()) or ["shell"]
        
        prompt = f"""你是星灵的规划专家。请为以下任务制定执行计划。

任务：{task.description}
任务类型：{task.task_type.value}

可用工具：
{', '.join(tools)}

{self.memory.get_context_prompt()}

请制定详细步骤，并评估风险等级。

风险等级说明：
- low：读取信息、搜索、聊天 - 直接执行
- medium：写入文件、执行命令、打开应用 - 需确认
- high：删除系统文件、格式化等 - 禁止

返回 JSON 格式：
{{
    "steps": [
        {{"step": 1, "tool": "工具名", "action": "具体操作", "params": {{"参数"}}}}
    ],
    "risk_level": "low/medium/high",
    "estimated_time": 预估秒数,
    "reasoning": "为什么这样做"
}}
"""
        try:
            response = await self.llm.generate(prompt)
            if isinstance(response, dict):
                content = response.get("content", str(response))
            else:
                content = str(response)
            
            # 解析 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                risk_str = data.get("risk_level", "low")
                try:
                    risk = RiskLevel(risk_str)
                except ValueError:
                    risk = RiskLevel.LOW
                    
                return ExecutionPlan(
                    task_id=task.id,
                    steps=data.get("steps", []),
                    risk_level=risk,
                    estimated_time=data.get("estimated_time", 60),
                    worker=self._select_worker(task.task_type),
                    reasoning=data.get("reasoning", "")
                )
        except Exception:
            pass
        
        # 默认计划：使用 shell 执行
        return ExecutionPlan(
            task_id=task.id,
            steps=[{"step": 1, "tool": "shell", "action": "execute", "params": {"command": task.description}}],
            risk_level=RiskLevel.MEDIUM,
            estimated_time=60,
            worker="shell",
            reasoning="默认执行方式"
        )
        
    def _select_worker(self, task_type: TaskType) -> str:
        """选择合适的 Worker"""
        mapping = {
            TaskType.FILE_OP: "file_worker",
            TaskType.GUI_OP: "gui_worker",
            TaskType.CODE_EXEC: "code_worker",
            TaskType.WEB_OP: "web_worker",
            TaskType.SYS_OP: "sys_worker",
        }
        return mapping.get(task_type, "shell")
        
    async def _execute_plan(self, plan: ExecutionPlan) -> TaskResult:
        """
        执行计划
        """
        results = []
        steps_history = []
        
        for step in plan.steps:
            tool_name = step.get("tool", "shell")
            action = step.get("action", "execute")
            params = step.get("params", {})
            
            worker = self.workers.get(tool_name)
            if not worker:
                # 回退到 shell
                worker = self.workers.get("shell")
                if not worker:
                    results.append({"step": step.get("step"), "error": f"工具 {tool_name} 未找到"})
                    continue
            
            try:
                result = await worker.execute(action, **params)
                results.append({"step": step.get("step"), "result": result})
                steps_history.append({
                    "tool": tool_name,
                    "action": action,
                    "params": params,
                    "result": result
                })
            except Exception as e:
                results.append({"step": step.get("step"), "error": str(e)})
                # 错误记录到学习系统
                await self.memory.record_error(
                    operation=f"{tool_name}.{action}",
                    error=str(e),
                    context=params
                )
                
        # 验证结果
        success = all("result" in r or "error" not in r for r in results)
        
        return TaskResult(
            success=success,
            output=results,
            plan=plan,
            steps=steps_history
        )
        
    async def _learn_from_result(self, task: Task, result: TaskResult):
        """
        从结果中学习
        """
        if result.success:
            await self.memory.record_success(
                task=task.description,
                steps=result.steps
            )
        else:
            await self.memory.record_failure(
                task=task.description,
                error=result.error,
                steps=result.steps
            )
            
        # 保存学习
        await self.memory.save()
