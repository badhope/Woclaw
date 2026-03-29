"""Final GUI Worker Test"""
import sys
import asyncio
import subprocess
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

async def test():
    from woclaw.workers import GuiWorker
    
    gui = GuiWorker()
    
    # Start notepad
    print('Starting Notepad...')
    proc = subprocess.Popen(['notepad.exe'])
    await asyncio.sleep(1)
    
    # List windows
    result = await gui.execute('window_list')
    print('Windows found:', result.get('count'))
    for w in result.get('windows', [])[:5]:
        print('  -', w.get('title', '')[:40])
    
    # Screenshot
    result = await gui.execute('screenshot', window_title='Notepad')
    print('Screenshot success:', result.get('success'))
    if result.get('path'):
        print('  Path:', result.get('path')[:60])
    
    # Close
    result = await gui.execute('window_close', title='Notepad')
    print('Close success:', result.get('success'))
    
    try:
        proc.kill()
    except:
        pass
    
    print('\nTest completed!')

asyncio.run(test())
