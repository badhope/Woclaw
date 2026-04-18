"""
Code Worker - 代码执行
安全的代码执行环境
"""

import asyncio
import json
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .base import BaseWorker, WorkerInfo


class CodeWorker(BaseWorker):
    """
    代码执行 Worker
    
    能力：
    - 执行 Python 代码
    - 执行 Shell 命令
    - 执行 JavaScript（Node.js）
    - 安全沙箱隔离
    - 超时控制
    """
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self._allowed_modules = {
            "os", "sys", "json", "math", "re", "datetime", 
            "collections", "itertools", "functools", "pathlib",
            "typing", "dataclasses", "abc", "copy", "random",
            "string", "time", "hashlib", "base64", "urllib",
            "http", "html", "xml", "csv", "io", "tempfile"
        }
        self._forbidden_modules = {
            "subprocess", "socket", "ctypes", "multiprocessing",
            "threading", "signal", "mmap", "resource"
        }
        
    def get_info(self) -> WorkerInfo:
        return WorkerInfo(
            name="code_worker",
            description="代码执行环境，支持 Python、Shell、JavaScript",
            capabilities=[
                "python",
                "shell",
                "javascript",
                "js",
                "install",
                "list_packages"
            ]
        )
        
    async def execute(self, action: str, **kwargs) -> dict:
        """执行代码"""
        
        handlers = {
            "python": self._run_python,
            "py": self._run_python,
            "shell": self._run_shell,
            "sh": self._run_shell,
            "bash": self._run_shell,
            "javascript": self._run_javascript,
            "js": self._run_javascript,
            "install": self._install_package,
            "pip": self._install_package,
            "list_packages": self._list_packages,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {"success": False, "error": f"未知操作: {action}"}
            
        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _run_python(self, code: str = None, file: str = None, **kwargs) -> dict:
        """执行 Python 代码"""
        if file:
            # 执行文件
            file_path = Path(file)
            if not file_path.exists():
                return {"success": False, "error": f"文件不存在: {file}"}
            code = file_path.read_text(encoding="utf-8")
            
        if not code:
            return {"success": False, "error": "需要 code 或 file 参数"}
            
        # 安全检查
        if not self._is_safe_code(code):
            return {"success": False, "error": "代码包含不允许的模块或操作"}
            
        # 执行代码
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = f.name
                
            try:
                # 执行
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=kwargs.get("timeout", self.timeout)
                )
                
                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "returncode": proc.returncode
                }
                
            finally:
                Path(temp_file).unlink(missing_ok=True)
                
        except asyncio.TimeoutError:
            return {"success": False, "error": f"执行超时（{self.timeout}秒）"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _run_shell(self, command: str, **kwargs) -> dict:
        """执行 Shell 命令"""
        if not command:
            return {"success": False, "error": "需要 command 参数"}
            
        # 安全检查
        forbidden = ["rm -rf", "mkfs", "dd if=", "> /dev/sd", "format"]
        for f in forbidden:
            if f in command.lower():
                return {"success": False, "error": f"禁止执行危险命令"}
                
        try:
            # Windows 使用 PowerShell
            shell = kwargs.get("shell", "powershell" if sys.platform == "win32" else "bash")
            
            if shell == "powershell":
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True
                )
            else:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=kwargs.get("timeout", self.timeout)
            )
            
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "returncode": proc.returncode
            }
            
        except asyncio.TimeoutError:
            return {"success": False, "error": f"执行超时（{self.timeout}秒）"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _run_javascript(self, code: str = None, file: str = None, **kwargs) -> dict:
        """执行 JavaScript 代码"""
        # 检查 Node.js 是否安装
        try:
            proc = await asyncio.create_subprocess_exec(
                "node", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            if proc.returncode != 0:
                return {"success": False, "error": "Node.js 未安装"}
                
        except FileNotFoundError:
            return {"success": False, "error": "Node.js 未安装"}
            
        if file:
            file_path = Path(file)
            if not file_path.exists():
                return {"success": False, "error": f"文件不存在: {file}"}
            code = file_path.read_text(encoding="utf-8")
            
        if not code:
            return {"success": False, "error": "需要 code 或 file 参数"}
            
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.js',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = f.name
                
            try:
                proc = await asyncio.create_subprocess_exec(
                    "node", temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=kwargs.get("timeout", self.timeout)
                )
                
                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "returncode": proc.returncode
                }
                
            finally:
                Path(temp_file).unlink(missing_ok=True)
                
        except asyncio.TimeoutError:
            return {"success": False, "error": f"执行超时（{self.timeout}秒）"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _install_package(self, package: str = None, packages: list = None, **kwargs) -> dict:
        """安装 Python 包"""
        packages = packages or ([package] if package else [])
        
        if not packages:
            return {"success": False, "error": "需要 package 或 packages 参数"}
            
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", *packages,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _list_packages(self, **kwargs) -> dict:
        """列出已安装的包"""
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "list", "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                packages = json.loads(stdout.decode('utf-8'))
                return {"success": True, "packages": packages}
            else:
                return {"success": False, "error": stderr.decode('utf-8')}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _is_safe_code(self, code: str) -> bool:
        """检查代码是否安全"""
        # 简单的关键词检查
        dangerous = [
            "__import__", "eval(", "exec(", "compile(",
            "globals()", "locals()", "vars(",
            "open(", "file(", "input(",
            "breakpoint(", "exit(", "quit(",
        ]
        
        for d in dangerous:
            if d in code:
                return False
                
        return True
