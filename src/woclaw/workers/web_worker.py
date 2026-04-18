"""
WebWorker - 网络操作 Worker
负责 HTTP 请求、网页抓取等
"""

import asyncio
import aiohttp
from typing import Any, ClassVar
from urllib.parse import urlparse, urljoin

from .base import BaseWorker


class WebWorker(BaseWorker):
    """
    网络操作 Worker
    提供 HTTP 请求和网页抓取功能
    """

    name = "web_worker"
    description = "网络请求和网页抓取"
    capabilities = [
        "http_get",
        "http_post",
        "http_download",
        "scrape_page",
        "check_url",
        "dns_lookup",
    ]

    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: aiohttp.ClientSession = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session

    async def execute(self, action: str, **kwargs) -> dict:
        """执行网络操作"""
        handlers = {
            "get": self._http_get,
            "post": self._http_post,
            "download": self._http_download,
            "scrape": self._scrape_page,
            "check": self._check_url,
            "dns": self._dns_lookup,
        }

        handler = handlers.get(action, self._http_get)
        return await handler(**kwargs)

    async def _http_get(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        **kwargs
    ) -> dict:
        """GET 请求"""
        try:
            session = await self._get_session()

            async with session.get(url, headers=headers, params=params) as response:
                content = await response.text()

                return {
                    "success": True,
                    "status": response.status,
                    "url": str(response.url),
                    "headers": dict(response.headers),
                    "content": content[:10000],  # 限制大小
                    "content_length": len(content),
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _http_post(
        self,
        url: str,
        data: dict = None,
        json: dict = None,
        headers: dict = None,
        **kwargs
    ) -> dict:
        """POST 请求"""
        try:
            session = await self._get_session()

            async with session.post(url, data=data, json=json, headers=headers) as response:
                content = await response.text()

                return {
                    "success": True,
                    "status": response.status,
                    "url": str(response.url),
                    "content": content[:10000],
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _http_download(
        self,
        url: str,
        save_path: str,
        chunk_size: int = 65536,
        **kwargs
    ) -> dict:
        """下载文件"""
        try:
            import os
            session = await self._get_session()

            # 创建目录
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

            async with session.get(url) as response:
                if response.status != 200:
                    return {"success": False, "error": f"HTTP {response.status}"}

                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(save_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)

            return {
                "success": True,
                "path": save_path,
                "size": downloaded,
                "url": url,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _scrape_page(
        self,
        url: str,
        selector: str = None,
        extract: str = "text",
        **kwargs
    ) -> dict:
        """抓取网页"""
        try:
            session = await self._get_session()

            async with session.get(url) as response:
                content = await response.text()

            # 如果安装了 BeautifulSoup
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(content, "html.parser")

                if selector:
                    elements = soup.select(selector)
                    results = []
                    for elem in elements:
                        if extract == "text":
                            results.append(elem.get_text(strip=True))
                        elif extract == "html":
                            results.append(str(elem))
                        elif extract == "link":
                            href = elem.get("href")
                            if href:
                                results.append(urljoin(url, href))

                    return {
                        "success": True,
                        "url": url,
                        "results": results,
                        "count": len(results),
                    }
                else:
                    # 返回标题和文本摘要
                    return {
                        "success": True,
                        "url": url,
                        "title": soup.title.string if soup.title else "",
                        "text": soup.get_text(strip=True)[:5000],
                        "links": [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)][:50],
                    }

            except ImportError:
                return {
                    "success": True,
                    "url": url,
                    "content": content[:10000],
                    "note": "建议安装 beautifulsoup4: pip install beautifulsoup4",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _check_url(self, url: str, **kwargs) -> dict:
        """检查 URL 是否可访问"""
        try:
            session = await self._get_session()

            async with session.head(url) as response:
                return {
                    "success": response.status < 400,
                    "status": response.status,
                    "url": url,
                    "content_type": response.headers.get("Content-Type", ""),
                }

        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    async def _dns_lookup(self, domain: str, **kwargs) -> dict:
        """DNS 查询"""
        try:
            import socket

            ip = socket.gethostbyname(domain)

            return {
                "success": True,
                "domain": domain,
                "ip": ip,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "domain": domain}

    async def cleanup(self):
        """关闭 session"""
        if self.session and not self.session.closed:
            await self.session.close()
