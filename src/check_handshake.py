# -*- coding: utf-8 -*-
"""
AFL Pre-Flight Handshake & Precision Session Verification
Standardized diagnostic tool for AI Studio (Argon) <-> Antigravity (Flash) Bridge.
Checks:
1. Local Relay Server (8790)
2. Antigravity CDP Port & Active Window
3. Tampermonkey Connection & Matching Project Target Session
"""

import sys
import os
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.error

BRIDGE_STATUS_URL = "http://127.0.0.1:8790/api/status"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import CDP discovery
try:
    from cdp_sender import find_cdp_endpoint
except ImportError:
    find_cdp_endpoint = lambda: (None, None)


def get_windows_unicode_argv():
    """Retrieve uncorrupted wide-character command line arguments on Windows."""
    if sys.platform != "win32":
        return sys.argv
    try:
        import ctypes
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


def find_project_config(start_dir=None):
    """Search upwards from start_dir for .aistudio_config.json."""
    if not start_dir:
        start_dir = os.getcwd()
    curr = os.path.abspath(start_dir)
    while True:
        cfg_path = os.path.join(curr, ".aistudio_config.json")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data, cfg_path
            except Exception as e:
                print(f"[AFL_HANDSHAKE] Warning: Failed to parse {cfg_path}: {e}")
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return None, None


def save_project_config(target_title, target_dir=None):
    """Save target_title to .aistudio_config.json in target_dir (default: cwd)."""
    if not target_dir:
        target_dir = os.getcwd()
    cfg_path = os.path.join(os.path.abspath(target_dir), ".aistudio_config.json")
    data = {
        "target_title": target_title.strip(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[AFL_HANDSHAKE] Successfully bound target session [{target_title.strip()}] -> {cfg_path}")
    return cfg_path


def check_server():
    try:
        req = urllib.request.Request(BRIDGE_STATUS_URL, headers={"User-Agent": "AFL-Handshake/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data
    except Exception:
        # Try auto-launching if not running
        bat_path = os.path.join(BASE_DIR, "start_bridge.bat")
        if os.path.exists(bat_path):
            try:
                subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=0x08000000) # CREATE_NO_WINDOW
                time.sleep(2.0)
                req = urllib.request.Request(BRIDGE_STATUS_URL, headers={"User-Agent": "AFL-Handshake/1.0"})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return True, data
            except Exception:
                pass
        return False, None


def check_cdp():
    port, ws_url = find_cdp_endpoint()
    return bool(ws_url), port, ws_url



def check_chrome_anti_occlusion():
    """Inspect running Chrome instances for anti-occlusion flags and CDP 42068."""
    port_42068_ok = False
    try:
        req = urllib.request.Request("http://127.0.0.1:42068/json/version", headers={"User-Agent": "AFL-Handshake/1.0"})
        with urllib.request.urlopen(req, timeout=0.6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "Browser" in data:
                port_42068_ok = True
    except Exception:
        pass

    flags_found = []
    has_occlusion_disabled = False
    try:
        # Use WMI / PowerShell to check chrome command lines
        res = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name = 'chrome.exe'\" | Where-Object { $_.CommandLine -notmatch '--type=' } | Select-Object -ExpandProperty CommandLine"],
            stderr=subprocess.DEVNULL
        ).decode("gbk", errors="ignore")
        for line in res.splitlines():
            line_str = line.strip()
            if not line_str: continue
            if "--disable-backgrounding-occluded-windows" in line_str:
                flags_found.append("disable-backgrounding-occluded-windows")
            if "--disable-renderer-backgrounding" in line_str:
                flags_found.append("disable-renderer-backgrounding")
            if "--disable-background-timer-throttling" in line_str:
                flags_found.append("disable-background-timer-throttling")
            if "CalculateNativeWin" in line_str:
                flags_found.append("CalculateNativeWindowOcclusion")
            if flags_found:
                has_occlusion_disabled = True
                break
    except Exception:
        pass

    return port_42068_ok, has_occlusion_disabled, list(set(flags_found))


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    raw_args = get_windows_unicode_argv()[1:]

    parser = argparse.ArgumentParser(description="AFL Multi-Project Handshake & Session Verification")
    parser.add_argument("--target-title", "-tt", help="Target AI Studio conversation/prompt title to verify")
    parser.add_argument("--bind-title", "-b", help="Bind target AI Studio conversation title to current workspace .aistudio_config.json")
    args = parser.parse_args(raw_args)

    if args.bind_title:
        save_project_config(args.bind_title)

    # Determine target title
    target_title = None
    config_file_found = None
    if args.target_title and args.target_title.strip():
        target_title = args.target_title.strip()
    else:
        cfg, cfg_path = find_project_config()
        if cfg and cfg.get("target_title"):
            target_title = cfg.get("target_title").strip()
            config_file_found = cfg_path

    print("=======================================================")
    print("  Project Argon-Flash Link (AFL) 协同链路就绪巡检")
    print("=======================================================\n")

    if target_title:
        origin = f"({config_file_found})" if config_file_found else "(命令行参数)"
        print(f"【目标绑定会话】: [{target_title}] {origin}\n")
    else:
        print("【目标绑定会话】: [未指定] (当前项目尚未绑定专属会话标题)\n")

    # 1. Check Server
    server_ok, server_data = check_server()
    if server_ok:
        print("[OK] 1. 本地网关 (端口 8790)：正常运行 (ACTIVE)")
    else:
        print("[FAIL] 1. 本地网关 (端口 8790)：未启动或无响应")
        print("    -> 解决方式：运行 start_bridge.bat 或 python src/bridge_server.py")

    # 2. Check CDP
    cdp_ok, cdp_port, ws_url = check_cdp()
    if cdp_ok:
        print(f"[OK] 2. Antigravity CDP 调试信道：已就绪 (端口: {cdp_port})")
    else:
        print("[FAIL] 2. Antigravity CDP 调试信道：未侦测到监听端口")
        print("    -> 解决方式：请确认 Antigravity 桌面端处于运行状态")

    # 4. Check Chrome Anti-Occlusion & CDP 42068
    cdp_42068_ok, occlusion_ok, flags_list = check_chrome_anti_occlusion()
    if occlusion_ok:
        print(f"[OK] 4. Chrome 抗遮蔽休眠：已成功激活 ({len(flags_list)}项核心参数生效中)")
    else:
        print("[!] 4. Chrome 抗遮蔽休眠：未检测到全量抗遮蔽启动参数")
        print("    -> 建议：运行 launch_afl_chrome.bat 启动 Chrome 以获得 100% 全速防休眠保障")

    if cdp_42068_ok:
        print(f"[OK] 5. Chrome CDP 调试信道 (42068)：已就绪")
    else:
        print("[*] 5. Chrome CDP 调试信道 (42068)：未激活 (当前主要依赖油猴直连，不影响 AFL 正常闭环)")


    # 3. Check Tampermonkey & Session Matching
    tm_ok = False
    matching_tab = None
    active_tabs = []

    if server_ok and server_data:
        active_tabs = server_data.get("active_tabs", [])
        if not active_tabs and server_data.get("commander_tab"):
            active_tabs = [server_data.get("commander_tab")]

    if target_title:
        # Precision matching mode
        t_target = target_title.lower()
        for tab in active_tabs:
            t_tab = (tab.get("title") or "").strip().lower()
            if t_target in t_tab or t_tab in t_target:
                matching_tab = tab
                break

        if matching_tab:
            tm_ok = True
            tab_ver = matching_tab.get('version') or '未知 (尚未刷新为 v5.9.2)'
            tab_phase = matching_tab.get('phase') or '未知'
            print(f"[OK] 3. AI Studio 油猴脚本：握手在线 (版本: {tab_ver}, 阶段: {tab_phase})")
            print(f"    -> 成功锁定专属统帅会话：[{matching_tab.get('title')}]")
        else:
            print(f"[FAIL] 3. AI Studio 油猴脚本：未发现与目标标题 [{target_title}] 匹配的活跃标签页！")
            if active_tabs:
                tab_names = ", ".join([f"[{t.get('title')}]" for t in active_tabs])
                print(f"    -> 当前在线标签页列表: {tab_names}")
                print(f"    -> 解决方式：请在浏览器中打开标题为 [{target_title}] 的 AI Studio 会话，或使用 --bind-title 重新绑定。")
            else:
                print("    -> 当前暂未收到任何 AI Studio 标签页心跳 (浏览器未打开或未安装油猴脚本)。")
                print(f"    -> 解决方式：打开浏览器访问 https://aistudio.google.com/ 并开启会话 [{target_title}]。")
    else:
        # Unbound / broadcast mode
        if active_tabs:
            tm_ok = True
            tab_names = ", ".join([f"[{t.get('title')}]" for t in active_tabs])
            print(f"[OK] 3. AI Studio 油猴脚本：握手在线 (未指定专属会话)")
            print(f"    -> 当前在线会话列表: {tab_names}")
            print(f"    -> [安全警示]：未在项目根目录下找到 .aistudio_config.json。")
            print(f"       强烈建议主君指定专属会话标题，例如：")
            print(f"       python src/check_handshake.py --bind-title \"具体会话标题\"")
        else:
            print("[!] 3. AI Studio 油猴脚本：暂未收到心跳 (可能未打开页面或会话未锁定)")
            print("    -> 解决方式：打开浏览器访问 https://aistudio.google.com/ 并打开对应会话。")

    print("\n-------------------------------------------------------")
    overall_ready = server_ok and cdp_ok and tm_ok
    if overall_ready:
        if target_title:
            print(f"【巡检结论】：协作链路 100% 畅通！已精准就绪于专属会话 [{target_title}]。")
        else:
            print("【巡检结论】：链路基本畅通，但当前处于广播模式，建议绑定专属会话标题后再发起咨询。")
    elif server_ok and cdp_ok:
        print("【巡检结论】：本地核心已就绪。请确认浏览器已打开对应的 AI Studio 专属会话。")
    else:
        print("【巡检结论】：链路尚未完全就绪，请按上述提示排除异常后重试。")
    print("-------------------------------------------------------\n")

    sys.exit(0 if overall_ready else 1)


if __name__ == "__main__":
    main()
