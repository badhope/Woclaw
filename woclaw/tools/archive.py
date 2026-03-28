"""
压缩解压工具
"""

import zipfile
import tarfile
import os
from pathlib import Path
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ArchiveTool(BaseTool):
    """
    压缩解压工具
    """
    
    name: ClassVar[str] = "archive"
    description: ClassVar[str] = "压缩解压：ZIP、TAR、GZ 格式"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行压缩解压操作
        
        Args:
            action: 操作类型
                - zip: 创建 ZIP 压缩包
                - unzip: 解压 ZIP
                - tar: 创建 TAR 压缩包
                - untar: 解压 TAR
                - list: 列出压缩包内容
        """
        handlers = {
            "zip": self._zip,
            "unzip": self._unzip,
            "tar": self._tar,
            "untar": self._untar,
            "list": self._list,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _zip(
        self,
        source: str,
        output: str,
        compression: int = zipfile.ZIP_DEFLATED
    ) -> dict[str, Any]:
        try:
            source_path = Path(source)
            files_count = 0
            
            with zipfile.ZipFile(output, "w", compression) as zf:
                if source_path.is_file():
                    zf.write(source_path, source_path.name)
                    files_count = 1
                else:
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path.parent)
                            zf.write(file_path, arcname)
                            files_count += 1
            
            return {
                "success": True,
                "output": output,
                "files_count": files_count,
                "size": os.path.getsize(output),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _unzip(
        self,
        archive: str,
        output_dir: str,
        password: str | None = None
    ) -> dict[str, Any]:
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            files_count = 0
            
            with zipfile.ZipFile(archive, "r") as zf:
                if password:
                    zf.setpassword(password.encode())
                zf.extractall(output_dir)
                files_count = len(zf.namelist())
            
            return {
                "success": True,
                "output_dir": output_dir,
                "files_count": files_count,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _tar(
        self,
        source: str,
        output: str,
        mode: str = "w:gz"
    ) -> dict[str, Any]:
        try:
            source_path = Path(source)
            files_count = 0
            
            with tarfile.open(output, mode) as tf:
                if source_path.is_file():
                    tf.add(source_path, source_path.name)
                    files_count = 1
                else:
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path.parent)
                            tf.add(file_path, arcname)
                            files_count += 1
            
            return {
                "success": True,
                "output": output,
                "files_count": files_count,
                "size": os.path.getsize(output),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _untar(
        self,
        archive: str,
        output_dir: str,
        mode: str = "r:*"
    ) -> dict[str, Any]:
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            files_count = 0
            
            with tarfile.open(archive, mode) as tf:
                tf.extractall(output_dir)
                files_count = len(tf.getnames())
            
            return {
                "success": True,
                "output_dir": output_dir,
                "files_count": files_count,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list(self, archive: str) -> dict[str, Any]:
        try:
            if archive.endswith(".zip"):
                with zipfile.ZipFile(archive, "r") as zf:
                    files = [
                        {
                            "name": info.filename,
                            "size": info.file_size,
                            "compressed_size": info.compress_size,
                        }
                        for info in zf.infolist()
                    ]
            else:
                with tarfile.open(archive, "r:*") as tf:
                    files = [
                        {
                            "name": member.name,
                            "size": member.size,
                        }
                        for member in tf.getmembers()
                    ]
            
            return {
                "success": True,
                "archive": archive,
                "files": files,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
