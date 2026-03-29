"""
Woclaw CLI - 启明星的命令行界面
简洁、人性化的交互体验
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table

from . import BRAND, __version__
from .supervisor.agent import Supervisor
from .workers import FileWorker, GuiWorker, ShellWorker, WebWorker, SysWorker
from .llm.registry import LLMRegistry


console = Console()


def print_banner():
    """打印品牌 Banner"""
    banner = f"""
✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

        ╔═══════════════════════════════════════╗
        ║                                       ║
        ║   🌟 Woclaw - 启明星 AI 助手 🌟      ║
        ║                                       ║
        ║   {BRAND['slogan']}   ║
        ║                                       ║
        ║   版本: {__version__}                       ║
        ║   类型: 轻量级自主电脑控制智能体         ║
        ║                                       ║
        ╚═══════════════════════════════════════╝

✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨
"""
    console.print(banner, style="cyan bold")


def print_star():
    """打印星星装饰"""
    console.print("\n✨ ", end="")


async def init_supervisor(config: dict = None) -> Supervisor:
    """初始化 Supervisor"""
    # 默认配置
    if config is None:
        config = {
            "llm": {
                "provider": os.getenv("WOCLAW_LLM", "ollama"),
                "model": os.getenv("WOCLAW_MODEL", "llama3.2"),
                "api_key": os.getenv("OPENAI_API_KEY", ""),
            }
        }

    # 创建 Supervisor
    supervisor = Supervisor(config)

    # 注册 Workers
    supervisor.register_worker("shell", ShellWorker())
    supervisor.register_worker("file_worker", FileWorker())
    supervisor.register_worker("gui_worker", GuiWorker())
    supervisor.register_worker("web_worker", WebWorker())
    supervisor.register_worker("sys_worker", SysWorker())

    # 加载学习记忆
    await supervisor.load_learnings()

    return supervisor


@click.group()
@click.version_option(version=__version__, prog_name="Woclaw")
def cli():
    """
    🌟 Woclaw - 启明星 AI 助手

    轻量级自主电脑控制智能体，让 AI 像启明星一样为你指引方向。
    """
    pass


@cli.command()
@click.argument("task", required=False)
@click.option("--model", "-m", help="使用的模型")
@click.option("--no-stream", is_flag=True, help="禁用流式输出")
def run(task: Optional[str], model: Optional[str], no_stream: bool):
    """
    执行任务

    示例：
        woclaw run "帮我整理下载文件夹"
        woclaw run "查看系统信息"
    """
    print_banner()

    async def _run():
        print_star()
        console.print("星灵正在启动... ✨\n")

        try:
            supervisor = await init_supervisor()
            print_star()
            console.print(f"星灵已就绪！使用模型: {supervisor.llm.__class__.__name__}\n")

            if task:
                # 执行单个任务
                await execute_task(supervisor, task, stream=not no_stream)
            else:
                # 交互模式
                await interactive_mode(supervisor)

        except Exception as e:
            console.print(f"\n❌ 启动失败: {str(e)}", style="red bold")
            console.print("\n💡 解决方案：")
            console.print("   1. 如果使用 Ollama，请确保 Ollama 服务正在运行")
            console.print("   2. 如果使用 API Key，请设置相应的环境变量")
            console.print("   3. 运行 'woclaw config' 进行配置\n")

    asyncio.run(_run())


@cli.command()
def chat():
    """
    启动交互式聊天

    示例：
        woclaw chat
    """
    print_banner()

    async def _chat():
        try:
            supervisor = await init_supervisor()

            print_star()
            console.print(f"星灵已上线！开始聊天吧~\n")
            console.print("输入 'exit' 或 'quit' 退出\n")

            await interactive_mode(supervisor)

        except Exception as e:
            console.print(f"\n❌ 启动失败: {str(e)}", style="red bold")

    asyncio.run(_chat())


@cli.command()
def status():
    """
    查看状态

    显示当前配置和系统信息
    """
    async def _status():
        try:
            supervisor = await init_supervisor()

            # 显示状态
            table = Table(title="✨ Woclaw 状态")
            table.add_column("项目", style="cyan")
            table.add_column("值", style="green")

            table.add_row("版本", __version__)
            table.add_row("模型提供商", supervisor.llm.__class__.__name__)
            table.add_row("学习记忆", f"已加载 ({supervisor.memory._loaded})")
            table.add_row("Workers", ", ".join(supervisor.workers.keys()))

            console.print(table)

            # 显示学习统计
            stats = supervisor.memory.get_stats()
            if stats["total_learnings"] > 0:
                console.print(f"\n📚 学习统计：")
                console.print(f"   - 成功案例: {stats['total_learnings']}")
                console.print(f"   - 错误记录: {stats['total_errors']}")
                console.print(f"   - 用户反馈: {stats['total_feedback']}")

        except Exception as e:
            console.print(f"\n❌ 获取状态失败: {str(e)}", style="red bold")

    asyncio.run(_status())


@cli.command()
def config():
    """
    查看/设置配置
    """
    console.print("\n✨ Woclaw 配置指南\n")

    table = Table(title="环境变量配置")
    table.add_column("变量名", style="cyan")
    table.add_column("说明", style="white")
    table.add_column("示例", style="green")

    configs = [
        ("WOCLAW_LLM", "模型提供商", "ollama, openai, claude, deepseek, kimi, qwen"),
        ("WOCLAW_MODEL", "模型名称", "llama3.2, gpt-4o, deepseek-chat"),
        ("OPENAI_API_KEY", "OpenAI API Key", "sk-..."),
        ("ANTHROPIC_API_KEY", "Claude API Key", "sk-ant-..."),
        ("OLLAMA_BASE_URL", "Ollama 地址", "http://localhost:11434"),
    ]

    for config in configs:
        table.add_row(*config)

    console.print(table)

    console.print("\n💡 快速配置：")
    console.print("   # 设置使用 OpenAI")
    console.print("   $env:WOCLAW_LLM = 'openai'")
    console.print("   $env:OPENAI_API_KEY = 'your-key'\n")


@cli.command()
def tools():
    """
    查看可用工具
    """
    async def _tools():
        try:
            supervisor = await init_supervisor()

            console.print("\n🛠️  Woclaw 可用工具\n")

            for name, worker in supervisor.workers.items():
                info = worker.get_info()
                console.print(f"\n✨ {name}")
                console.print(f"   {info.description}")
                console.print(f"   能力: {', '.join(info.capabilities)}")

        except Exception as e:
            console.print(f"\n❌ 获取工具列表失败: {str(e)}", style="red bold")

    asyncio.run(_tools())


@cli.command()
def init():
    """
    初始化 Woclaw

    创建默认配置和目录结构
    """
    print_banner()

    console.print("✨ 正在初始化 Woclaw...\n")

    # 创建配置目录
    config_dir = Path.home() / ".woclaw"
    config_dir.mkdir(exist_ok=True)

    # 创建学习目录
    learn_dir = config_dir / ".learnings"
    learn_dir.mkdir(exist_ok=True)

    console.print(f"✅ 配置目录: {config_dir}")
    console.print(f"✅ 学习目录: {learn_dir}")

    console.print("\n✨ 初始化完成！")
    console.print("\n💡 接下来：")
    console.print("   1. 运行 'woclaw chat' 开始对话")
    console.print("   2. 运行 'woclaw config' 查看配置选项")
    console.print("   3. 或直接告诉星灵你想做什么~")


async def interactive_mode(supervisor: Supervisor):
    """交互模式"""
    console.print("\n" + "─" * 50)
    console.print("✨ 星灵正在等待你的指令...\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]你[/bold cyan]")

            if user_input.lower() in ["exit", "quit", "q", "退出"]:
                console.print("\n✨ 星灵正在休息，再见！期待下次见面~ 🌟\n")
                break

            if not user_input.strip():
                continue

            await execute_task(supervisor, user_input)

        except KeyboardInterrupt:
            console.print("\n\n✨ 星灵正在休息，再见！🌟\n")
            break
        except Exception as e:
            console.print(f"\n❌ 出错了: {str(e)}", style="red")


async def execute_task(supervisor: Supervisor, task: str, stream: bool = True):
    """执行任务"""
    console.print(f"\n[bold yellow]✨ 星灵正在思考...[/bold yellow]")

    result = await supervisor.process(task)

    if result.success:
        console.print("\n✨ 执行结果：")

        if result.output:
            if isinstance(result.output, str):
                # 文本输出
                console.print(Panel(result.output, title="✨ 星灵回复", border_style="green"))
            elif isinstance(result.output, dict):
                # 字典输出
                if "content" in result.output:
                    console.print(Panel(result.output["content"], title="✨ 星灵回复", border_style="green"))
                else:
                    console.print(result.output)
            elif isinstance(result.output, list):
                # 列表输出
                for item in result.output:
                    if isinstance(item, dict):
                        if "result" in item:
                            console.print(f"  ✅ {item['result']}")
                        elif "error" in item:
                            console.print(f"  ❌ {item['error']}")
            else:
                console.print(result.output)
    else:
        console.print(f"\n❌ 执行失败: {result.error}", style="red bold")


def main():
    """主入口"""
    cli()


if __name__ == "__main__":
    main()
