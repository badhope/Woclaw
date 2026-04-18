"""
ShellWorker - Shell 命令执行
负责执行系统命令
"""

import asyncio
import shlex
from typing import Any, ClassVar
from pathlib import Path

from .base import BaseWorker


class ShellWorker(BaseWorker):
    """
    Shell 命令执行 Worker
    用于执行系统命令和脚本
    """

    name = "shell"
    description = "执行系统命令和脚本"
    capabilities = [
        "execute_command",
        "run_script",
        "check_command",
    ]

    async def execute(self, action: str, **kwargs) -> dict:
        """
        执行 Shell 命令

        Args:
            action: 操作类型
                - execute: 执行命令
                - run_script: 运行脚本
                - check: 检查命令是否存在

        **kwargs:
            command: str - 要执行的命令
            cwd: str - 工作目录
            timeout: int - 超时时间（秒）
            shell: bool - 是否使用 shell
        """
        handlers = {
            "execute": self._execute_command,
            "run_script": self._run_script,
            "check": self._check_command,
        }

        handler = handlers.get(action, self._execute_command)
        return await handler(**kwargs)

    async def _execute_command(
        self,
        command: str,
        cwd: str = None,
        timeout: int = 300,
        shell: bool = False,
        env: dict = None,
    ) -> dict:
        """
        执行命令

        Args:
            command: 命令
            cwd: 工作目录
            timeout: 超时（秒）
            shell: 是否使用 shell
            env: 环境变量
        """
        try:
            # 构建命令
            if not shell:
                # 分割命令避免 shell 注入
                cmd = shlex.split(command)
            else:
                cmd = command

            # 创建进程
            process = await asyncio.create_subprocess_shell(
                command if shell else cmd[0],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            # 等待结果
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                return {
                    "success": process.returncode == 0,
                    "returncode": process.returncode,
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "command": command,
                }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"命令执行超时（{timeout}秒）",
                    "command": command,
                    "returncode": -1,
                }

        except FileNotFoundError:
            return {
                "success": False,
                "error": f"命令未找到: {command.split()[0]}",
                "command": command,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }

    async def _run_script(
        self,
        script: str,
        language: str = "bash",
        cwd: str = None,
        timeout: int = 300,
    ) -> dict:
        """
        运行脚本

        Args:
            script: 脚本内容
            language: 语言 (bash/powershell/python)
            cwd: 工作目录
            timeout: 超时
        """
        # 临时脚本文件
        import tempfile

        suffix_map = {
            "bash": ".sh",
            "powershell": ".ps1",
            "python": ".py",
        }
        suffix = suffix_map.get(language, ".txt")

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=suffix,
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(script)
            script_path = f.name

        try:
            if language == "bash":
                command = f"bash {script_path}"
            elif language == "powershell":
                command = f"powershell -File {script_path}"
            elif language == "python":
                command = f"python {script_path}"
            else:
                return {"success": False, "error": f"不支持的语言: {language}"}

            return await self._execute_command(command, cwd=cwd, timeout=timeout)
        finally:
            # 清理临时文件
            Path(script_path).unlink(missing_ok=True)

    async def _check_command(self, command: str) -> dict:
        """检查命令是否存在"""
        import shutil

        cmd_name = command.split()[0] if " " in command else command
        result = shutil.which(cmd_name)

        return {
            "exists": result is not None,
            "path": result,
            "command": cmd_name,
        }
