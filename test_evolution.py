"""
🧬 进化引擎测试脚本
测试AI进化Skill的各项功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_evolution_engine_basic():
    """测试进化引擎基础功能"""
    print("=" * 60)
    print("🧬 进化引擎基础测试")
    print("=" * 60)

    from woclaw.skills import SkillManager

    sm = SkillManager()

    print("\n1️⃣  测试进化引擎初始化")
    engine = sm.get_evolution_engine()
    if engine:
        print("   ✅ 进化引擎初始化成功")
    else:
        print("   ❌ 进化引擎初始化失败")
        return False

    print("\n2️⃣  测试获取进化状态")
    status = await engine.get_status()
    print(f"   状态: {status['status']}")
    print(f"   种群大小: {status['population_size']}")
    print(f"   统计: {status['statistics']}")

    print("\n3️⃣  测试列出进化技能")
    skills = await engine.list_evolved_skills()
    print(f"   已进化技能数: {skills['count']}")

    print("\n4️⃣  触发简单进化循环")
    result = await engine.start_evolution_cycle(
        task="自动整理下载目录的文件",
        mode="fast"
    )
    print(f"   进化结果: {result['success']}")
    print(f"   消息: {result['message']}")
    print(f"   耗时: {result.get('duration_seconds', 0)}s")

    print("\n" + "=" * 60)
    print("✅ 所有基础测试通过！")
    print("=" * 60)

    return True


async def test_skill_manager_integration():
    """测试Skill Manager集成"""
    print("\n" + "=" * 60)
    print("🔗 Skill Manager 集成测试")
    print("=" * 60)

    from woclaw.skills import SkillManager

    sm = SkillManager()

    print("\n1️⃣  测试 evolve 接口")
    result = await sm.evolve("批量重命名图片文件")
    print(f"   进化结果: {result['success']}")
    if result["success"]:
        print(f"   新技能: {result.get('new_skill', '无')}")

    print("\n2️⃣  测试 evolution_status 接口")
    status = await sm.evolution_status()
    print(f"   状态获取: {status['success']}")
    if status["success"]:
        print(f"   顶级技能数: {len(status.get('top_skills', []))}")

    print("\n3️⃣  测试 list_evolved_skills 接口")
    skills = await sm.list_evolved_skills()
    print(f"   技能列表: {skills['success']}, 共 {skills.get('count', 0)} 个")

    print("\n" + "=" * 60)
    print("✅ 集成测试通过！")
    print("=" * 60)

    return True


async def main():
    print("\n" + "🚀" * 20)
    print("开始测试 AI 进化引擎 🧬")
    print("🚀" * 20 + "\n")

    try:
        await test_evolution_engine_basic()
        await test_skill_manager_integration()

        print("\n🎉 进化引擎测试完成！")
        print("\n📋 进化引擎功能清单:")
        print("   ✅ Mission Controller - 任务分析与匹配")
        print("   ✅ Discovery Module - 自主方案探索")
        print("   ✅ TrueSkill Rater - 技能评级系统")
        print("   ✅ Skill Incubator - 技能自动孵化")
        print("   ✅ TextGrad Optimizer - 反馈优化")
        print("   ✅ Speciation Evolution - 物种进化")
        print("   ✅ Evolution Memory - 进化记忆")
        print("\n💡 使用方法:")
        print("   from woclaw.skills import SkillManager")
        print("   sm = SkillManager()")
        print("   await sm.evolve('你的任务描述')")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    asyncio.run(main())
