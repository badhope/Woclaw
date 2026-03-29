"""
SysWorker - 系统操作 Worker
负责系统监控、进程管理等
"""

import platform
import psutil
from typing import Any, ClassVar
from datetime import datetime

from .base import BaseWorker


class SysWorker(BaseWorker):
    """
    系统操作 Worker
    提供系统信息、进程管理、磁盘监控等
    """

    name = "sys_worker"
    description = "系统信息和进程管理"
    capabilities = [
        "sys_info",
        "cpu_info",
        "memory_info",
        "disk_info",
        "network_info",
        "process_list",
        "process_kill",
        "process_start",
        "battery_info",
        "uptime",
    ]

    def __init__(self):
        super().__init__()

    async def execute(self, action: str, **kwargs) -> dict:
        """执行系统操作"""
        handlers = {
            "info": self._sys_info,
            "cpu": self._cpu_info,
            "memory": self._memory_info,
            "disk": self._disk_info,
            "network": self._network_info,
            "processes": self._process_list,
            "kill": self._process_kill,
            "start": self._process_start,
            "battery": self._battery_info,
            "uptime": self._uptime,
            "top": self._top_processes,
        }

        handler = handlers.get(action, self._sys_info)
        return await handler(**kwargs)

    async def _sys_info(self, **kwargs) -> dict:
        """获取系统信息"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            now = datetime.now()

            return {
                "success": True,
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "boot_time": boot_time.isoformat(),
                "uptime": str(now - boot_time).split(".")[0],
                "hostname": platform.node(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _cpu_info(self, interval: float = 1.0, **kwargs) -> dict:
        """获取 CPU 信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
            cpu_freq = psutil.cpu_freq()

            return {
                "success": True,
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "usage_percent": sum(cpu_percent) / len(cpu_percent),
                "usage_per_core": cpu_percent,
                "freq_current": cpu_freq.current if cpu_freq else None,
                "freq_max": cpu_freq.max if cpu_freq else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _memory_info(self, **kwargs) -> dict:
        """获取内存信息"""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()

            def format_bytes(b):
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if b < 1024:
                        return f"{b:.1f} {unit}"
                    b /= 1024
                return f"{b:.1f} PB"

            return {
                "success": True,
                "virtual": {
                    "total": format_bytes(vm.total),
                    "available": format_bytes(vm.available),
                    "used": format_bytes(vm.used),
                    "percent": vm.percent,
                },
                "swap": {
                    "total": format_bytes(swap.total),
                    "used": format_bytes(swap.used),
                    "percent": swap.percent,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _disk_info(self, path: str = None, **kwargs) -> dict:
        """获取磁盘信息"""
        try:
            if path is None:
                if platform.system() == "Windows":
                    path = "C:\\"
                else:
                    path = "/"

            usage = psutil.disk_usage(path)

            def format_bytes(b):
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if b < 1024:
                        return f"{b:.1f} {unit}"
                    b /= 1024
                return f"{b:.1f} PB"

            # 获取所有分区
            partitions = []
            for p in psutil.disk_partitions():
                try:
                    usage_p = psutil.disk_usage(p.mountpoint)
                    partitions.append({
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "total": format_bytes(usage_p.total),
                        "used": format_bytes(usage_p.used),
                        "free": format_bytes(usage_p.free),
                        "percent": usage_p.percent,
                    })
                except (PermissionError, OSError):
                    continue

            return {
                "success": True,
                "path": path,
                "total": format_bytes(usage.total),
                "used": format_bytes(usage.used),
                "free": format_bytes(usage.free),
                "percent": usage.percent,
                "partitions": partitions,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _network_info(self, **kwargs) -> dict:
        """获取网络信息"""
        try:
            io_counters = psutil.net_io_counters()
            connections = psutil.net_connections(kind="inet")

            def format_bytes(b):
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if b < 1024:
                        return f"{b:.1f} {unit}"
                    b /= 1024
                return f"{b:.1f} PB"

            # 获取网络接口
            interfaces = {}
            for name, addrs in psutil.net_if_addrs().items():
                interfaces[name] = []
                for addr in addrs:
                    interfaces[name].append({
                        "family": str(addr.family),
                        "address": addr.address,
                    })

            return {
                "success": True,
                "bytes_sent": format_bytes(io_counters.bytes_sent),
                "bytes_recv": format_bytes(io_counters.bytes_recv),
                "packets_sent": io_counters.packets_sent,
                "packets_recv": io_counters.packets_recv,
                "connections_count": len(connections),
                "interfaces": interfaces,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_list(self, limit: int = 50, **kwargs) -> dict:
        """列出进程"""
        try:
            processes = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
                try:
                    processes.append({
                        "pid": p.info["pid"],
                        "name": p.info["name"],
                        "cpu_percent": p.info["cpu_percent"] or 0,
                        "memory_percent": p.info["memory_percent"] or 0,
                        "status": p.info["status"],
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 按 CPU 使用率排序
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)

            return {
                "success": True,
                "processes": processes[:limit],
                "total_count": len(processes),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_kill(self, pid: int, force: bool = False, **kwargs) -> dict:
        """终止进程"""
        try:
            proc = psutil.Process(pid)

            if force:
                proc.kill()
            else:
                proc.terminate()

            return {
                "success": True,
                "pid": pid,
                "name": proc.name(),
                "method": "kill" if force else "terminate",
            }

        except psutil.NoSuchProcess:
            return {"success": False, "error": f"进程 {pid} 不存在"}
        except psutil.AccessDenied:
            return {"success": False, "error": f"权限不足，无法终止进程 {pid}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_start(self, command: str, cwd: str = None, **kwargs) -> dict:
        """启动进程"""
        try:
            import asyncio

            if cwd:
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=cwd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            else:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )

            return {
                "success": True,
                "pid": process.pid,
                "command": command,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _battery_info(self, **kwargs) -> dict:
        """获取电池信息"""
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return {"success": False, "error": "未检测到电池"}

            def format_time(seconds):
                if seconds == psutil.POWER_TIME_UNLIMITED:
                    return "无限制"
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                return f"{hours}h {minutes}m"

            return {
                "success": True,
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "charging": battery.power_plugged,
                "time_left": format_time(battery.secs_left),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _uptime(self, **kwargs) -> dict:
        """获取运行时间"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            now = datetime.now()
            uptime = now - boot_time

            return {
                "success": True,
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime.total_seconds(),
                "uptime_human": str(uptime).split(".")[0],
                "days": uptime.days,
                "hours": uptime.seconds // 3600,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _top_processes(self, sort_by: str = "cpu", limit: int = 10, **kwargs) -> dict:
        """获取资源占用最高的进程"""
        try:
            processes = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append({
                        "pid": p.info["pid"],
                        "name": p.info["name"],
                        "cpu_percent": p.info["cpu_percent"] or 0,
                        "memory_percent": p.info["memory_percent"] or 0,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if sort_by == "cpu":
                processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            else:
                processes.sort(key=lambda x: x["memory_percent"], reverse=True)

            return {
                "success": True,
                "sort_by": sort_by,
                "processes": processes[:limit],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
