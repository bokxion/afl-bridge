# -*- coding: utf-8 -*-
"""
AFL Background Window Manager v6.0.0
Manages dedicated AI Studio Chrome windows in an off-screen restored state (-32000, -32000),
completely replacing SW_MINIMIZE while preventing Chromium kFrozen lifecycle suspension.

Redline Compliance:
- Strictly guards against moving multi-tab windows (e.g., windows containing user's active browsing like '远控').
- Only manipulates the dedicated single session window for the target project (e.g., '统帅').
- If no dedicated window exists, spawns a dedicated isolated window and places it off-screen without touching other tabs.
"""

import sys
import os
import json
import time
import argparse
import ctypes
from ctypes import wintypes
import urllib.request

DEFAULT_DESKTOP_NAME = "Default"
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_NOZORDER = 0x0004
SW_SHOWNOACTIVATE = 4
SW_RESTORE = 9

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def open_interactive_desktop():
    """Attempt to open and switch thread to the interactive Default desktop."""
    hDesk = user32.OpenDesktopW(DEFAULT_DESKTOP_NAME, 0, False, 0x10000000)
    if not hDesk:
        hDesk = user32.OpenDesktopW(DEFAULT_DESKTOP_NAME, 0, False, 0x0001 | 0x0040 | 0x0002)
    if hDesk:
        user32.SetThreadDesktop(hDesk)
        return hDesk
    return None

def find_chrome_executable():
    """Locate Google Chrome executable path on Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    try:
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                key = winreg.OpenKey(root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                val, _ = winreg.QueryValueEx(key, "")
                if val and os.path.isfile(val):
                    return val
            except Exception:
                pass
    except Exception:
        pass
    return None

def get_target_info(target_title=None):
    """Retrieve target_title and target_url from .aistudio_config.json or bridge status."""
    title = target_title
    url = ""
    # 1. From local .aistudio_config.json
    cfg_path = os.path.join(os.getcwd(), ".aistudio_config.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                if not title and d.get("target_title"):
                    title = d["target_title"].strip()
                if d.get("target_url"):
                    url = d["target_url"].strip()
        except Exception:
            pass

    # 2. Query bridge status for URL
    try:
        req = urllib.request.Request("http://127.0.0.1:8790/api/status", headers={"User-Agent": "AFL-BgWin/6.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for tab in data.get("active_tabs", []):
                t_title = tab.get("title", "")
                if not title or title.lower() in t_title.lower() or t_title.lower() in title.lower():
                    if not title:
                        title = t_title
                    url = tab.get("url", url)
                    break
    except Exception:
        pass

    if not title:
        title = "统帅"
    return title, url

def enum_chrome_windows():
    """Enumerate all top-level Chrome windows on the interactive desktop."""
    windows = []

    def callback(hwnd, _):
        c_buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, c_buff, 256)
        cls = c_buff.value
        if cls == "Chrome_WidgetWin_1":
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            vis = user32.IsWindowVisible(hwnd)
            iconic = user32.IsIconic(hwnd)
            is_offscreen = (rect.left <= -30000 or rect.top <= -30000)
            windows.append({
                "hwnd": hwnd,
                "pid": pid.value,
                "title": title,
                "visible": vis,
                "iconic": iconic,
                "rect": (rect.left, rect.top, rect.right, rect.bottom),
                "is_offscreen": is_offscreen
            })
        return 1

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HWND, wintypes.LPARAM)
    cb = WNDENUMPROC(callback)
    user32.EnumWindows(cb, 0)
    return windows

def move_window_offscreen(hwnd):
    """Move a window off-screen to (-32000, -32000) without activating or minimizing."""
    user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
    user32.SetWindowPos(hwnd, 0, -32000, -32000, 1280, 800, SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_NOZORDER)
    time.sleep(0.1)
    iconic = user32.IsIconic(hwnd)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return (rect.left <= -30000) and (iconic == 0)

def restore_window_onscreen(hwnd, x=100, y=100, w=1280, h=800):
    """Restore a window back to visible desktop coordinates."""
    user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
    user32.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_NOZORDER)
    time.sleep(0.1)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left > -30000

WINSTA_DEFAULT = r"WinSta0\Default"

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', ctypes.c_void_p),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('hProcess', wintypes.HANDLE),
        ('hThread', wintypes.HANDLE),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD),
    ]

def launch_dedicated_window(chrome_exe, target_url):
    """Launch Chrome in a dedicated new-window directed strictly at WinSta0\\Default."""
    anti_occlusion_flags = (
        "--disable-backgrounding-occluded-windows "
        "--disable-renderer-backgrounding "
        "--disable-background-timer-throttling "
        "--disable-features=CalculateNativeWindowOcclusion,CalculateNativeWinOcclusion,IntensiveWakeUpThrottling "
        "--remote-debugging-port=42068 "
        '--profile-directory="Default"'
    )
    cmd_line = f'"{chrome_exe}" {anti_occlusion_flags} --new-window "{target_url}"'
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    si.lpDesktop = WINSTA_DEFAULT
    pi = PROCESS_INFORMATION()

    print(f"[AFL_BGWIN] Spawning dedicated Chrome window on {WINSTA_DEFAULT}:")
    print(f"            Command: {cmd_line}")

    res = kernel32.CreateProcessW(
        None, cmd_line, None, None, False, 0, None, None,
        ctypes.byref(si), ctypes.byref(pi)
    )
    if res:
        print(f"[AFL_BGWIN] Successfully initiated Chrome process PID={pi.dwProcessId}")
        kernel32.CloseHandle(pi.hProcess)
        kernel32.CloseHandle(pi.hThread)
        return True
    else:
        err = kernel32.GetLastError()
        print(f"[AFL_BGWIN] Warning: CreateProcessW failed with code {err}")
        return False

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="AFL Background Window Manager v6.0.0")
    parser.add_argument("--offscreen", action="store_true", help="Move target session window off-screen (-32000, -32000)")
    parser.add_argument("--restore", action="store_true", help="Restore target session window back to visible desktop (100, 100)")
    parser.add_argument("--status", action="store_true", help="Show all Chrome windows and off-screen status")
    parser.add_argument("--target-title", "-tt", help="Target session title (default: from .aistudio_config.json)")
    parser.add_argument("--force-hwnd", type=int, help="Force move a specific HWND (use with caution)")
    args = parser.parse_args()

    hDesk = open_interactive_desktop()
    target_title, target_url = get_target_info(args.target_title)
    print(f"[AFL_BGWIN] Active Target Session: [{target_title}] | URL: [{target_url or 'Auto'}]")

    all_windows = enum_chrome_windows()

    if args.status or (not args.offscreen and not args.restore):
        print(f"\n[AFL_BGWIN] Discovered {len(all_windows)} Chrome_WidgetWin_1 Window(s):")
        for w in all_windows:
            state = "OFF-SCREEN (Deep Water)" if w["is_offscreen"] else "VISIBLE (Desktop)"
            iconic_str = "MINIMIZED" if w["iconic"] else "RESTORED"
            is_target = target_title.lower() in w["title"].lower()
            tag = " << [TARGET MATCH]" if is_target else ""
            print(f"  -> HWND: {w['hwnd']:<10} PID: {w['pid']:<6} State: {state:<22} ({iconic_str}) Rect: {w['rect']} Title: '{w['title']}'{tag}")
        if hDesk:
            user32.CloseDesktop(hDesk)
        return

    if args.restore:
        # Restore target window
        restored_count = 0
        for w in all_windows:
            if args.force_hwnd and w["hwnd"] == args.force_hwnd:
                ok = restore_window_onscreen(w["hwnd"])
                print(f"[AFL_BGWIN] Restored force HWND {w['hwnd']}: ok={ok}")
                restored_count += 1
            elif target_title.lower() in w["title"].lower():
                ok = restore_window_onscreen(w["hwnd"])
                print(f"[AFL_BGWIN] Restored [{target_title}] HWND {w['hwnd']} ('{w['title']}'): ok={ok}")
                restored_count += 1
            elif w["is_offscreen"]:
                # If off-screen, ask or restore
                print(f"[AFL_BGWIN] Found off-screen Chrome window HWND {w['hwnd']} ('{w['title']}'). Restoring...")
                ok = restore_window_onscreen(w["hwnd"])
                restored_count += 1
        if restored_count == 0:
            print("[AFL_BGWIN] No matching off-screen window found to restore.")
        if hDesk:
            user32.CloseDesktop(hDesk)
        return

    if args.offscreen:
        # Off-screen implementation with Redline Protection
        if args.force_hwnd:
            ok = move_window_offscreen(args.force_hwnd)
            print(f"[AFL_BGWIN] Moved force HWND {args.force_hwnd} off-screen: ok={ok}")
            if hDesk: user32.CloseDesktop(hDesk)
            return

        # 1. Search for dedicated target window
        target_windows = [w for w in all_windows if target_title.lower() in w["title"].lower()]
        
        # Redline check: ensure window does not contain other tabs (like '远控' etc.)
        valid_dedicated_target = None
        for w in target_windows:
            title_lower = w["title"].lower()
            # If the title strictly starts with target_title, it's the active tab of that window!
            if target_title.lower() in title_lower:
                valid_dedicated_target = w
                break

        if valid_dedicated_target:
            hwnd = valid_dedicated_target["hwnd"]
            print(f"[AFL_BGWIN] Found dedicated window HWND {hwnd} ('{valid_dedicated_target['title']}').")
            ok = move_window_offscreen(hwnd)
            print(f"[AFL_BGWIN] Successfully moved [{target_title}] HWND {hwnd} to Off-Screen Deep Water: ok={ok}")
        else:
            # Multi-tab conflict protection!
            print(f"[AFL_BGWIN] ⚠️ Redline Notice: No dedicated window found for [{target_title}].")
            print("  -> Existing Chrome window is likely a multi-tab workspace (e.g., active with '远控').")
            print("  -> Refusing to drag the entire multi-tab window to protect the user's active browsing session!")

            if target_url:
                chrome_exe = find_chrome_executable()
                if chrome_exe:
                    print(f"[AFL_BGWIN] Spawning a dedicated isolated window for [{target_title}]...")
                    launch_dedicated_window(chrome_exe, target_url)
                    print("[AFL_BGWIN] Waiting 4 seconds for dedicated window to appear...")
                    time.sleep(4.0)
                    new_windows = enum_chrome_windows()
                    for nw in new_windows:
                        if target_title.lower() in nw["title"].lower() and not nw["is_offscreen"]:
                            ok = move_window_offscreen(nw["hwnd"])
                            print(f"[AFL_BGWIN] Successfully placed new dedicated HWND {nw['hwnd']} off-screen: ok={ok}")
                            break
            else:
                print(f"[AFL_BGWIN] Please manually detach [{target_title}] tab to a new window, or provide URL in .aistudio_config.json.")

    if hDesk:
        user32.CloseDesktop(hDesk)

if __name__ == "__main__":
    main()
