"""
键盘鼠标自动化工具
"""

import asyncio
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class AutomationTool(BaseTool):
    """
    键盘鼠标自动化工具
    """
    
    name: ClassVar[str] = "automation"
    description: ClassVar[str] = "键盘鼠标自动化：模拟按键、鼠标操作"
    
    async def execute(self, action: str, **kwargs) -> Any:
        """
        执行自动化操作
        
        Args:
            action: 操作类型
                - key_press: 按键
                - key_hotkey: 组合键
                - type_text: 输入文字
                - mouse_click: 鼠标点击
                - mouse_move: 鼠标移动
                - mouse_scroll: 鼠标滚动
                - mouse_drag: 鼠标拖拽
                - get_position: 获取鼠标位置
        """
        handlers = {
            "key_press": self._key_press,
            "key_hotkey": self._key_hotkey,
            "type_text": self._type_text,
            "mouse_click": self._mouse_click,
            "mouse_move": self._mouse_move,
            "mouse_scroll": self._mouse_scroll,
            "mouse_drag": self._mouse_drag,
            "get_position": self._get_position,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**kwargs)
    
    def _get_pyautogui(self):
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            return pyautogui
        except ImportError:
            raise ImportError("Please install pyautogui: pip install pyautogui")
    
    async def _key_press(self, key: str, presses: int = 1, interval: float = 0.1) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.press(key, presses=presses, interval=interval)
            return {"success": True, "key": key, "presses": presses}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _key_hotkey(self, *keys: str) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.hotkey(*keys)
            return {"success": True, "keys": list(keys)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _type_text(self, text: str, interval: float = 0.05) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.typewrite(text, interval=interval)
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _mouse_click(
        self,
        x: int | None = None,
        y: int | None = None,
        button: str = "left",
        clicks: int = 1
    ) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.click(x=x, y=y, button=button, clicks=clicks)
            return {"success": True, "x": x, "y": y, "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _mouse_move(
        self,
        x: int,
        y: int,
        duration: float = 0.5
    ) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.moveTo(x, y, duration=duration)
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _mouse_scroll(
        self,
        clicks: int,
        x: int | None = None,
        y: int | None = None
    ) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.scroll(clicks, x=x, y=y)
            return {"success": True, "clicks": clicks}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _mouse_drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: str = "left"
    ) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            pg.moveTo(start_x, start_y)
            pg.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
            return {
                "success": True,
                "start": (start_x, start_y),
                "end": (end_x, end_y),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_position(self) -> dict[str, Any]:
        try:
            pg = self._get_pyautogui()
            x, y = pg.position()
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
