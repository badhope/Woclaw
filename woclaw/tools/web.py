"""
网络请求工具
"""

import aiohttp
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class WebTool(BaseTool):
    """
    HTTP 请求工具
    """
    
    name: ClassVar[str] = "web"
    description: ClassVar[str] = "HTTP 请求：API 调用、网页抓取"
    
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Any:
        """
        执行网络请求
        
        Args:
            action: 操作类型
                - get: GET 请求
                - post: POST 请求
                - put: PUT 请求
                - delete: DELETE 请求
                - download: 下载文件
        """
        handlers = {
            "get": self._request,
            "post": self._request,
            "put": self._request,
            "delete": self._request,
            "download": self._download,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(method=action.upper() if action in ["get", "post", "put", "delete"] else None, **kwargs)
    
    async def _request(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        data: Any = None,
        json: Any = None,
        timeout: int = 30,
        **kwargs
    ) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    content_type = response.headers.get("Content-Type", "")
                    
                    if "application/json" in content_type:
                        body = await response.json()
                    else:
                        body = await response.text()
                    
                    return {
                        "success": response.status < 400,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "body": body,
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _download(
        self,
        url: str,
        path: str,
        headers: dict[str, str] | None = None,
        timeout: int = 300,
        **kwargs
    ) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status >= 400:
                        return {
                            "success": False,
                            "status": response.status,
                            "error": f"HTTP {response.status}",
                        }
                    
                    with open(path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    return {
                        "success": True,
                        "path": path,
                        "size": len(open(path, "rb").read()),
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
