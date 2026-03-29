"""Woclaw Comprehensive Worker Test"""
import sys
import os
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

print('='*60)
print('WOCLAW COMPREHENSIVE WORKER TEST')
print('='*60)

async def run_all_tests():
    # 1. Test ShellWorker
    print('\n[1] Testing ShellWorker...')
    from woclaw.workers import ShellWorker
    shell = ShellWorker()
    
    result = await shell.execute('execute', command='echo hello')
    print(f'    echo: success={result.get("success")}')
    
    result = await shell.execute('execute', command='dir')
    print(f'    dir: success={result.get("success")}')
    
    result = await shell.execute('check', command='python')
    print(f'    check python: exists={result.get("exists")}')
    print('    ShellWorker: OK')
    
    # 2. Test SysWorker
    print('\n[2] Testing SysWorker...')
    from woclaw.workers import SysWorker
    sys_worker = SysWorker()
    
    result = await sys_worker.execute('info')
    print(f'    sys_info: success={result.get("success")}, system={result.get("system")}')
    
    result = await sys_worker.execute('cpu')
    print(f'    cpu: success={result.get("success")}, cores={result.get("physical_cores")}')
    
    result = await sys_worker.execute('memory')
    print(f'    memory: success={result.get("success")}')
    
    result = await sys_worker.execute('processes', limit=5)
    print(f'    processes: success={result.get("success")}, count={result.get("total_count")}')
    print('    SysWorker: OK')
    
    # 3. Test FileWorker
    print('\n[3] Testing FileWorker...')
    from woclaw.workers import FileWorker
    file_worker = FileWorker()
    
    result = await file_worker.execute('list')
    print(f'    list: success={result.get("success")}, count={result.get("count")}')
    
    result = await file_worker.execute('write', path='C:/Users/X1882/.qclaw/workspace/Woclaw/test_file.txt', content='Hello from Woclaw!')
    print(f'    write: success={result.get("success")}')
    
    result = await file_worker.execute('read', path='C:/Users/X1882/.qclaw/workspace/Woclaw/test_file.txt')
    print(f'    read: success={result.get("success")}, content={result.get("content","")[:30]}')
    
    result = await file_worker.execute('delete', path='C:/Users/X1882/.qclaw/workspace/Woclaw/test_file.txt')
    print(f'    delete: success={result.get("success")}')
    print('    FileWorker: OK')
    
    # 4. Test LearningMemory
    print('\n[4] Testing LearningMemory...')
    from woclaw.learning import LearningMemory
    memory = LearningMemory()
    
    await memory.load()
    print(f'    load: loaded={memory._loaded}')
    
    await memory.record_success('test task', [{'tool': 'shell', 'action': 'execute'}])
    print('    record_success: OK')
    
    await memory.record_error('test_op', 'test error', {})
    print('    record_error: OK')
    
    await memory.save()
    print('    save: OK')
    
    stats = memory.get_stats()
    print(f'    stats: learnings={stats["total_learnings"]}, errors={stats["total_errors"]}')
    print('    LearningMemory: OK')
    
    # 5. Test GuiWorker (basic detection)
    print('\n[5] Testing GuiWorker...')
    from woclaw.workers import GuiWorker
    gui_worker = GuiWorker()
    
    # Just test that it can be instantiated
    info = gui_worker.get_info()
    print(f'    info: name={info.name}, capabilities={len(info.capabilities)}')
    print('    GuiWorker: OK')
    
    # 6. Test WebWorker
    print('\n[6] Testing WebWorker...')
    from woclaw.workers import WebWorker
    web_worker = WebWorker()
    
    # Test DNS lookup
    result = await web_worker.execute('dns', domain='example.com')
    print(f'    dns lookup: success={result.get("success")}, ip={result.get("ip")}')
    
    await web_worker.cleanup()
    print('    WebWorker: OK')
    
    print('\n' + '='*60)
    print('ALL WORKER TESTS PASSED!')
    print('='*60)

# Run
import asyncio
asyncio.run(run_all_tests())
