"""
文件系统工具
"""

import os
import shutil
from pathlib import Path
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class FilesystemTool(BaseTool):
    """
    文件系统操作工具
    """
    
    name: ClassVar[str] = "filesystem"
    description: ClassVar[str] = "文件系统操作：读写、搜索、组织文件"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行文件系统操作
        
        Args:
            action: 操作类型
                - read: 读取文件
                - write: 写入文件
                - list: 列出目录
                - search: 搜索文件
                - delete: 删除文件/目录
                - copy: 复制文件
                - move: 移动文件
                - create_dir: 创建目录
        """
        handlers = {
            "read": self._read,
            "write": self._write,
            "list": self._list,
            "search": self._search,
            "delete": self._delete,
            "copy": self._copy,
            "move": self._move,
            "create_dir": self._create_dir,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _read(self, path: str, encoding: str = "utf-8") -> str:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    
    async def _write(self, path: str, content: str, encoding: str = "utf-8") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return path
    
    async def _list(self, path: str, pattern: str = "*") -> list[str]:
        return [str(p) for p in Path(path).glob(pattern)]
    
    async def _search(self, path: str, query: str, file_pattern: str = "*") -> list[dict[str, Any]]:
        results = []
        for file_path in Path(path).rglob(file_pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        results.append({
                            "path": str(file_path),
                            "matches": content.lower().count(query.lower())
                        })
                except Exception:
                    continue
        return results
    
    async def _delete(self, path: str) -> bool:
        p = Path(path)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return True
    
    async def _copy(self, src: str, dst: str) -> str:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return dst
    
    async def _move(self, src: str, dst: str) -> str:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
        return dst
    
    async def _create_dir(self, path: str) -> str:
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
