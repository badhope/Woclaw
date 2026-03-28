"""
数据处理工具
"""

import json
import csv
from pathlib import Path
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class DataTool(BaseTool):
    """
    数据处理工具
    """
    
    name: ClassVar[str] = "data"
    description: ClassVar[str] = "数据处理：JSON/CSV/Excel 处理"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行数据处理操作
        
        Args:
            action: 操作类型
                - json_read: 读取 JSON 文件
                - json_write: 写入 JSON 文件
                - csv_read: 读取 CSV 文件
                - csv_write: 写入 CSV 文件
                - transform: 数据转换
                - filter: 数据过滤
        """
        handlers = {
            "json_read": self._json_read,
            "json_write": self._json_write,
            "csv_read": self._csv_read,
            "csv_write": self._csv_write,
            "transform": self._transform,
            "filter": self._filter,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _json_read(self, path: str, encoding: str = "utf-8") -> Any:
        with open(path, "r", encoding=encoding) as f:
            return json.load(f)
    
    async def _json_write(
        self,
        path: str,
        data: Any,
        encoding: str = "utf-8",
        indent: int = 2
    ) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return path
    
    async def _csv_read(
        self,
        path: str,
        encoding: str = "utf-8",
        delimiter: str = ",",
        has_header: bool = True
    ) -> list[dict[str, Any]]:
        result = []
        with open(path, "r", encoding=encoding, newline="") as f:
            if has_header:
                reader = csv.DictReader(f, delimiter=delimiter)
                result = list(reader)
            else:
                reader = csv.reader(f, delimiter=delimiter)
                result = [{"col_" + str(i): v for i, v in enumerate(row)} for row in reader]
        return result
    
    async def _csv_write(
        self,
        path: str,
        data: list[dict[str, Any]],
        encoding: str = "utf-8",
        delimiter: str = ","
    ) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if not data:
            with open(path, "w", encoding=encoding, newline="") as f:
                pass
            return path
        
        fieldnames = list(data[0].keys())
        with open(path, "w", encoding=encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        return path
    
    async def _transform(
        self,
        data: list[dict[str, Any]],
        mapping: dict[str, str]
    ) -> list[dict[str, Any]]:
        result = []
        for item in data:
            new_item = {}
            for old_key, new_key in mapping.items():
                if old_key in item:
                    new_item[new_key] = item[old_key]
            result.append(new_item)
        return result
    
    async def _filter(
        self,
        data: list[dict[str, Any]],
        conditions: dict[str, Any]
    ) -> list[dict[str, Any]]:
        result = []
        for item in data:
            match = True
            for key, value in conditions.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                result.append(item)
        return result
