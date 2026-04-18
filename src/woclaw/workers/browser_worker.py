"""
Browser Worker - 浏览器自动化
使用 Playwright 进行网页操作
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .base import BaseWorker, WorkerInfo


class BrowserWorker(BaseWorker):
    """
    浏览器自动化 Worker
    
    能力：
    - 打开网页
    - 点击元素
    - 输入文本
    - 截图
    - 提取内容
    - 执行 JS
    - Cookie 管理
    - 多标签页管理
    """
    
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._pages: dict[str, Page] = {}
        
    def get_info(self) -> WorkerInfo:
        return WorkerInfo(
            name="browser_worker",
            description="浏览器自动化，网页操作、抓取、截图",
            capabilities=[
                "navigate",
                "click",
                "type",
                "screenshot",
                "extract",
                "evaluate",
                "cookies",
                "tabs",
                "fill_form",
                "scroll",
                "wait",
                "close"
            ]
        )
        
    async def _ensure_browser(self, headless: bool = True):
        """确保浏览器已启动"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright 未安装。请运行: pip install playwright && playwright install")
            
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=headless)
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self._page = await self._context.new_page()
            
    async def execute(self, action: str, **kwargs) -> dict:
        """执行浏览器操作"""
        
        handlers = {
            "navigate": self._navigate,
            "open": self._navigate,
            "click": self._click,
            "type": self._type_text,
            "input": self._type_text,
            "screenshot": self._screenshot,
            "capture": self._screenshot,
            "extract": self._extract,
            "get_text": self._extract,
            "evaluate": self._evaluate,
            "js": self._evaluate,
            "cookies": self._cookies,
            "tabs": self._manage_tabs,
            "fill_form": self._fill_form,
            "scroll": self._scroll,
            "wait": self._wait,
            "close": self._close,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {"success": False, "error": f"未知操作: {action}"}
            
        try:
            # 确保浏览器启动（除 close 外）
            if action != "close":
                headless = kwargs.get("headless", True)
                await self._ensure_browser(headless=headless)
                
            return await handler(**kwargs)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _navigate(self, url: str, **kwargs) -> dict:
        """打开网页"""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
            
        await self._page.goto(url, wait_until="networkidle", timeout=kwargs.get("timeout", 30000))
        
        return {
            "success": True,
            "url": self._page.url,
            "title": await self._page.title()
        }
        
    async def _click(self, selector: str = None, text: str = None, **kwargs) -> dict:
        """点击元素"""
        if selector:
            await self._page.click(selector, timeout=kwargs.get("timeout", 10000))
        elif text:
            await self._page.get_by_text(text).first.click()
        else:
            return {"success": False, "error": "需要 selector 或 text 参数"}
            
        return {"success": True}
        
    async def _type_text(self, selector: str = None, text: str = "", value: str = "", **kwargs) -> dict:
        """输入文本"""
        text = text or value
        if selector:
            await self._page.fill(selector, text)
        else:
            await self._page.keyboard.type(text)
            
        return {"success": True}
        
    async def _screenshot(self, selector: str = None, path: str = None, full_page: bool = False, **kwargs) -> dict:
        """截图"""
        if not path:
            path = str(Path.home() / ".woclaw" / "screenshots" / f"screenshot_{asyncio.get_event_loop().time():.0f}.png")
            
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        if selector:
            element = await self._page.query_selector(selector)
            if element:
                await element.screenshot(path=path)
            else:
                return {"success": False, "error": f"元素未找到: {selector}"}
        else:
            await self._page.screenshot(path=path, full_page=full_page)
            
        return {
            "success": True,
            "path": path
        }
        
    async def _extract(self, selector: str = None, **kwargs) -> dict:
        """提取内容"""
        if selector:
            elements = await self._page.query_selector_all(selector)
            texts = []
            for el in elements:
                text = await el.text_content()
                if text:
                    texts.append(text.strip())
            return {"success": True, "texts": texts}
        else:
            # 提取整个页面文本
            text = await self._page.text_content("body")
            return {"success": True, "text": text.strip() if text else ""}
            
    async def _evaluate(self, script: str, **kwargs) -> dict:
        """执行 JavaScript"""
        result = await self._page.evaluate(script)
        return {"success": True, "result": result}
        
    async def _cookies(self, action: str = "get", cookies: list = None, **kwargs) -> dict:
        """Cookie 管理"""
        if action == "get":
            cookies = await self._context.cookies()
            return {"success": True, "cookies": cookies}
        elif action == "set" and cookies:
            await self._context.add_cookies(cookies)
            return {"success": True}
        elif action == "clear":
            await self._context.clear_cookies()
            return {"success": True}
        return {"success": False, "error": f"未知 cookie 操作: {action}"}
        
    async def _manage_tabs(self, action: str = "list", url: str = None, index: int = 0, **kwargs) -> dict:
        """标签页管理"""
        if action == "list":
            pages = self._context.pages
            return {
                "success": True,
                "tabs": [
                    {"index": i, "url": p.url, "title": await p.title()}
                    for i, p in enumerate(pages)
                ]
            }
        elif action == "new" and url:
            page = await self._context.new_page()
            await page.goto(url)
            return {"success": True, "index": len(self._context.pages) - 1}
        elif action == "switch":
            pages = self._context.pages
            if 0 <= index < len(pages):
                self._page = pages[index]
                return {"success": True, "url": self._page.url}
        elif action == "close":
            pages = self._context.pages
            if 0 <= index < len(pages) and len(pages) > 1:
                await pages[index].close()
                return {"success": True}
        return {"success": False, "error": f"未知标签页操作: {action}"}
        
    async def _fill_form(self, fields: list[dict], submit: str = None, **kwargs) -> dict:
        """填充表单"""
        for field in fields:
            selector = field.get("selector")
            value = field.get("value")
            if selector and value:
                await self._page.fill(selector, value)
                
        if submit:
            await self._page.click(submit)
            
        return {"success": True}
        
    async def _scroll(self, direction: str = "down", amount: int = 500, **kwargs) -> dict:
        """滚动页面"""
        if direction == "down":
            await self._page.mouse.wheel(0, amount)
        elif direction == "up":
            await self._page.mouse.wheel(0, -amount)
        elif direction == "bottom":
            await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        elif direction == "top":
            await self._page.evaluate("window.scrollTo(0, 0)")
            
        return {"success": True}
        
    async def _wait(self, selector: str = None, timeout: int = 30000, **kwargs) -> dict:
        """等待元素"""
        if selector:
            await self._page.wait_for_selector(selector, timeout=timeout)
        else:
            await asyncio.sleep(kwargs.get("seconds", 1))
            
        return {"success": True}
        
    async def _close(self, **kwargs) -> dict:
        """关闭浏览器"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
            
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            
        return {"success": True}
        
    async def shutdown(self):
        """清理资源"""
        await self._close()
