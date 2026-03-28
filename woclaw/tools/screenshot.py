"""
截图工具
"""

from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ScreenshotTool(BaseTool):
    """
    截图工具
    """
    
    name: ClassVar[str] = "screenshot"
    description: ClassVar[str] = "截图：全屏截图、区域截图、窗口截图"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行截图操作
        
        Args:
            action: 操作类型
                - full: 全屏截图
                - region: 区域截图
                - window: 窗口截图
        """
        handlers = {
            "full": self._full,
            "region": self._region,
            "window": self._window,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    async def _full(
        self,
        save_path: str | None = None,
        format: str = "png"
    ) -> dict[str, Any]:
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab()
            
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshot_{timestamp}.{format}"
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path, format.upper())
            
            return {
                "success": True,
                "path": save_path,
                "size": img.size,
            }
        except ImportError:
            return {"success": False, "error": "Please install Pillow: pip install Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _region(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        save_path: str | None = None,
        format: str = "png"
    ) -> dict[str, Any]:
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshot_region_{timestamp}.{format}"
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path, format.upper())
            
            return {
                "success": True,
                "path": save_path,
                "size": img.size,
                "region": (x1, y1, x2, y2),
            }
        except ImportError:
            return {"success": False, "error": "Please install Pillow: pip install Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _window(
        self,
        window_title: str | None = None,
        save_path: str | None = None,
        format: str = "png"
    ) -> dict[str, Any]:
        try:
            import pygetwindow as gw
            from PIL import ImageGrab
            
            if window_title:
                window = gw.getWindowsWithTitle(window_title)
                if not window:
                    return {"success": False, "error": f"Window '{window_title}' not found"}
                window = window[0]
            else:
                window = gw.getActiveWindow()
            
            if not window:
                return {"success": False, "error": "No active window found"}
            
            bbox = (window.left, window.top, window.right, window.bottom)
            img = ImageGrab.grab(bbox=bbox)
            
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c for c in window.title if c.isalnum() or c in " _-")[:30]
                save_path = f"screenshot_{safe_title}_{timestamp}.{format}"
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path, format.upper())
            
            return {
                "success": True,
                "path": save_path,
                "size": img.size,
                "window_title": window.title,
            }
        except ImportError:
            return {
                "success": False,
                "error": "Please install: pip install Pillow pygetwindow"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
