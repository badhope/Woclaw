"""
Woclaw CLI 入口
"""

import asyncio
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from woclaw import Config, Agent


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="woclaw")
def cli():
    """
    🦀 Woclaw - 轻量级自主电脑控制智能体
    """
    pass


@cli.command()
@click.argument("task", required=False)
@click.option("--config", "-c", "config_path", help="配置文件路径")
@click.option("--model", "-m", help="使用的模型")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
def run(task: Optional[str], config_path: Optional[str], model: Optional[str], verbose: bool):
    """
    执行任务
    
    示例:
        woclaw run "从 example.com 抓取所有产品信息"
        woclaw run --config config.py
    """
    if not task and not config_path:
        console.print("[red]错误: 请提供任务或配置文件[/red]")
        sys.exit(1)
    
    config = _load_config(config_path)
    if model:
        config.llm.model = model
    
    agent = Agent(config)
    
    if task:
        _run_task(agent, task, verbose)


@cli.command()
def interactive():
    """
    启动交互模式
    """
    console.print(Panel.fit(
        "[bold cyan]🦀 Woclaw 交互模式[/bold cyan]\n"
        "输入任务，我会帮你完成。输入 'exit' 退出。",
        title="Woclaw"
    ))
    
    config = _load_config(None)
    agent = Agent(config)
    
    while True:
        try:
            task = console.input("\n[bold green]任务>[/bold green] ")
            
            if task.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]再见！[/yellow]")
                break
            
            if not task.strip():
                continue
            
            _run_task(agent, task, verbose=True)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]再见！[/yellow]")
            break


@cli.command()
@click.option("--provider", "-p", help="LLM 提供者")
def tools(provider: Optional[str]):
    """
    列出可用工具
    """
    table = Table(title="可用工具")
    table.add_column("工具名", style="cyan")
    table.add_column("描述", style="green")
    
    from woclaw.tools import ToolRegistry
    registry = ToolRegistry()
    
    for name in registry.list_tools():
        tool = registry.get(name)
        table.add_row(name, tool.description)
    
    console.print(table)


@cli.command()
def config():
    """
    显示当前配置
    """
    cfg = _load_config(None)
    
    table = Table(title="当前配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("LLM Provider", cfg.llm.provider)
    table.add_row("LLM Model", cfg.llm.model)
    table.add_row("Database Host", cfg.database.host)
    table.add_row("Browser Headless", str(cfg.browser.headless))
    table.add_row("Max Workers", str(cfg.concurrency.max_workers))
    
    console.print(table)


def _load_config(config_path: Optional[str]) -> Config:
    """
    加载配置
    """
    if config_path:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.config
    
    return Config()


def _run_task(agent: Agent, task: str, verbose: bool):
    """
    执行任务
    """
    console.print(f"\n[bold]任务:[/bold] {task}")
    
    with console.status("[bold green]执行中...[/bold green]"):
        result = agent.run_sync(task)
    
    if result.success:
        console.print("\n[bold green]✓ 任务完成[/bold green]")
        
        if verbose and result.steps:
            console.print("\n[bold]执行步骤:[/bold]")
            for i, step in enumerate(result.steps, 1):
                phase = step.get("phase", "unknown")
                console.print(f"  {i}. {phase}")
        
        if result.output:
            console.print(f"\n[bold]结果:[/bold]")
            console.print(result.output)
    else:
        console.print(f"\n[bold red]✗ 任务失败[/bold red]")
        console.print(f"[red]错误: {result.error}[/red]")


if __name__ == "__main__":
    cli()
