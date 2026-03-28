"""
系统监控工具
"""

import platform
import shutil
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class SystemTool(BaseTool):
    """
    系统监控工具
    """
    
    name: ClassVar[str] = "system"
    description: ClassVar[str] = "系统监控：CPU、内存、磁盘、网络监控"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行系统监控操作
        
        Args:
            action: 操作类型
                - info: 系统信息
                - cpu: CPU 信息
                - memory: 内存信息
                - disk: 磁盘信息
                - network: 网络信息
                - battery: 电池信息
                - users: 用户信息
                - uptime: 运行时间
        """
        handlers = {
            "info": self._info,
            "cpu": self._cpu,
            "memory": self._memory,
            "disk": self._disk,
            "network": self._network,
            "battery": self._battery,
            "users": self._users,
            "uptime": self._uptime,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _info(self) -> dict[str, Any]:
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
    
    async def _cpu(self) -> dict[str, Any]:
        try:
            import psutil
            return {
                "count_logical": psutil.cpu_count(logical=True),
                "count_physical": psutil.cpu_count(logical=False),
                "percent": psutil.cpu_percent(interval=1),
                "percent_per_cpu": psutil.cpu_percent(interval=1, percpu=True),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "stats": psutil.cpu_stats()._asdict(),
            }
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _memory(self) -> dict[str, Any]:
        try:
            import psutil
            virtual = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                "virtual": {
                    "total": virtual.total,
                    "available": virtual.available,
                    "used": virtual.used,
                    "free": virtual.free,
                    "percent": virtual.percent,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                },
            }
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _disk(self, path: str = "/") -> dict[str, Any]:
        try:
            import psutil
            usage = psutil.disk_usage(path)
            partitions = []
            for p in psutil.disk_partitions():
                try:
                    usage_p = psutil.disk_usage(p.mountpoint)
                    partitions.append({
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype,
                        "total": usage_p.total,
                        "used": usage_p.used,
                        "free": usage_p.free,
                        "percent": usage_p.percent,
                    })
                except PermissionError:
                    continue
            
            io = psutil.disk_io_counters()
            return {
                "usage": {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                },
                "partitions": partitions,
                "io": io._asdict() if io else None,
            }
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _network(self) -> dict[str, Any]:
        try:
            import psutil
            io = psutil.net_io_counters()
            connections = []
            for conn in psutil.net_connections(kind="inet"):
                try:
                    connections.append({
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid,
                    })
                except Exception:
                    continue
            
            interfaces = {}
            for name, addrs in psutil.net_if_addrs().items():
                interfaces[name] = [
                    {"family": str(addr.family), "address": addr.address}
                    for addr in addrs
                ]
            
            return {
                "io": io._asdict() if io else None,
                "connections": connections[:20],
                "interfaces": interfaces,
            }
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _battery(self) -> dict[str, Any]:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secs_left": battery.secs_left,
                }
            return {"error": "No battery detected"}
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _users(self) -> list[dict[str, Any]]:
        try:
            import psutil
            return [
                {
                    "name": u.name,
                    "terminal": u.terminal,
                    "host": u.host,
                    "started": u.started,
                }
                for u in psutil.users()
            ]
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
    
    async def _uptime(self) -> dict[str, Any]:
        try:
            import psutil
            import datetime
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            now = datetime.datetime.now()
            uptime = now - boot_time
            return {
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime.total_seconds(),
                "uptime_human": str(uptime).split(".")[0],
            }
        except ImportError:
            raise ImportError("Please install psutil: pip install psutil")
