"""Debug pywinauto backends"""
import sys
sys.path.insert(0, 'C:/Users/X1882/.qclaw/workspace/Woclaw/src')

print("Testing pywinauto backends...")

# Test win32 backend
print("\n[1] Testing 'win32' backend:")
try:
    from pywinauto import Application
    from pywinauto.findwindows import find_windows
    
    windows = find_windows(backend='win32')
    print(f"    Found {len(windows)} windows with win32 backend")
    
    # Try to get some titles
    count = 0
    for hwnd in windows[:10]:
        try:
            app = Application(backend='win32').from_hwnd(hwnd)
            title = app.window().window_text()
            if title:
                print(f"      {count+1}. {title[:50]}")
                count += 1
        except:
            pass
except Exception as e:
    print(f"    Error: {e}")

# Test uia backend
print("\n[2] Testing 'uia' backend:")
try:
    from pywinauto import Application
    from pywinauto.findwindows import find_windows
    
    windows = find_windows(backend='uia')
    print(f"    Found {len(windows)} windows with uia backend")
    
    count = 0
    for hwnd in windows[:10]:
        try:
            app = Application(backend='uia').from_hwnd(hwnd)
            title = app.window().window_text()
            if title:
                print(f"      {count+1}. {title[:50]}")
                count += 1
        except:
            pass
except Exception as e:
    print(f"    Error: {e}")

# Test starting and controlling notepad
print("\n[3] Testing Notepad control with win32:")
try:
    import subprocess
    subprocess.Popen(['notepad.exe'])
    
    import time
    time.sleep(0.5)
    
    # Try with win32
    app = Application(backend='win32').connect(title_re=".*Notepad.*")
    window = app.window()
    print(f"    Connected to: {window.window_text()}")
    
    # Type some text
    window['Edit'].type_keys("Hello from Woclaw!", with_spaces=True)
    print("    Typed text successfully")
    
    window.close()
    print("    Closed Notepad")
except Exception as e:
    print(f"    Error: {e}")

print("\nDone!")
