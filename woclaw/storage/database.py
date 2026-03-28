"""
数据库存储
"""

from typing import Any, Optional
from datetime import datetime

from woclaw.config import DatabaseConfig


class Database:
    """
    PostgreSQL 数据库封装
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool = None
    
    async def connect(self):
        """
        建立数据库连接
        """
        try:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=2,
                max_size=10
            )
            await self._init_tables()
        except ImportError:
            raise ImportError("Please install asyncpg: pip install asyncpg")
    
    async def _init_tables(self):
        """
        初始化数据表
        """
        async with self._pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    task TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    steps JSONB,
                    result JSONB,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id SERIAL PRIMARY KEY,
                    task_hash TEXT UNIQUE NOT NULL,
                    task TEXT NOT NULL,
                    steps JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
    
    async def save_task(self, task: str, steps: list[dict[str, Any]], result: Any = None, error: str = None) -> int:
        """
        保存任务记录
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO tasks (task, steps, result, error, status, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                task,
                steps,
                result,
                error,
                "completed" if not error else "failed",
                datetime.now()
            )
            return row["id"]
    
    async def get_task(self, task_id: int) -> Optional[dict[str, Any]]:
        """
        获取任务记录
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tasks WHERE id = $1",
                task_id
            )
            return dict(row) if row else None
    
    async def search_tasks(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        搜索任务历史
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM tasks 
                WHERE task ILIKE $1 
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                f"%{query}%",
                limit
            )
            return [dict(row) for row in rows]
    
    async def close(self):
        """
        关闭数据库连接
        """
        if self._pool:
            await self._pool.close()
