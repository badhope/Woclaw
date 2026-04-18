"""
GuiWorker - GUI 操控 Worker
使用 Windows UI Automation 操控桌面应用
"""

import asyncio
from typing import Any, ClassVar, Optional
from dataclasses import dataclass

from .base import BaseWorker


@dataclass
class WindowInfo:
    """窗口信息"""
    title: str
    handle: int
    process_id: int
    process_name: str
    rect: tuple[int, int, int, int]  # left, top, right, bottom


class GuiWorker(BaseWorker):
    """
    GUI 操控 Worker
    基于 pywinauto 的 Windows UI Automation

    功能：
    - 窗口管理（查找、激活、最小化、关闭）
    - 控件操作（点击、输入、获取文本）
    - 截图
    - 快捷键
    """

    name = "gui_worker"
    description = "GUI 图形界面操控 - 控制窗口应用"
    capabilities = [
        "window_find",
        "window_activate",
        "window_close",
        "control_click",
        "control_type",
        "control_get_text",
        "screenshot",
        "hotkey",
    ]

    def __init__(self):
        super().__init__()
        self._app = None
        self._backend = "win32"  # win32 is more reliable for basic operations

    async def execute(self, action: str, **kwargs) -> dict:
        """执行 GUI 操作"""
        handlers = {
            "window_find": self._find_window,
            "window_activate": self._activate_window,
            "window_close": self._close_window,
            "window_list": self._list_windows,
            "control_click": self._click_control,
            "control_type": self._type_control,
            "control_get_text": self._get_control_text,
            "screenshot": self._take_screenshot,
            "hotkey": self._send_hotkey,
            "wait_for_window": self._wait_for_window,
            "get_desktop": self._get_desktop_info,
        }

        handler = handlers.get(action)
        if not handler:
            return {"success": False, "error": f"未知操作: {action}"}

        return await handler(**kwargs)

    def _get_pywinauto(self):
        """获取 pywinauto 模块"""
        try:
            from pywinauto import Application, findwindows, timings
            from pywinauto.controls import common_controls
            return Application, findwindows, timings
        except ImportError:
            raise ImportError(
                "✨ 星灵需要 pywinauto 来操控窗口应用~\n"
                "请运行: pip install pywinauto"
            )

    async def _find_window(self, title: str = None, process: int = None, **kwargs) -> dict:
        """查找窗口"""
        try:
            from pywinauto import Application
            from pywinauto.findwindows import find_windows

            # 使用 visible_only=False 以找到所有窗口
            if process:
                windows = find_windows(process=process, backend=self._backend, visible_only=False)
            elif title:
                windows = find_windows(title_re=f".*{title}.*", backend=self._backend, visible_only=False)
            else:
                windows = find_windows(backend=self._backend, visible_only=False)

            result = []
            for hwnd in windows:
                try:
                    app = Application(backend=self._backend).from_hwnd(hwnd)
                    window = app.window()
                    title_text = window.window_text()
                    
                    if title_text:  # Only include windows with titles
                        rect = window.rect()
                        result.append({
                            "title": title_text,
                            "handle": hwnd,
                            "rect": {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom},
                            "width": rect.width(),
                            "height": rect.height(),
                        })
                except Exception:
                    continue

            return {"success": True, "windows": result, "count": len(result)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _activate_window(self, title: str = None, handle: int = None, **kwargs) -> dict:
        """激活窗口"""
        try:
            from pywinauto import Application

            if handle:
                app = Application(backend=self._backend).from_hwnd(handle)
            elif title:
                # Try direct title first, then regex
                try:
                    app = Application(backend=self._backend).connect(title=title, timeout=2)
                except Exception:
                    app = Application(backend=self._backend).connect(title_re=f".*{title}.*", timeout=2)
            else:
                return {"success": False, "error": "需要提供 title 或 handle"}

            window = app.window()
            window.set_focus()
            window.restore()
            window.wait("visible", timeout=5)

            return {"success": True, "title": window.window_text()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _close_window(self, title: str = None, handle: int = None, **kwargs) -> dict:
        """关闭窗口"""
        try:
            from pywinauto import Application

            if handle:
                app = Application(backend=self._backend).from_hwnd(handle)
                window = app.window()
                window.close()
            elif title:
                # Try direct title first
                try:
                    app = Application(backend=self._backend).connect(title=title, timeout=2)
                    app.window().close()
                except Exception:
                    # Try to close all matching windows
                    from pywinauto.findwindows import find_windows
                    wins = find_windows(title_re=f".*{title}.*", backend=self._backend, visible_only=False)
                    for h in wins:
                        try:
                            a = Application(backend=self._backend).from_hwnd(h)
                            a.window().close()
                        except:
                            pass
            else:
                return {"success": False, "error": "需要提供 title 或 handle"}

            return {"success": True, "message": "窗口已关闭"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _list_windows(self, **kwargs) -> dict:
        """列出所有窗口"""
        return await self._find_window(**kwargs)

    async def _click_control(
        self,
        window_title: str,
        control_text: str = None,
        control_type: str = None,
        button: str = "left",
        double: bool = False,
        **kwargs
    ) -> dict:
        """点击控件"""
        try:
            from pywinauto import Application
            from pywinauto.findwindows import find_windows

            # 查找窗口
            wins = find_windows(title_re=f".*{window_title}.*", backend=self._backend, visible_only=False)
            
            if not wins:
                return {"success": False, "error": f"未找到窗口: {window_title}"}
            
            app = Application(backend=self._backend).from_hwnd(wins[0])
            window = app.window()

            # 激活窗口
            window.set_focus()

            # 查找控件
            if control_text:
                try:
                    if double:
                        window[control_text].double_click_input(button=button)
                    else:
                        window[control_text].click_input(button=button)
                except Exception:
                    # 尝试模糊匹配
                    children = window.children()
                    for child in children:
                        try:
                            if control_text.lower() in child.window_text().lower():
                                if double:
                                    child.double_click_input(button=button)
                                else:
                                    child.click_input(button=button)
                                return {"success": True, "control": child.window_text()}
                        except Exception:
                            continue
                    return {"success": False, "error": f"未找到控件: {control_text}"}

            return {"success": True, "control": control_text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _type_control(
        self,
        window_title: str,
        control_text: str,
        text: str,
        **kwargs
    ) -> dict:
        """向控件输入文本"""
        try:
            from pywinauto import Application

            app = Application(backend=self._backend).connect(title_re=f".*{window_title}.*")
            window = app.window()
            window.set_focus()

            # 查找并聚焦控件
            window[control_text].set_focus()
            window[control_text].type_keys(text, with_spaces=True)

            return {"success": True, "text": text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_control_text(self, window_title: str, control_text: str, **kwargs) -> dict:
        """获取控件文本"""
        try:
            from pywinauto import Application

            app = Application(backend=self._backend).connect(title_re=f".*{window_title}.*")
            window = app.window()

            text = window[control_text].window_text()

            return {"success": True, "text": text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _take_screenshot(
        self,
        window_title: str = None,
        save_path: str = None,
        **kwargs
    ) -> dict:
        """截图"""
        try:
            import pyscreeze
            from PIL import Image
            import os

            if save_path is None:
                import tempfile
                save_path = os.path.join(tempfile.gettempdir(), "woclaw_screenshot.png")

            if window_title:
                from pywinauto import Application
                from pywinauto.findwindows import find_windows

                # Find all matching windows and use the first one
                wins = find_windows(title_re=f".*{window_title}.*", backend=self._backend, visible_only=False)
                
                if wins:
                    app = Application(backend=self._backend).from_hwnd(wins[0])
                    window = app.window()
                    rect = window.rect()
                    
                    # 使用 PIL 截图指定区域
                    img = pyscreeze.screenshot(region=(
                        rect.left, rect.top, rect.width(), rect.height()
                    ))
                else:
                    # 回退到全屏
                    img = pyscreeze.screenshot()
            else:
                # 全屏截图
                img = pyscreeze.screenshot()

            img.save(save_path)

            return {"success": True, "path": save_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_hotkey(self, *keys: str, **kwargs) -> dict:
        """发送快捷键"""
        try:
            from pywinauto import keyboard

            # 转换按键格式
            key_combo = "+".join(keys)
            keyboard.send_keys(key_combo)

            return {"success": True, "keys": list(keys)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _wait_for_window(self, title: str, timeout: int = 10, **kwargs) -> dict:
        """等待窗口出现"""
        try:
            from pywinauto import Application
            from pywinauto.timings import wait_until_passes

            app = Application(backend=self._backend)
            window = app.window(title_re=f".*{title}.*")
            window.wait("visible", timeout=timeout)

            return {"success": True, "title": window.window_text()}

        except Exception as e:
            return {"success": False, "error": f"等待超时: {str(e)}"}

    async def _get_desktop_info(self, **kwargs) -> dict:
        """获取桌面信息"""
        try:
            from pywinauto import Application
            from pywinauto.findwindows import find_windows

            # 查找所有顶级窗口（包括隐藏的）
            all_windows = find_windows(backend=self._backend, visible_only=False)

            result = []
            for hwnd in all_windows:
                try:
                    app = Application(backend=self._backend).from_hwnd(hwnd)
                    window = app.window()
                    title = window.window_text()
                    if title:  # Only include windows with titles
                        result.append({
                            "title": title,
                            "handle": hwnd,
                        })
                except Exception:
                    continue

            return {"success": True, "windows": result, "count": len(result)}

        except Exception as e:
            return {"success": False, "error": str(e)}
