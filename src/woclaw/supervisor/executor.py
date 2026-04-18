"""
Executor - 执行调度器
负责执行任务步骤，处理重试和错误
"""

import asyncio
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionStep:
    """执行步骤"""
    id: int
    description: str
    tool: str
    action: str
    params: dict
    depends_on: list[int] = field(default_factory=list)
    estimated_time: int = 30
    risk: str = "low"
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = None
    retry_count: int = 0


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    steps: list[ExecutionStep]
    output: Any = None
    error: str = None
    total_time: float = 0


class Executor:
    """
    执行调度器
    负责任务的并行/串行执行，错误重试
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.tools: dict[str, Any] = {}

    def register_tool(self, name: str, tool: Any):
        """注册工具"""
        self.tools[name] = tool

    async def execute_steps(
        self,
        steps: list[dict],
        workers: dict[str, Any],
        progress_callback: Callable = None
    ) -> ExecutionResult:
        """
        执行步骤列表

        Args:
            steps: 步骤列表
            workers: Worker 实例字典
            progress_callback: 进度回调函数

        Returns:
            执行结果
        """
        import time
        start_time = time.time()

        # 转换为 ExecutionStep
        exec_steps = []
        for i, step in enumerate(steps):
            exec_steps.append(ExecutionStep(
                id=step.get("id", i + 1),
                description=step.get("description", ""),
                tool=step.get("tool", "shell"),
                action=step.get("action", "execute"),
                params=step.get("params", {}),
                depends_on=step.get("depends_on", []),
                estimated_time=step.get("estimated_time", 30),
                risk=step.get("risk", "low")
            ))

        # 按依赖关系排序执行
        completed = set()
        pending = set(range(1, len(exec_steps) + 1))

        while pending:
            # 找到可以执行的步骤（依赖都已完成）
            ready = []
            for step in exec_steps:
                if step.id in pending:
                    deps = set(step.depends_on) if step.depends_on else set()
                    if deps <= completed:
                        ready.append(step)

            if not ready:
                # 没有可执行的步骤，可能是依赖环
                break

            # 并行执行准备好的步骤
            tasks = []
            for step in ready:
                task = self._execute_step(step, workers, progress_callback)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 更新完成状态
            for step, result in zip(ready, results):
                pending.discard(step.id)
                if isinstance(result, Exception):
                    step.status = StepStatus.FAILED
                    step.error = str(result)
                elif result.get("success"):
                    step.status = StepStatus.SUCCESS
                    step.result = result
                else:
                    step.status = StepStatus.FAILED
                    step.error = result.get("error", "未知错误")

                if step.status == StepStatus.SUCCESS:
                    completed.add(step.id)

                # 回调
                if progress_callback:
                    await progress_callback(step)

            # 检查是否全部失败
            if all(s.status == StepStatus.FAILED for s in exec_steps if s.id in pending):
                break

        total_time = time.time() - start_time
        success = all(s.status == StepStatus.SUCCESS for s in exec_steps)

        return ExecutionResult(
            success=success,
            steps=exec_steps,
            total_time=total_time
        )

    async def _execute_step(
        self,
        step: ExecutionStep,
        workers: dict[str, Any],
        progress_callback: Callable = None
    ) -> dict:
        """执行单个步骤"""
        step.status = StepStatus.RUNNING

        worker = workers.get(step.tool)
        if not worker:
            return {"success": False, "error": f"未找到工具: {step.tool}"}

        # 重试逻辑
        for attempt in range(self.max_retries + 1):
            try:
                result = await worker.execute(step.action, **step.params)
                return result
            except Exception as e:
                step.retry_count = attempt + 1
                if attempt < self.max_retries:
                    # 等待后重试（指数退避）
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": "超过最大重试次数"}
