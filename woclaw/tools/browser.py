"""
浏览器控制工具
"""

from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class BrowserTool(BaseTool):
    """
    浏览器控制工具（混合模式：无头 + 真实浏览器）
    """
    
    name: ClassVar[str] = "browser"
    description: ClassVar[str] = "浏览器控制：打开网页、点击、输入、截图"
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
    
    async def execute(
        self,
        action: str,
        headless: bool = True,
        **kwargs
    ) -> Any:
        """
        执行浏览器操作
        
        Args:
            action: 操作类型
                - navigate: 导航到 URL
                - click: 点击元素
                - type: 输入文字
                - screenshot: 截图
                - content: 获取页面内容
                - wait: 等待元素
                - close: 关闭浏览器
            headless: 是否无头模式
        """
        handlers = {
            "navigate": self._navigate,
            "click": self._click,
            "type": self._type,
            "screenshot": self._screenshot,
            "content": self._content,
            "wait": self._wait,
            "close": self._close,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(headless=headless, **kwargs)
    
    async def _ensure_browser(self, headless: bool = True):
        if self._browser is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(headless=headless)
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()
            except ImportError:
                raise ImportError("Please install playwright: pip install playwright && playwright install")
    
    async def _navigate(self, url: str, headless: bool = True, **kwargs) -> str:
        await self._ensure_browser(headless)
        await self._page.goto(url)
        return url
    
    async def _click(self, selector: str, headless: bool = True, **kwargs) -> bool:
        await self._ensure_browser(headless)
        await self._page.click(selector)
        return True
    
    async def _type(self, selector: str, text: str, headless: bool = True, **kwargs) -> bool:
        await self._ensure_browser(headless)
        await self._page.fill(selector, text)
        return True
    
    async def _screenshot(self, path: str, headless: bool = True, **kwargs) -> str:
        await self._ensure_browser(headless)
        await self._page.screenshot(path=path)
        return path
    
    async def _content(self, headless: bool = True, **kwargs) -> str:
        await self._ensure_browser(headless)
        return await self._page.content()
    
    async def _wait(self, selector: str, timeout: int = 30000, headless: bool = True, **kwargs) -> bool:
        await self._ensure_browser(headless)
        await self._page.wait_for_selector(selector, timeout=timeout)
        return True
    
    async def _close(self, **kwargs) -> bool:
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
        return True
