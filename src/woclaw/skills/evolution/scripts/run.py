"""
🧬 Woclaw Evolution Skill - AI进化引擎
让AI自主创造、优化、进化技能
"""

import os
import sys
import json
import asyncio
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent
MODULES_PATH = SKILL_PATH / "modules"
sys.path.insert(0, str(MODULES_PATH))

from evolution_engine import EvolutionEngine


async def main(config: dict, context: dict = None):
    """
    进化技能入口函数

    Args:
        config: 技能配置
        context: 执行上下文，包含：
            - task: 用户任务描述
            - llm: LLM实例
            - skill_manager: 技能管理器实例
            - mode: 运行模式 (auto, manual)
    """
    context = context or {}
    task = context.get("task", "")
    mode = context.get("mode", "auto")

    print("=" * 60)
    print("🧬 AI EVOLUTION ENGINE - 进化引擎启动")
    print("=" * 60)

    engine = EvolutionEngine(
        skill_path=SKILL_PATH,
        config=config,
        llm=context.get("llm"),
        skill_manager=context.get("skill_manager")
    )

    if not task:
        print("\n📋 使用方法:")
        print("  evolution.evolve(task) - 针对任务触发进化")
        print("  evolution.status() - 查看进化状态")
        print("  evolution.list_skills() - 列出所有已进化技能")
        print("  evolution.optimize(skill_name) - 优化特定技能")
        print("  evolution.speciate() - 触发物种进化")
        return {"success": True, "message": "进化引擎已就绪"}

    print(f"\n🎯 触发进化任务: {task}")
    print(f"⚙️  运行模式: {mode}")

    result = await engine.start_evolution_cycle(task, mode)

    print("\n" + "=" * 60)
    if result["success"]:
        print(f"✅ 进化循环完成: {result['message']}")
        if "new_skill" in result:
            print(f"🧬 新技能诞生: {result['new_skill']}")
        if "evolved_skills" in result:
            print(f"🌟 进化技能数: {result['evolved_skills']}")
    else:
        print(f"❌ 进化中断: {result.get('error', '未知错误')}")
    print("=" * 60)

    return result


async def evolve(task: str, context: dict = None):
    """触发进化循环"""
    return await main({}, {"task": task, "mode": "auto", **(context or {})})


async def status(context: dict = None):
    """查看进化状态"""
    context = context or {}
    engine = EvolutionEngine(skill_path=SKILL_PATH, config={}, llm=context.get("llm"))
    return await engine.get_status()


async def list_skills(context: dict = None):
    """列出所有已进化的技能"""
    context = context or {}
    engine = EvolutionEngine(skill_path=SKILL_PATH, config={}, llm=context.get("llm"))
    return await engine.list_evolved_skills()


async def optimize(skill_name: str, context: dict = None):
    """优化特定技能"""
    context = context or {}
    engine = EvolutionEngine(skill_path=SKILL_PATH, config={}, llm=context.get("llm"))
    return await engine.optimize_skill(skill_name)


async def speciate(context: dict = None):
    """触发物种进化"""
    context = context or {}
    engine = EvolutionEngine(skill_path=SKILL_PATH, config={}, llm=context.get("llm"))
    return await engine.trigger_speciation()


if __name__ == "__main__":
    asyncio.run(main({}))
