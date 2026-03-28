"""
记忆系统
"""

import json
from typing import Any, Optional
from datetime import datetime


class Memory:
    """
    任务历史与上下文记忆
    """
    
    def __init__(self, db_config):
        self.db_config = db_config
        self._cache: dict[str, Any] = {}
    
    async def save(self, task: str, steps: list[dict[str, Any]]) -> str:
        """
        保存任务执行记录
        """
        record = {
            "task": task,
            "steps": steps,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        self._cache[task] = record
        return task
    
    async def recall(self, task: str) -> Optional[dict[str, Any]]:
        """
        回忆历史任务
        """
        return self._cache.get(task)
    
    async def search_similar(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        搜索相似的历史任务
        """
        results = []
        for task, record in self._cache.items():
            if query.lower() in task.lower():
                results.append(record)
        return results[:limit]
