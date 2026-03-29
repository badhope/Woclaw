"""Woclaw GUI Worker Test - Fixed Version"""
import sys
import subprocess
import time
import asyncio
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

print('='*60)
print('GUI WORKER TEST - Window Operations (Fixed)')
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
    
    # Test 2: Find Notepad
    print('\n[2] Finding Notepad...')
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
        for w in result.get('windows', [])[:3]:
            print(f'      - {w.get("title","")[:40]}')
    else:
        print(f'    Error: {result.get("error")}')
    
    # Test 4: Start and control Notepad
    print('\n[4] Testing Notepad automation...')
    
    # Start notepad
    print('    Starting Notepad...')
    proc = subprocess.Popen(['notepad.exe'])
    await asyncio.sleep(1)
    
    # Find notepad
    result = await gui.execute('window_find', title='Notepad')
    if result.get('success'):
        windows = result.get('windows', [])
        if windows:
            hwnd = windows[0].get('handle')
            print(f'    Found Notepad, handle={hwnd}')
            
            # Activate
            result = await gui.execute('window_activate', handle=hwnd)
            print(f'    Activate: success={result.get("success")}')
            
            # Screenshot
            result = await gui.execute('screenshot', window_title='Notepad')
            print(f'    Screenshot: success={result.get("success")}')
            if result.get('path'):
                print(f'      Path: {result.get("path")[:60]}')
            
            # Close
            result = await gui.execute('window_close', handle=hwnd)
            print(f'    Close: success={result.get("success")}')
        else:
            print('    No Notepad window found')
    else:
        print(f'    Error: {result.get("error")}')
    
    # Cleanup
    try:
        proc.kill()
    except:
        pass
    
    print('\n' + '='*60)
    print('GUI WORKER TEST COMPLETED!')
    print('='*60)

asyncio.run(test_gui())
