# Woclaw Module Test Script
import sys
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

print('=' * 60)
print('WOCLAW MODULE TEST')
print('=' * 60)

# Test basic dependencies
results = []
for mod in ['aiohttp', 'psutil', 'click', 'rich', 'PIL', 'pywinauto']:
    try:
        __import__(mod)
        results.append(f'[OK] {mod}')
    except ImportError as e:
        results.append(f'[FAIL] {mod}: {e}')

print()
for r in results:
    print(r)

print()
print('=' * 60)
print('Testing Woclaw core imports...')
print('=' * 60)

try:
    import woclaw
    print(f'[OK] woclaw {woclaw.__version__}')
    print(f'     Brand: {woclaw.BRAND["name"]}')
    print(f'     Slogan: {woclaw.BRAND["slogan"]}')
except Exception as e:
    print(f'[FAIL] woclaw: {e}')

print()
try:
    from woclaw.supervisor import Supervisor, Planner, Executor
    print('[OK] Supervisor, Planner, Executor')
except Exception as e:
    print(f'[FAIL] Supervisor: {e}')

print()
try:
    from woclaw.workers import FileWorker, GuiWorker, ShellWorker, WebWorker, SysWorker
    print('[OK] FileWorker, GuiWorker, ShellWorker, WebWorker, SysWorker')
except Exception as e:
    print(f'[FAIL] Workers: {e}')

print()
try:
    from woclaw.llm import LLMRegistry
    providers = LLMRegistry.list_providers()
    print(f'[OK] LLMRegistry - {len(providers)} providers: {providers}')
except Exception as e:
    print(f'[FAIL] LLMRegistry: {e}')

print()
try:
    from woclaw.learning import LearningMemory
    print('[OK] LearningMemory')
except Exception as e:
    print(f'[FAIL] LearningMemory: {e}')

print()
print('=' * 60)
print('ALL CORE IMPORTS SUCCESSFUL!')
print('=' * 60)
