"""
BaseWorker - Worker 基类
所有 Worker 的父类，定义统一接口
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar
from dataclasses import dataclass


@dataclass
class WorkerInfo:
    """Worker 信息"""
    name: str
    description: str
    capabilities: list[str]
    version: str = "1.0.0"


class BaseWorker(ABC):
    """
    Worker 基类
    所有专业 Worker 都继承此类
    """

    name: ClassVar[str] = "base"
    description: ClassVar[str] = "基础 Worker"
    capabilities: ClassVar[list[str]] = []

    def __init__(self):
        self.info = WorkerInfo(
            name=self.name,
            description=self.description,
            capabilities=self.capabilities,
        )

    @abstractmethod
    async def execute(self, action: str, **kwargs) -> dict:
        """
        执行操作

        Args:
            action: 操作名称
            **kwargs: 操作参数

        Returns:
            执行结果字典
        """
        pass

    def get_info(self) -> WorkerInfo:
        """获取 Worker 信息"""
        return self.info

    async def validate_params(self, action: str, params: dict) -> tuple[bool, str]:
        """
        验证参数

        Returns:
            (是否有效, 错误信息)
        """
        return True, ""

    async def cleanup(self):
        """清理资源（可选实现）"""
        pass
