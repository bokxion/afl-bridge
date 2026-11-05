# -*- coding: utf-8 -*-
r"""
open_userscript_install.py
=============================================================================
AFL (Argon-Flash Link) Userscript Cross-Desktop Foreground Launcher
-----------------------------------------------------------------------------
Solves:
1. Windows Desktop Sandbox Isolation (crosses from WinSta0\exebox-... to WinSta0\Default)
2. Foreground Focus Lock (breaks Windows LockSetForegroundWindow via VK_MENU + AttachThreadInput)
3. Direct Chrome Dispatch (prevents Edge or default browser protocol hijacking)
4. Exact .user.js URL Handshake for native Tampermonkey interception
=============================================================================
"""

import sys
import os
import time
import argparse
import ctypes
from ctypes import wintypes
import urllib.request
import urllib.error
import subprocess
import shutil

# Win32 API definitions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

SW_RESTORE = 9
SW_SHOW = 5
VK_MENU = 0x12
KEYEVENTF_KEYUP = 0x0002

DEFAULT_USERSCRIPT_URL = "http://127.0.0.1:8790/argon_commander.user.js"
DEFAULT_DESKTOP_NAME = "Default"
WINSTA_DEFAULT = "WinSta0\\Default"

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
        ('lpReserved2', ctypes.POINTER(wintypes.BYTE)),
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

def get_windows_unicode_argv():
    """Retrieve uncorrupted wide-character command line arguments on Windows."""
    if sys.platform != "win32":
        return sys.argv
    try:
        GetCommandLineW = ctypes.windll.kernel32.GetCommandLineW
        GetCommandLineW.restype = ctypes.c_wchar_p
        CommandLineToArgvW = ctypes.windll.shell32.CommandLineToArgvW
        CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)

        cmd = GetCommandLineW()
        argc = ctypes.c_int()
        argv_ptr = CommandLineToArgvW(cmd, ctypes.byref(argc))
        if argv_ptr:
            args = [argv_ptr[i] for i in range(argc.value)]
            ctypes.windll.kernel32.LocalFree(argv_ptr)
            for idx, a in enumerate(args):
                if a.endswith(".py") or a.endswith(".pyw"):
                    return args[idx:]
    except Exception:
        pass
    return sys.argv

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

    # Registry lookup
    try:
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                key = winreg.OpenKey(root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                val, _ = winreg.QueryValueEx(key, "")
                winreg.CloseKey(key)
                if val and os.path.isfile(val):
                    return val
            except OSError:
                pass
    except Exception:
        pass

    which_chrome = shutil.which("chrome")
    if which_chrome:
        return which_chrome

    return None

def ensure_bridge_server_running(url):
    """If url targets localhost:8790, verify relay server is alive, auto-start if needed."""
    if "127.0.0.1:8790" not in url and "localhost:8790" not in url:
        return True

    status_url = "http://127.0.0.1:8790/api/status"
    try:
        req = urllib.request.Request(status_url, headers={"User-Agent": "AFL-Installer/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                print("[AFL_INSTALLER] Relay server (port 8790) is active.")
                return True
    except Exception:
        print("[AFL_INSTALLER] Relay server (8790) not responding. Launching background server...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(base_dir, "start_bridge.bat")
    py_path = os.path.join(base_dir, "bridge_server.py")

    # 1. Primary: Launch via Windows WMI (SWbemLocator / Win32_Process)
    # This completely decouples the process under WmiPrvSE, immune to caller/subagent terminal or Job Object termination.
    launched = False
    if os.path.isfile(py_path):
        try:
            import win32com.client
            locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            services = locator.ConnectServer(".", r"root\cimv2")
            process = services.Get("Win32_Process")
            in_params = process.Methods_("Create").InParameters.SpawnInstance_()
            in_params.CommandLine = f'"{sys.executable}" "{py_path}"'
            in_params.CurrentDirectory = base_dir
            out = process.ExecMethod_("Create", in_params)
            if out.ReturnValue == 0:
                print(f"[AFL_INSTALLER] Successfully launched persistent relay server via WMI (PID={out.ProcessId}).")
                launched = True
                time.sleep(1.5)
        except Exception as e:
            print(f"[AFL_INSTALLER] Note: WMI launch attempt bypassed: {e}")

    # 2. Secondary fallback: direct detached Popen with cwd and DEVNULL handles
    if not launched and os.path.isfile(py_path):
        detached_flags = 0x08000000 | 0x00000200 | 0x00000008
        try:
            subprocess.Popen(
                [sys.executable, py_path],
                cwd=base_dir,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=detached_flags
            )
            time.sleep(1.5)
            launched = True
        except Exception as e:
            print(f"[AFL_INSTALLER] Warning: Failed direct python launch: {e}")

    if not launched and os.path.isfile(bat_path):
        detached_flags = 0x08000000 | 0x00000200 | 0x00000008
        try:
            subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                cwd=base_dir,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=detached_flags
            )
            time.sleep(1.5)
        except Exception as e:
            print(f"[AFL_INSTALLER] Warning: Failed to run {bat_path}: {e}")

    # Verification loop (up to 4 seconds)
    for _ in range(4):
        try:
            req = urllib.request.Request(status_url, headers={"User-Agent": "AFL-Installer/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    print("[AFL_INSTALLER] Relay server successfully verified and responding on port 8790.")
                    return True
        except Exception:
            time.sleep(0.8)
    print("[AFL_INSTALLER] Warning: Could not verify relay server on 8790.")
    return False

def open_interactive_desktop():
    """Attempt to open and switch thread to the interactive Default desktop."""
    hDesk = user32.OpenDesktopW(DEFAULT_DESKTOP_NAME, 0, False, 0x10000000)
    if not hDesk:
        hDesk = user32.OpenDesktopW(DEFAULT_DESKTOP_NAME, 0, False, 0x0001 | 0x0040 | 0x0002)
    if hDesk:
        user32.SetThreadDesktop(hDesk)
    return hDesk

def force_window_foreground(hwnd):
    """Break Windows foreground lock and bring target window to front."""
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    # 1. Break Windows LockSetForegroundWindow lock by tapping Alt (VK_MENU)
    user32.keybd_event(VK_MENU, 0, 0, 0)
    user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

    # 2. Attach thread inputs to bypass foreground restrictions
    curr_tid = kernel32.GetCurrentThreadId()
    fg_hwnd = user32.GetForegroundWindow()
    fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
    wnd_tid = user32.GetWindowThreadProcessId(hwnd, None)

    if fg_tid and fg_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, fg_tid, True)
    if wnd_tid and wnd_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, wnd_tid, True)

    # 3. Restore and activate window
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    user32.SwitchToThisWindow(hwnd, True)

    # 4. Detach thread inputs
    if fg_tid and fg_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, fg_tid, False)
    if wnd_tid and wnd_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, wnd_tid, False)

    return True

def find_chrome_windows(hDesk=None):
    """Find visible Chrome windows on desktop."""
    chrome_hwnds = []

    def enum_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            low = title.lower()
            if "chrome" in low or "google ai studio" in low or "userscript" in low or "tampermonkey" in low:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                chrome_hwnds.append((hwnd, pid.value, title))
        return 1

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HWND, wintypes.LPARAM)
    cb = WNDENUMPROC(enum_proc)

    if hDesk:
        user32.EnumDesktopWindows(hDesk, cb, 0)
    else:
        user32.EnumWindows(cb, 0)

    return chrome_hwnds

def launch_chrome_on_default_desktop(chrome_exe, target_url):
    """Launch Chrome directed strictly at WinSta0\\Default."""
    cmd_line = f'"{chrome_exe}" "{target_url}"'
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    si.lpDesktop = WINSTA_DEFAULT
    pi = PROCESS_INFORMATION()

    print(f"[AFL_INSTALLER] Launching Chrome on {WINSTA_DEFAULT}:")
    print(f"                 URL: {target_url}")

    res = kernel32.CreateProcessW(
        None,
        cmd_line,
        None,
        None,
        False,
        0,
        None,
        None,
        ctypes.byref(si),
        ctypes.byref(pi)
    )

    if res:
        print(f"[AFL_INSTALLER] Successfully initiated Chrome process (PID={pi.dwProcessId}).")
        kernel32.CloseHandle(pi.hProcess)
        kernel32.CloseHandle(pi.hThread)
        return True
    else:
        err = kernel32.GetLastError()
        print(f"[AFL_INSTALLER] Warning: CreateProcessW on {WINSTA_DEFAULT} failed with code {err}.")
        # Fallback to subprocess
        try:
            subprocess.Popen([chrome_exe, target_url])
            return True
        except Exception as e:
            print(f"[AFL_INSTALLER] Error: Fallback launch failed: {e}")
            return False

def open_userscript_install(target_url=DEFAULT_USERSCRIPT_URL):
    """Main execution routine to open userscript installation page in Chrome."""
    print("=" * 70)
    print("  AFL Userscript Cross-Desktop Foreground Launcher")
    print("=" * 70)

    # 0. Local file path resolution: map local .user.js files to local HTTP relay gateway
    if os.path.isfile(target_url) and target_url.endswith(".user.js"):
        script_name = os.path.basename(target_url)
        print(f"[AFL_INSTALLER] Local userscript file detected: {target_url}")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dest_copy = os.path.join(base_dir, script_name)
        if os.path.abspath(target_url) != os.path.abspath(dest_copy):
            try:
                shutil.copy2(target_url, dest_copy)
                print(f"[AFL_INSTALLER] Staged userscript copy to bridge server directory: {dest_copy}")
            except Exception as e:
                print(f"[AFL_INSTALLER] Note: Copy to {dest_copy} skipped: {e}")
        target_url = f"http://127.0.0.1:8790/{script_name}"
        print(f"[AFL_INSTALLER] Automatically routed via HTTP relay gateway: {target_url}")

    # 1. URL verification
    if not target_url.endswith(".user.js") and not "/userscript" in target_url:
        print(f"[AFL_INSTALLER] Note: Target URL '{target_url}' may not trigger Tampermonkey auto-install.")
        print("[AFL_INSTALLER] Tip: Tampermonkey typically requires URLs ending with '.user.js'.")

    # 2. Check local relay gateway
    ensure_bridge_server_running(target_url)

    # 3. Locate Chrome executable
    chrome_exe = find_chrome_executable()
    if not chrome_exe:
        print("[AFL_INSTALLER] Error: Could not locate Google Chrome executable.")
        return False
    print(f"[AFL_INSTALLER] Found Chrome at: {chrome_exe}")

    # 4. Open Default desktop handle
    hDesk = open_interactive_desktop()
    if hDesk:
        print(f"[AFL_INSTALLER] Switched thread to interactive desktop '{DEFAULT_DESKTOP_NAME}'.")
    else:
        print(f"[AFL_INSTALLER] Warning: Could not open '{DEFAULT_DESKTOP_NAME}' desktop directly.")

    # 5. Check existing Chrome windows before launch
    existing_windows = find_chrome_windows(hDesk)
    if existing_windows:
        print(f"[AFL_INSTALLER] Detected {len(existing_windows)} active Chrome window(s).")
        # Pre-focus to ensure Chrome is receptive
        for hwnd, pid, title in existing_windows[:1]:
            force_window_foreground(hwnd)

    # 6. Launch Chrome with userscript URL targeting WinSta0\Default
    launched = launch_chrome_on_default_desktop(chrome_exe, target_url)
    if not launched:
        if hDesk:
            user32.CloseDesktop(hDesk)
        return False

    # 7. Wait briefly and bring Chrome window to topmost foreground
    time.sleep(1.2)
    after_windows = find_chrome_windows(hDesk)
    activated = False

    # Prioritize windows that show "Userscript", "Tampermonkey", or "Chrome"
    priority_hwnds = []
    other_hwnds = []
    for hwnd, pid, title in after_windows:
        low = title.lower()
        if "userscript" in low or "tampermonkey" in low:
            priority_hwnds.append((hwnd, pid, title))
        else:
            other_hwnds.append((hwnd, pid, title))

    targets = priority_hwnds if priority_hwnds else other_hwnds
    for hwnd, pid, title in targets[:2]:
        force_window_foreground(hwnd)
        activated = True
        print(f"[AFL_INSTALLER] Successfully set foreground focus to HWND {hwnd} ('{title}')")

    if hDesk:
        user32.CloseDesktop(hDesk)

    print("-" * 70)
    print("  [操作提示 / USER ACTION REQUIRED]")
    print("  Chrome 已在前台激活并打开油猴脚本安装页面。")
    print("  请在页面中央点击绿色【Install / Update】（安装/更新）按键完成部署！")
    print("=" * 70)
    return True

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    raw_args = get_windows_unicode_argv()[1:]

    parser = argparse.ArgumentParser(description="AFL Userscript Cross-Desktop Foreground Launcher")
    parser.add_argument("url", nargs="?", default=DEFAULT_USERSCRIPT_URL, help="Target .user.js URL to install/update")
    parser.add_argument("--url", "-u", dest="flag_url", help="Target .user.js URL (flag alternative)")

    args = parser.parse_args(raw_args)
    target = args.flag_url if args.flag_url else args.url

    success = open_userscript_install(target)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
