"""
进程管理工具
"""

import asyncio
import psutil
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ProcessTool(BaseTool):
    """
    进程管理工具
    """
    
    name: ClassVar[str] = "process"
    description: ClassVar[str] = "进程管理：启动、停止、监控进程"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行进程管理操作
        
        Args:
            action: 操作类型
                - list: 列出所有进程
                - find: 查找进程
                - kill: 终止进程
                - start: 启动进程
                - info: 获取进程信息
                - top: 获取资源占用最高的进程
        """
        handlers = {
            "list": self._list,
            "find": self._find,
            "kill": self._kill,
            "start": self._start,
            "info": self._info,
            "top": self._top,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _list(self) -> list[dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cpu_percent": proc.info["cpu_percent"],
                    "memory_percent": proc.info["memory_percent"],
                    "status": proc.info["status"],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    async def _find(self, name: str) -> list[dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                if name.lower() in proc.info["name"].lower():
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_percent": proc.info["memory_percent"],
                        "status": proc.info["status"],
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    async def _kill(self, pid: int, force: bool = False) -> dict[str, Any]:
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return {"success": True, "pid": pid, "name": proc.name()}
        except psutil.NoSuchProcess:
            return {"success": False, "error": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"success": False, "error": f"Access denied to kill process {pid}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        background: bool = True
    ) -> dict[str, Any]:
        try:
            if background:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                    cwd=cwd,
                    env=env
                )
                return {
                    "success": True,
                    "pid": proc.pid,
                    "command": command
                }
            else:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=env
                )
                stdout, stderr = await proc.communicate()
                return {
                    "success": proc.returncode == 0,
                    "pid": proc.pid,
                    "return_code": proc.returncode,
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _info(self, pid: int) -> dict[str, Any]:
        try:
            proc = psutil.Process(pid)
            return {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "memory_info": proc.memory_info()._asdict(),
                "create_time": proc.create_time(),
                "exe": proc.exe(),
                "cwd": proc.cwd(),
                "cmdline": proc.cmdline(),
                "num_threads": proc.num_threads(),
                "num_handles": proc.num_handles() if hasattr(proc, "num_handles") else None,
            }
        except psutil.NoSuchProcess:
            return {"error": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"error": f"Access denied to process {pid}"}
    
    async def _top(self, sort_by: str = "cpu", limit: int = 10) -> list[dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cpu_percent": proc.info["cpu_percent"] or 0,
                    "memory_percent": proc.info["memory_percent"] or 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if sort_by == "cpu":
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x["memory_percent"], reverse=True)
        
        return processes[:limit]
