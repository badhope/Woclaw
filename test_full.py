# -*- coding: utf-8 -*-
"""
Woclaw 完整功能测试
模拟用户各种操作
"""

import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# 设置编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_all():
    """完整测试"""
    
    print("=" * 60)
    print("WOCLAW 完整功能测试")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # ==================== 1. 导入测试 ====================
    print("\n[1/8] 模块导入测试...")
    try:
        from woclaw import BRAND, __version__
        from woclaw.supervisor import Supervisor
        from woclaw.workers import FileWorker, GuiWorker, ShellWorker, WebWorker, SysWorker
        from woclaw.workers.browser_worker import BrowserWorker
        from woclaw.workers.code_worker import CodeWorker
        from woclaw.llm.registry import LLMRegistry
        from woclaw.skills.manager import SkillManager
        from woclaw.gateway import MessageHub
        print("  [OK] 所有模块导入成功")
        print(f"       版本: {__version__}")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] 导入失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"导入: {e}")
        return results
        
    # ==================== 2. LLM 注册表测试 ====================
    print("\n[2/8] LLM 注册表测试...")
    try:
        providers = LLMRegistry.list_providers()
        print(f"  支持的提供商: {len(providers)} 个")
        for p in providers[:6]:
            info = LLMRegistry.get_info(p)
            if info:
                print(f"    - {p}: {info.get('name', p)}")
        print("  [OK] LLM 注册表正常")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] LLM 注册表测试失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"LLM: {e}")
        
    # ==================== 3. Workers 测试 ====================
    print("\n[3/8] Workers 测试...")
    
    # ShellWorker
    print("  [3.1] ShellWorker...")
    try:
        worker = ShellWorker()
        result = await worker.execute("run", command="echo Hello")
        if result.get("success"):
            print("    [OK] ShellWorker 正常")
            results["passed"] += 1
        else:
            print(f"    [FAIL] ShellWorker 失败: {result.get('error')}")
            results["failed"] += 1
    except Exception as e:
        print(f"    [FAIL] ShellWorker 异常: {e}")
        results["failed"] += 1
        
    # FileWorker
    print("  [3.2] FileWorker...")
    try:
        worker = FileWorker()
        result = await worker.execute("list", path=str(Path.home()))
        if result.get("success"):
            print("    [OK] FileWorker 正常")
            results["passed"] += 1
        else:
            print(f"    [FAIL] FileWorker 失败: {result.get('error')}")
            results["failed"] += 1
    except Exception as e:
        print(f"    [FAIL] FileWorker 异常: {e}")
        results["failed"] += 1
        
    # SysWorker
    print("  [3.3] SysWorker...")
    try:
        worker = SysWorker()
        result = await worker.execute("info")
        if result.get("success"):
            print(f"    系统: {result.get('system', 'N/A')}")
            print("    [OK] SysWorker 正常")
            results["passed"] += 1
        else:
            print(f"    [FAIL] SysWorker 失败: {result.get('error')}")
            results["failed"] += 1
    except Exception as e:
        print(f"    [FAIL] SysWorker 异常: {e}")
        results["failed"] += 1
        
    # WebWorker
    print("  [3.4] WebWorker...")
    try:
        worker = WebWorker()
        result = await worker.execute("dns", domain="github.com")
        if result.get("success"):
            print("    [OK] WebWorker 正常")
            results["passed"] += 1
        else:
            print(f"    [FAIL] WebWorker 失败: {result.get('error')}")
            results["failed"] += 1
    except Exception as e:
        print(f"    [FAIL] WebWorker 异常: {e}")
        results["failed"] += 1
        
    # GuiWorker
    print("  [3.5] GuiWorker...")
    try:
        worker = GuiWorker()
        info = worker.get_info()
        print(f"    能力: {len(info.capabilities)} 个")
        print("    [OK] GuiWorker 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"    [FAIL] GuiWorker 异常: {e}")
        results["failed"] += 1
        
    # CodeWorker
    print("  [3.6] CodeWorker...")
    try:
        worker = CodeWorker()
        result = await worker.execute("python", code="print('Hello CodeWorker')")
        if result.get("success"):
            print(f"    输出: {result.get('stdout', '').strip()}")
            print("    [OK] CodeWorker 正常")
            results["passed"] += 1
        else:
            print(f"    [FAIL] CodeWorker 失败: {result.get('error')}")
            results["failed"] += 1
    except Exception as e:
        print(f"    [FAIL] CodeWorker 异常: {e}")
        results["failed"] += 1
        
    # BrowserWorker
    print("  [3.7] BrowserWorker...")
    try:
        worker = BrowserWorker()
        info = worker.get_info()
        print(f"    能力: {len(info.capabilities)} 个")
        print("    [OK] BrowserWorker 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"    [FAIL] BrowserWorker 异常: {e}")
        results["failed"] += 1
        
    # ==================== 4. Learning Memory 测试 ====================
    print("\n[4/8] Learning Memory 测试...")
    try:
        from woclaw.learning.memory import LearningMemory
        memory = LearningMemory()
        await memory.load()
        
        # 记录测试
        await memory.record_success("测试任务", [{"step": 1}])
        await memory.save()
        
        stats = memory.get_stats()
        print(f"  学习记录: {stats['total_learnings']} 条")
        print("  [OK] Learning Memory 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Learning Memory 测试失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"Memory: {e}")
        
    # ==================== 5. Skill Manager 测试 ====================
    print("\n[5/8] Skill Manager 测试...")
    try:
        manager = SkillManager()
        
        # 列出已安装
        installed = manager.list_installed()
        print(f"  已安装技能: {len(installed)} 个")
        
        print("  [OK] Skill Manager 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Skill Manager 测试失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"Skill: {e}")
        
    # ==================== 6. Message Gateway 测试 ====================
    print("\n[6/8] Message Gateway 测试...")
    try:
        from woclaw.gateway import MessageHub, DingtalkGateway, FeishuGateway
        
        hub = MessageHub(None)
        hub.register_gateway("dingtalk", DingtalkGateway())
        hub.register_gateway("feishu", FeishuGateway())
        
        print(f"  注册网关: {len(hub.gateways)} 个")
        print("  [OK] Message Gateway 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Message Gateway 测试失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"Gateway: {e}")
        
    # ==================== 7. Supervisor 测试 ====================
    print("\n[7/8] Supervisor 测试...")
    try:
        config = {
            "llm": {
                "provider": "ollama",
                "model": "llama3.2",
                "base_url": "http://localhost:11434"
            }
        }
        
        supervisor = Supervisor(config)
        supervisor.register_worker("shell", ShellWorker())
        supervisor.register_worker("file_worker", FileWorker())
        supervisor.register_worker("sys_worker", SysWorker())
        supervisor.register_worker("code_worker", CodeWorker())
        
        print(f"  注册 Workers: {len(supervisor.workers)} 个")
        print("  [OK] Supervisor 正常")
        results["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Supervisor 测试失败: {e}")
        results["failed"] += 1
        results["errors"].append(f"Supervisor: {e}")
        
    # ==================== 8. 用户模拟测试 ====================
    print("\n[8/8] 用户操作模拟测试...")
    
    test_cases = [
        ("查看系统信息", "sys_worker", "info", {}),
        ("列出当前目录文件", "file_worker", "list", {"path": "."}),
        ("执行简单命令", "shell", "run", {"command": "dir" if os.name == 'nt' else "ls"}),
        ("执行 Python 代码", "code_worker", "python", {"code": "import sys; print(sys.version)"}),
    ]
    
    for i, (desc, worker_name, action, params) in enumerate(test_cases, 1):
        print(f"  [8.{i}] {desc}...")
        try:
            worker = supervisor.workers.get(worker_name)
            if worker:
                result = await worker.execute(action, **params)
                if result.get("success"):
                    print(f"    [OK] 成功")
                    results["passed"] += 1
                else:
                    print(f"    [FAIL] 失败: {result.get('error', '未知')[:50]}")
                    results["failed"] += 1
            else:
                print(f"    [WARN] Worker 未注册")
        except Exception as e:
            print(f"    [FAIL] 异常: {str(e)[:50]}")
            results["failed"] += 1
            
    # ==================== 结果汇总 ====================
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"[PASS] 通过: {results['passed']}")
    print(f"[FAIL] 失败: {results['failed']}")
    
    if results['errors']:
        print("\n错误详情：")
        for err in results['errors']:
            print(f"  - {err}")
            
    print("\n" + "=" * 60)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_all())
