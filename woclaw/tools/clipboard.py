"""
剪贴板操作工具
"""

from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ClipboardTool(BaseTool):
    """
    剪贴板操作工具
    """
    
    name: ClassVar[str] = "clipboard"
    description: ClassVar[str] = "剪贴板操作：读取、写入、清空"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行剪贴板操作
        
        Args:
            action: 操作类型
                - read: 读取剪贴板内容
                - write: 写入剪贴板
                - clear: 清空剪贴板
                - read_image: 读取剪贴板图片
        """
        handlers = {
            "read": self._read,
            "write": self._write,
            "clear": self._clear,
            "read_image": self._read_image,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    def _get_clipboard(self):
        try:
            import pyperclip
            return pyperclip
        except ImportError:
            raise ImportError("Please install pyperclip: pip install pyperclip")
    
    async def _read(self) -> str:
        clipboard = self._get_clipboard()
        return clipboard.paste()
    
    async def _write(self, text: str) -> dict[str, Any]:
        clipboard = self._get_clipboard()
        clipboard.copy(text)
        return {"success": True, "content": text}
    
    async def _clear(self) -> dict[str, Any]:
        clipboard = self._get_clipboard()
        clipboard.copy("")
        return {"success": True}
    
    async def _read_image(self, save_path: str | None = None) -> dict[str, Any]:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()
            if img is None:
                return {"success": False, "error": "No image in clipboard"}
            
            if save_path:
                img.save(save_path)
                return {"success": True, "path": save_path}
            else:
                return {"success": True, "image": img}
        except ImportError:
            return {"success": False, "error": "Please install Pillow: pip install Pillow"}
