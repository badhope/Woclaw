"""Woclaw GUI Worker Test - Real Window Operations"""
import sys
import asyncio
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

print('='*60)
print('GUI WORKER TEST - Window Operations')
print('='*60)

async def test_gui():
    from woclaw.workers import GuiWorker
    gui = GuiWorker()
    
    # Test 1: List all windows
    print('\n[1] Listing all visible windows...')
    result = await gui.execute('window_list')
    if result.get('success'):
        windows = result.get('windows', [])
        print(f'    Found {len(windows)} windows')
        for w in windows[:5]:
            title = w.get('title', '')[:40]
            print(f'      - {title}')
    else:
        print(f'    Error: {result.get("error")}')
    
    # Test 2: Find specific window
    print('\n[2] Finding window by title...')
    result = await gui.execute('window_find', title='Notepad')
    if result.get('success'):
        windows = result.get('windows', [])
        print(f'    Found {len(windows)} matching windows')
    else:
        print(f'    Error: {result.get("error")}')
    
    # Test 3: Desktop info
    print('\n[3] Getting desktop info...')
    result = await gui.execute('get_desktop')
    if result.get('success'):
        print(f'    Windows on desktop: {result.get("count")}')
    else:
        print(f'    Error: {result.get("error")}')
    
    # Test 4: Start and control Notepad
    print('\n[4] Testing Notepad automation...')
    print('    Starting Notepad...')
    
    # Start notepad
    import subprocess
    proc = subprocess.Popen(['notepad.exe'])
    await asyncio.sleep(0.5)
    
    # Find notepad window
    result = await gui.execute('window_find', title='Notepad')
    if result.get('success') and result.get('windows'):
        hwnd = result.get('windows')[0].get('handle')
        print(f'    Found Notepad, handle={hwnd}')
        
        # Activate
        result = await gui.execute('window_activate', handle=hwnd)
        print(f'    Activate: success={result.get("success")}')
        
        # Screenshot
        result = await gui.execute('screenshot', window_title='Notepad')
        print(f'    Screenshot: success={result.get("success")}, path={result.get("path","")[:50]}')
        
        # Close
        result = await gui.execute('window_close', handle=hwnd)
        print(f'    Close: success={result.get("success")}')
    else:
        print('    Notepad not found (may already be closed)')
    
    # Cleanup
    try:
        proc.kill()
    except:
        pass
    
    print('\n' + '='*60)
    print('GUI WORKER TEST COMPLETED!')
    print('='*60)

asyncio.run(test_gui())
