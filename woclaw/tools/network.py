"""
网络工具
"""

import asyncio
import socket
import aiohttp
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

from woclaw.tools.base import BaseTool


class NetworkTool(BaseTool):
    """
    网络工具
    """
    
    name: ClassVar[str] = "network"
    description: ClassVar[str] = "网络工具：下载、DNS、端口扫描、Ping"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行网络操作
        
        Args:
            action: 操作类型
                - download: 下载文件
                - upload: 上传文件
                - dns_lookup: DNS 查询
                - port_scan: 端口扫描
                - ping: Ping 测试
                - whois: Whois 查询
                - check_url: 检查 URL 可访问性
        """
        handlers = {
            "download": self._download,
            "upload": self._upload,
            "dns_lookup": self._dns_lookup,
            "port_scan": self._port_scan,
            "ping": self._ping,
            "check_url": self._check_url,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _download(
        self,
        url: str,
        save_path: str,
        chunk_size: int = 8192,
        timeout: int = 300,
        headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status >= 400:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                        }
                    
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0
                    
                    with open(save_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                    
                    return {
                        "success": True,
                        "path": save_path,
                        "total_size": total_size,
                        "downloaded": downloaded,
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _upload(
        self,
        url: str,
        file_path: str,
        field_name: str = "file",
        timeout: int = 300,
        headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        try:
            with open(file_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field(field_name, f, filename=Path(file_path).name)
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        data=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        return {
                            "success": response.status < 400,
                            "status": response.status,
                            "response": await response.text(),
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _dns_lookup(self, hostname: str) -> dict[str, Any]:
        try:
            ipv4 = socket.getaddrinfo(hostname, None, socket.AF_INET)
            ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)
            
            return {
                "hostname": hostname,
                "ipv4": list(set(addr[4][0] for addr in ipv4)),
                "ipv6": list(set(addr[4][0] for addr in ipv6)),
            }
        except socket.gaierror as e:
            return {"error": str(e)}
    
    async def _port_scan(
        self,
        host: str,
        ports: list[int],
        timeout: float = 1.0
    ) -> dict[str, Any]:
        results = {}
        
        async def check_port(port: int) -> tuple[int, bool]:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=timeout
                )
                writer.close()
                await writer.wait_closed()
                return port, True
            except Exception:
                return port, False
        
        tasks = [check_port(port) for port in ports]
        port_results = await asyncio.gather(*tasks)
        
        for port, is_open in port_results:
            results[port] = is_open
        
        return {
            "host": host,
            "ports": results,
            "open_ports": [p for p, open_ in results.items() if open_],
        }
    
    async def _ping(self, host: str, count: int = 4) -> dict[str, Any]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "ping" if platform.system() != "Windows" else "ping",
                "-c" if platform.system() != "Windows" else "-n",
                str(count),
                host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return {
                "host": host,
                "success": proc.returncode == 0,
                "output": stdout.decode("utf-8", errors="replace"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_url(self, url: str, timeout: int = 10) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    allow_redirects=True
                ) as response:
                    end_time = asyncio.get_event_loop().time()
                    
                    return {
                        "url": url,
                        "accessible": True,
                        "status": response.status,
                        "response_time": round((end_time - start_time) * 1000, 2),
                        "headers": dict(response.headers),
                        "final_url": str(response.url),
                    }
        except Exception as e:
            return {
                "url": url,
                "accessible": False,
                "error": str(e),
            }


import platform
