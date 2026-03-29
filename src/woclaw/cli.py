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
from .workers.browser_worker import BrowserWorker
from .workers.code_worker import CodeWorker
from .llm.registry import LLMRegistry
from .skills.manager import SkillManager


console = Console()


def print_banner():
    """打印品牌 Banner"""
    banner = """
✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

        ╔═══════════════════════════════════════╗
        ║                                       ║
        ║   🌟 Woclaw - 启明星 AI 助手 🌟      ║
        ║                                       ║
        ║   让启明星照亮你的电脑世界            ║
        ║                                       ║
        ║   版本: """ + __version__ + """                       ║
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
    if config is None:
        config = {
            "llm": {
                "provider": os.getenv("WOCLAW_LLM", "ollama"),
                "model": os.getenv("WOCLAW_MODEL", "llama3.2"),
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            }
        }

    supervisor = Supervisor(config)

    # 注册 Workers
    supervisor.register_worker("shell", ShellWorker())
    supervisor.register_worker("file_worker", FileWorker())
    supervisor.register_worker("gui_worker", GuiWorker())
    supervisor.register_worker("web_worker", WebWorker())
    supervisor.register_worker("sys_worker", SysWorker())
    supervisor.register_worker("browser_worker", BrowserWorker())
    supervisor.register_worker("code_worker", CodeWorker())

    await supervisor.load_learnings()

    return supervisor


@click.group()
@click.version_option(version=__version__, prog_name="Woclaw")
def cli():
    """🌟 Woclaw - 启明星 AI 助手"""
    pass


@cli.command()
@click.argument("task", required=False)
@click.option("--model", "-m", help="使用的模型")
@click.option("--no-stream", is_flag=True, help="禁用流式输出")
def run(task: Optional[str], model: Optional[str], no_stream: bool):
    """执行任务"""
    print_banner()

    async def _run():
        print_star()
        console.print("星灵正在启动... ✨\n")

        try:
            supervisor = await init_supervisor()
            print_star()
            console.print(f"星灵已就绪！使用模型: {supervisor.llm.__class__.__name__}\n")

            if task:
                await execute_task(supervisor, task, stream=not no_stream)
            else:
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
    """启动交互式聊天"""
    print_banner()

    async def _chat():
        try:
            supervisor = await init_supervisor()
            print_star()
            console.print("星灵已上线！开始聊天吧~\n")
            console.print("输入 'exit' 或 'quit' 退出\n")
            await interactive_mode(supervisor)
        except Exception as e:
            console.print(f"\n❌ 启动失败: {str(e)}", style="red bold")

    asyncio.run(_chat())


@cli.command()
def status():
    """查看状态"""
    async def _status():
        try:
            supervisor = await init_supervisor()

            table = Table(title="✨ Woclaw 状态")
            table.add_column("项目", style="cyan")
            table.add_column("值", style="green")

            table.add_row("版本", __version__)
            table.add_row("模型提供商", supervisor.llm.__class__.__name__)
            table.add_row("学习记忆", f"已加载 ({supervisor.memory._loaded})")
            table.add_row("Workers", ", ".join(supervisor.workers.keys()))

            console.print(table)

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
    """查看/设置配置"""
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
        ("DEEPSEEK_API_KEY", "DeepSeek API Key", "sk-..."),
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
    """查看可用工具"""
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
    """初始化 Woclaw"""
    print_banner()
    console.print("✨ 正在初始化 Woclaw...\n")

    config_dir = Path.home() / ".woclaw"
    config_dir.mkdir(exist_ok=True)

    learn_dir = config_dir / ".learnings"
    learn_dir.mkdir(exist_ok=True)

    skills_dir = config_dir / "skills"
    skills_dir.mkdir(exist_ok=True)

    console.print(f"✅ 配置目录: {config_dir}")
    console.print(f"✅ 学习目录: {learn_dir}")
    console.print(f"✅ 技能目录: {skills_dir}")

    console.print("\n✨ 初始化完成！")
    console.print("\n💡 接下来：")
    console.print("   1. 运行 'woclaw chat' 开始对话")
    console.print("   2. 运行 'woclaw config' 查看配置选项")
    console.print("   3. 运行 'woclaw skill list' 查看可用技能")


# ==================== Skill 命令 ====================

@cli.group()
def skill():
    """技能管理"""
    pass


@skill.command("list")
def skill_list():
    """列出可用技能"""
    async def _list():
        manager = SkillManager()
        
        # 搜索所有技能
        skills = await manager.search()
        
        if skills:
            console.print("\n📦 官方技能仓库\n")
            table = Table()
            table.add_column("名称", style="cyan")
            table.add_column("描述", style="white")
            table.add_column("分类", style="green")
            table.add_column("状态", style="yellow")
            
            for s in skills:
                status = "✅ 已安装" if s.installed else "⬜ 未安装"
                table.add_row(s.name, s.description[:40], s.category, status)
                
            console.print(table)
        else:
            console.print("\n⚠️ 无法获取技能列表，请检查网络连接")
            
        # 列出已安装
        installed = manager.list_installed()
        if installed:
            console.print(f"\n📦 已安装技能 ({len(installed)})\n")
            for s in installed:
                console.print(f"  ✅ {s.name} - {s.description}")
                
    asyncio.run(_list())


@skill.command("install")
@click.argument("name")
def skill_install(name: str):
    """安装技能"""
    async def _install():
        manager = SkillManager()
        result = await manager.install(name)
        
        if result.get("success"):
            console.print(f"\n✅ 技能安装成功: {result.get('skill', name)}\n")
        else:
            console.print(f"\n❌ 安装失败: {result.get('error', '未知错误')}\n")
            
    asyncio.run(_install())


@skill.command("run")
@click.argument("name")
@click.argument("args", nargs=-1)
def skill_run(name: str, args: tuple):
    """运行技能"""
    async def _run():
        manager = SkillManager()
        result = await manager.run(name, list(args))
        
        if result.get("success"):
            console.print(result.get("stdout", ""))
        else:
            console.print(f"\n❌ 执行失败: {result.get('error', '未知错误')}\n")
            
    asyncio.run(_run())


@skill.command("uninstall")
@click.argument("name")
def skill_uninstall(name: str):
    """卸载技能"""
    manager = SkillManager()
    result = manager.uninstall(name)
    
    if result.get("success"):
        console.print(f"\n✅ 技能已卸载: {name}\n")
    else:
        console.print(f"\n❌ 卸载失败: {result.get('error', '未知错误')}\n")


@skill.command("search")
@click.argument("keyword", required=False)
def skill_search(keyword: Optional[str]):
    """搜索技能"""
    async def _search():
        manager = SkillManager()
        skills = await manager.search(keyword or "")
        
        if skills:
            console.print(f"\n🔍 搜索结果 ({len(skills)} 个)\n")
            for s in skills:
                console.print(f"  • {s.name} - {s.description}")
        else:
            console.print("\n未找到匹配的技能\n")
            
    asyncio.run(_search())


# ==================== Gateway 命令 ====================

@cli.group()
def gateway():
    """消息网关管理"""
    pass


@gateway.command("start")
@click.option("--wechat", is_flag=True, help="启动微信网关")
@click.option("--dingtalk", is_flag=True, help="启动钉钉网关")
@click.option("--feishu", is_flag=True, help="启动飞书网关")
@click.option("--telegram", is_flag=True, help="启动 Telegram 网关")
@click.option("--all", "all_gateways", is_flag=True, help="启动所有网关")
def gateway_start(wechat: bool, dingtalk: bool, feishu: bool, telegram: bool, all_gateways: bool):
    """启动消息网关"""
    async def _start():
        from ..gateway import MessageHub, WechatGateway, DingtalkGateway, FeishuGateway, TelegramGateway
        
        supervisor = await init_supervisor()
        hub = MessageHub(supervisor)
        
        if all_gateways or wechat:
            hub.register_gateway("wechat", WechatGateway())
        if all_gateways or dingtalk:
            hub.register_gateway("dingtalk", DingtalkGateway())
        if all_gateways or feishu:
            hub.register_gateway("feishu", FeishuGateway())
        if all_gateways or telegram:
            hub.register_gateway("telegram", TelegramGateway())
            
        results = await hub.start_all()
        
        console.print("\n✨ 消息网关启动结果：\n")
        for name, success in results.items():
            status = "✅ 已启动" if success else "❌ 失败"
            console.print(f"  {name}: {status}")
            
        if any(results.values()):
            console.print("\n✨ 网关已就绪，等待消息...\n")
            console.print("按 Ctrl+C 退出\n")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await hub.stop_all()
                console.print("\n✨ 网关已停止\n")
                
    asyncio.run(_start())


# ==================== 辅助函数 ====================

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
                console.print(Panel(result.output, title="✨ 星灵回复", border_style="green"))
            elif isinstance(result.output, dict):
                if "content" in result.output:
                    console.print(Panel(result.output["content"], title="✨ 星灵回复", border_style="green"))
                else:
                    console.print(result.output)
            elif isinstance(result.output, list):
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
