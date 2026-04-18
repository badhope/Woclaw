"""
FileWorker - 文件操作 Worker
负责文件和文件夹的管理操作
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Any, ClassVar
from datetime import datetime

from .base import BaseWorker


class FileWorker(BaseWorker):
    """
    文件操作 Worker
    提供安全的文件和文件夹操作
    """

    name = "file_worker"
    description = "文件和文件夹管理"
    capabilities = [
        "read_file",
        "write_file",
        "copy_file",
        "move_file",
        "delete_file",
        "list_dir",
        "search_files",
        "create_dir",
        "delete_dir",
        "file_info",
        "batch_rename",
    ]

    def __init__(self, workspace: str = None):
        super().__init__()
        self.workspace = workspace or os.getcwd()

    async def execute(self, action: str, **kwargs) -> dict:
        """执行文件操作"""
        handlers = {
            "read": self._read_file,
            "write": self._write_file,
            "copy": self._copy_file,
            "move": self._move_file,
            "delete": self._delete_file,
            "list": self._list_dir,
            "search": self._search_files,
            "mkdir": self._create_dir,
            "rmdir": self._delete_dir,
            "info": self._file_info,
            "rename": self._rename_file,
            "batch_rename": self._batch_rename,
            "organize": self._organize_files,
        }

        handler = handlers.get(action)
        if not handler:
            return {"success": False, "error": f"未知操作: {action}"}

        return await handler(**kwargs)

    def _resolve_path(self, path: str) -> Path:
        """解析路径（安全检查）"""
        p = Path(path).resolve()

        # 禁止访问系统目录
        dangerous = ["C:\\Windows", "C:\\Program Files", "/etc", "/usr/bin", "/usr/sbin"]
        for d in dangerous:
            if str(p).startswith(d):
                raise ValueError(f"禁止访问系统目录: {d}")

        return p

    async def _read_file(self, path: str, encoding: str = "utf-8", **kwargs) -> dict:
        """读取文件"""
        try:
            p = self._resolve_path(path)

            if not p.exists():
                return {"success": False, "error": f"文件不存在: {path}"}

            if not p.is_file():
                return {"success": False, "error": f"不是文件: {path}"}

            # 根据扩展名自动选择编码
            if p.suffix.lower() in [".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml", ".xml", ".html", ".css"]:
                encoding = "utf-8"
            else:
                encoding = "utf-8"

            content = p.read_text(encoding=encoding, errors="replace")

            return {
                "success": True,
                "path": str(p),
                "content": content,
                "size": p.stat().st_size,
                "lines": len(content.splitlines()),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
        **kwargs
    ) -> dict:
        """写入文件"""
        try:
            p = self._resolve_path(path)

            if create_dirs:
                p.parent.mkdir(parents=True, exist_ok=True)

            p.write_text(content, encoding=encoding)

            return {
                "success": True,
                "path": str(p),
                "size": p.stat().st_size,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _copy_file(self, src: str, dst: str, **kwargs) -> dict:
        """复制文件"""
        try:
            src_p = self._resolve_path(src)
            dst_p = self._resolve_path(dst)

            if not src_p.exists():
                return {"success": False, "error": f"源文件不存在: {src}"}

            # 如果目标是目录
            if dst_p.is_dir():
                dst_p = dst_p / src_p.name

            # 确保目标目录存在
            dst_p.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src_p, dst_p)

            return {"success": True, "src": str(src_p), "dst": str(dst_p)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _move_file(self, src: str, dst: str, **kwargs) -> dict:
        """移动文件"""
        try:
            src_p = self._resolve_path(src)
            dst_p = self._resolve_path(dst)

            if not src_p.exists():
                return {"success": False, "error": f"源文件不存在: {src}"}

            # 如果目标是目录
            if dst_p.is_dir():
                dst_p = dst_p / src_p.name

            # 确保目标目录存在
            dst_p.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(src_p), str(dst_p))

            return {"success": True, "src": str(src_p), "dst": str(dst_p)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _delete_file(self, path: str, **kwargs) -> dict:
        """删除文件"""
        try:
            p = self._resolve_path(path)

            if not p.exists():
                return {"success": False, "error": f"文件不存在: {path}"}

            if p.is_dir():
                return {"success": False, "error": f"是目录不是文件: {path}"}

            p.unlink()

            return {"success": True, "path": str(p), "message": "文件已删除"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _list_dir(
        self,
        path: str = None,
        show_hidden: bool = False,
        pattern: str = "*",
        **kwargs
    ) -> dict:
        """列出目录内容"""
        try:
            p = self._resolve_path(path or self.workspace)

            if not p.exists():
                return {"success": False, "error": f"目录不存在: {path}"}

            if not p.is_dir():
                return {"success": False, "error": f"不是目录: {path}"}

            items = []
            for item in p.glob(pattern):
                if not show_hidden and item.name.startswith("."):
                    continue

                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "is_file": item.is_file(),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "ext": item.suffix,
                })

            # 按目录优先、名称排序
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

            return {
                "success": True,
                "path": str(p),
                "items": items,
                "count": len(items),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _search_files(
        self,
        directory: str = None,
        pattern: str = "*",
        recursive: bool = True,
        file_type: str = None,
        **kwargs
    ) -> dict:
        """搜索文件"""
        try:
            dir_path = self._resolve_path(directory or self.workspace)

            results = []
            if recursive:
                glob_pattern = "**/" + pattern
            else:
                glob_pattern = pattern

            for p in dir_path.glob(glob_pattern):
                if p.is_file():
                    # 文件类型过滤
                    if file_type:
                        if file_type.startswith("."):
                            if p.suffix.lower() != file_type.lower():
                                continue
                        elif p.suffix.lower() not in [f".{file_type.lower()}"]:
                            continue

                    results.append({
                        "name": p.name,
                        "path": str(p),
                        "size": p.stat().st_size,
                        "ext": p.suffix,
                    })

            return {
                "success": True,
                "directory": str(dir_path),
                "pattern": pattern,
                "results": results,
                "count": len(results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_dir(self, path: str, parents: bool = True, **kwargs) -> dict:
        """创建目录"""
        try:
            p = self._resolve_path(path)
            p.mkdir(parents=parents, exist_ok=True)

            return {"success": True, "path": str(p)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _delete_dir(self, path: str, recursive: bool = False, **kwargs) -> dict:
        """删除目录"""
        try:
            p = self._resolve_path(path)

            if not p.exists():
                return {"success": False, "error": f"目录不存在: {path}"}

            if not p.is_dir():
                return {"success": False, "error": f"不是目录: {path}"}

            if recursive:
                shutil.rmtree(p)
            else:
                p.rmdir()

            return {"success": True, "path": str(p), "message": "目录已删除"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _file_info(self, path: str, **kwargs) -> dict:
        """获取文件信息"""
        try:
            p = self._resolve_path(path)

            if not p.exists():
                return {"success": False, "error": f"文件不存在: {path}"}

            stat = p.stat()

            info = {
                "success": True,
                "name": p.name,
                "path": str(p),
                "is_dir": p.is_dir(),
                "is_file": p.is_file(),
                "size": stat.st_size,
                "size_human": self._human_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "ext": p.suffix,
            }

            # 计算 MD5（仅小文件）
            if p.is_file() and stat.st_size < 10 * 1024 * 1024:  # < 10MB
                md5 = hashlib.md5()
                with open(p, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        md5.update(chunk)
                info["md5"] = md5.hexdigest()

            return info

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _rename_file(self, path: str, new_name: str, **kwargs) -> dict:
        """重命名文件"""
        try:
            p = self._resolve_path(path)
            new_p = p.parent / new_name

            p.rename(new_p)

            return {"success": True, "old": str(p), "new": str(new_p)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _batch_rename(
        self,
        directory: str,
        pattern: str,
        replace_with: str,
        recursive: bool = False,
        **kwargs
    ) -> dict:
        """批量重命名"""
        try:
            dir_path = self._resolve_path(directory)
            results = []

            if recursive:
                glob_pattern = "**/" + pattern
            else:
                glob_pattern = pattern

            for p in dir_path.glob(glob_pattern):
                if p.is_file():
                    new_name = p.name.replace(pattern.replace("*", ""), replace_with)
                    new_p = p.parent / new_name

                    if new_name != p.name:
                        p.rename(new_p)
                        results.append({"old": p.name, "new": new_name})

            return {
                "success": True,
                "renamed": results,
                "count": len(results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _organize_files(
        self,
        directory: str,
        organize_by: str = "type",
        **kwargs
    ) -> dict:
        """
        整理文件

        Args:
            directory: 要整理的目录
            organize_by: 整理方式
                - type: 按文件类型
                - date: 按修改日期
                - size: 按大小
        """
        try:
            import re

            dir_path = self._resolve_path(directory)

            # 文件类型映射
            type_map = {
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
                "documents": [".doc", ".docx", ".pdf", ".txt", ".md", ".rtf", ".odt"],
                "spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
                "presentations": [".ppt", ".pptx", ".odp"],
                "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
                "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                "code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs"],
            }

            # 反向映射：扩展名 -> 文件夹
            ext_to_folder = {}
            for folder, exts in type_map.items():
                for ext in exts:
                    ext_to_folder[ext.lower()] = folder

            # 分类文件
            folders_created = set()
            moved_files = []

            for item in dir_path.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()

                    if organize_by == "type":
                        target_folder = ext_to_folder.get(ext, "others")
                    elif organize_by == "date":
                        stat = item.stat()
                        date = datetime.fromtimestamp(stat.st_mtime)
                        target_folder = date.strftime("%Y-%m")
                    elif organize_by == "size":
                        stat = item.stat()
                        if stat.st_size < 1024 * 1024:  # < 1MB
                            target_folder = "small"
                        elif stat.st_size < 10 * 1024 * 1024:  # < 10MB
                            target_folder = "medium"
                        else:
                            target_folder = "large"
                    else:
                        target_folder = "others"

                    # 创建目标文件夹
                    target_path = dir_path / target_folder
                    if target_folder not in folders_created:
                        target_path.mkdir(exist_ok=True)
                        folders_created.add(target_folder)

                    # 移动文件
                    if item.parent != target_path:
                        new_path = target_path / item.name
                        counter = 1
                        while new_path.exists():
                            new_name = f"{item.stem}_{counter}{item.suffix}"
                            new_path = target_path / new_name
                            counter += 1

                        shutil.move(str(item), str(new_path))
                        moved_files.append({
                            "name": item.name,
                            "from": str(item),
                            "to": str(new_path),
                            "folder": target_folder,
                        })

            return {
                "success": True,
                "moved": moved_files,
                "folders_created": list(folders_created),
                "count": len(moved_files),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _human_size(self, size: int) -> str:
        """人类可读的文件大小"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
