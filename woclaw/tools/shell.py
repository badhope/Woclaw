"""
Shell 命令执行工具
"""

import asyncio
from typing import Any, ClassVar

from woclaw.tools.base import BaseTool


class ShellTool(BaseTool):
    """
    Shell 命令执行工具
    """
    
    name: ClassVar[str] = "shell"
    description: ClassVar[str] = "执行系统命令"
    
    async def execute(
        self,
        command: str,
        cwd: str | None = None,
        timeout: int = 300,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        执行 Shell 命令
        
        Args:
            command: 要执行的命令
            cwd: 工作目录
            timeout: 超时时间（秒）
            env: 环境变量
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
