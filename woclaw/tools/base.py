"""
工具基类
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class BaseTool(ABC):
    """
    工具抽象基类
    """
    
    name: ClassVar[str] = "base"
    description: ClassVar[str] = "Base tool"
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        执行工具
        """
        pass
    
    def get_schema(self) -> dict[str, Any]:
        """
        获取工具的 JSON Schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    def _get_parameters_schema(self) -> dict[str, Any]:
        """
        获取参数 Schema，子类可重写
        """
        return {}


class ToolRegistry:
    """
    工具注册中心
    """
    
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """
        注册默认工具
        """
        from woclaw.tools.filesystem import FilesystemTool
        from woclaw.tools.shell import ShellTool
        from woclaw.tools.browser import BrowserTool
        from woclaw.tools.web import WebTool
        from woclaw.tools.data import DataTool
        from woclaw.tools.process import ProcessTool
        from woclaw.tools.clipboard import ClipboardTool
        from woclaw.tools.system import SystemTool
        from woclaw.tools.network import NetworkTool
        from woclaw.tools.screenshot import ScreenshotTool
        from woclaw.tools.automation import AutomationTool
        from woclaw.tools.archive import ArchiveTool
        from woclaw.tools.image import ImageTool
        
        self.register(FilesystemTool())
        self.register(ShellTool())
        self.register(BrowserTool())
        self.register(WebTool())
        self.register(DataTool())
        self.register(ProcessTool())
        self.register(ClipboardTool())
        self.register(SystemTool())
        self.register(NetworkTool())
        self.register(ScreenshotTool())
        self.register(AutomationTool())
        self.register(ArchiveTool())
        self.register(ImageTool())
    
    def register(self, tool: BaseTool):
        """
        注册工具
        """
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> BaseTool | None:
        """
        获取工具
        """
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        """
        列出所有工具
        """
        return list(self._tools.keys())
    
    def get_schemas(self) -> list[dict[str, Any]]:
        """
        获取所有工具的 Schema
        """
        return [tool.get_schema() for tool in self._tools.values()]
