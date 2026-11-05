# -*- coding: utf-8 -*-
"""
Send Consultation Capsule from Antigravity to AI Studio (v5.3 Automated File Conduit Edition).
Supports 1-to-1 session routing (--target-title), multi-file attachments (--attach / -a, glob, comma-separated),
flexible attach modes (--attach-mode chip/inline), cross-device mobile relay (F5 auto-recovery),
and synchronous blocking wait (--wait) that natively wakes up the calling Antigravity conversation!
"""

import sys
import os
import json
import time
import argparse
import base64
import glob
import mimetypes
import urllib.request
import urllib.parse
import urllib.error

BRIDGE_CONSULT_URL = "http://127.0.0.1:8790/api/agent/consult"
BRIDGE_WAIT_URL = "http://127.0.0.1:8790/api/agent/wait_task"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_OUTGOING = os.path.join(DATA_DIR, "antigravity_outgoing_consult.md")


def get_windows_unicode_argv():
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
    if not start_dir:
        start_dir = os.getcwd()
    curr = os.path.abspath(start_dir)
    while True:
        cfg_path = os.path.join(curr, ".aistudio_config.json")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f), cfg_path
            except Exception:
                pass
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return None, None


def collect_attachments(attach_patterns):
    """
    Safely resolves and packages file attachments from multiple patterns (globs, paths, comma-separated).
    Extracts filename, size, MIME type, Base64 data, and UTF-8 decoded content for inline fallback.
    """
    if not attach_patterns:
        return []

    raw_candidates = []
    for item in attach_patterns:
        if not item or not str(item).strip():
            continue
        parts = [p.strip() for p in str(item).split(",") if p.strip()]
        for p in parts:
            p_expanded = os.path.expanduser(p)
            matched = glob.glob(p_expanded, recursive=True)
            if matched:
                raw_candidates.extend(matched)
            elif os.path.exists(p_expanded):
                raw_candidates.append(p_expanded)
            else:
                print(f"[AFL_ATTACH] ⚠️ Warning: Pattern or path not found: {p}", flush=True)

    seen = set()
    valid_files = []
    for p in raw_candidates:
        norm = os.path.abspath(p)
        if norm in seen:
            continue
        seen.add(norm)
        if os.path.isfile(norm):
            valid_files.append(norm)
        elif os.path.isdir(norm):
            for root, _, files in os.walk(norm):
                for f in files:
                    fp = os.path.abspath(os.path.join(root, f))
                    if fp not in seen:
                        seen.add(fp)
                        valid_files.append(fp)

    text_extensions = {
        ".cs": "text/x-csharp",
        ".vue": "text/x-vue",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".ts": "text/typescript",
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".bat": "text/plain",
        ".cmd": "text/plain",
        ".sh": "text/x-sh",
        ".log": "text/plain",
        ".toml": "text/plain",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".html": "text/html",
        ".htm": "text/html",
        ".css": "text/css",
        ".xml": "text/xml",
        ".sql": "text/x-sql",
        ".ini": "text/plain",
        ".env": "text/plain",
        ".gradle": "text/plain",
        ".props": "text/plain",
        ".config": "text/plain"
    }

    results = []
    for fpath in valid_files:
        try:
            fname = os.path.basename(fpath)
            fsize = os.path.getsize(fpath)
            guessed_mime, _ = mimetypes.guess_type(fpath)
            ext = os.path.splitext(fname)[1].lower()
            mime = guessed_mime or "application/octet-stream"
            if ext in text_extensions:
                mime = text_extensions[ext]

            with open(fpath, "rb") as bf:
                raw_bytes = bf.read()

            b64_str = base64.b64encode(raw_bytes).decode("ascii")

            is_text = False
            content_text = None
            try:
                content_text = raw_bytes.decode("utf-8")
                is_text = True
            except UnicodeDecodeError:
                try:
                    content_text = raw_bytes.decode("gbk")
                    is_text = True
                except UnicodeDecodeError:
                    is_text = False
                    content_text = None

            results.append({
                "name": fname,
                "path": fpath,
                "size": fsize,
                "mime": mime,
                "is_text": is_text,
                "data_b64": b64_str,
                "content_text": content_text
            })
        except Exception as e:
            print(f"[AFL_ATTACH] ⚠️ Failed to process file '{fpath}': {e}", flush=True)

    return results


def send_and_optionally_wait(text, target_title=None, wait_for_reply=True, max_wait_sec=3600, attachments=None, attach_mode="chip"):
    payload = {
        "consult_text": text,
        "attachments": attachments or [],
        "attach_mode": attach_mode or "chip"
    }
    if target_title:
        payload["target_title"] = target_title

    if attachments:
        print(f"[AFL_ATTACH] 📦 Loaded {len(attachments)} attachment(s) [Mode: {attach_mode}]:", flush=True)
        for att in attachments:
            sz_str = f"{att['size'] / 1024:.1f} KB" if att['size'] < 1024 * 1024 else f"{att['size'] / (1024 * 1024):.2f} MB"
            print(f"  📎 {att['name']} ({sz_str}, {att['mime']}, text: {att['is_text']})", flush=True)

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_CONSULT_URL,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "Antigravity-Consult/5.3"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[AFL_CONSULT] Failed to submit consultation to Bridge: {e}")
        return False

    ticket_id = data.get("id")
    reply_file = data.get("reply_file")
    print(f"[AFL_CONSULT] Queued successfully! Ticket: [{ticket_id}] | Target Session: [{target_title or 'Broadcast'}]", flush=True)

    if not wait_for_reply:
        return True

    print(f"[AFL_CONSULT] Entering Reactive Wakeup blocking wait on Ticket [{ticket_id}] (max {max_wait_sec}s)...", flush=True)
    start_ts = time.time()
    last_reported_event = None

    while time.time() - start_ts < max_wait_sec:
        try:
            q = urllib.parse.urlencode({"ticket": ticket_id, "timeout": "40"})
            wait_req = urllib.request.Request(f"{BRIDGE_WAIT_URL}?{q}", headers={"User-Agent": "Antigravity-Waiter/5.3"})
            with urllib.request.urlopen(wait_req, timeout=45) as resp:
                w_data = json.loads(resp.read().decode("utf-8"))

            client_ev = w_data.get("client_event")
            client_det = w_data.get("client_detail")
            if client_ev and (client_ev, client_det) != last_reported_event:
                last_reported_event = (client_ev, client_det)
                if client_ev == "RETRY_EXHAUSTED_AWAITING_MANUAL":
                    print(f"\n[AFL_STATUS] ⚠️ AI Studio 自动重试已达上限(2/2)，系统已停止重试并转入【手机接力 / F5 刷新静默守候态】，等待主君操作...", flush=True)
                elif "RETRY" in client_ev:
                    print(f"\n[AFL_STATUS] 🔄 AI Studio 原生报错驱动有限自愈中: {client_ev} ({client_det})", flush=True)
                else:
                    print(f"\n[AFL_STATUS] ℹ️ AI Studio 状态遥测: {client_ev} ({client_det})", flush=True)

            if w_data.get("status") == "has_task":
                task = w_data.get("task", {})
                raw_text = (task.get("raw_text") or "").strip()
                saved_path = task.get("reply_file") or reply_file
                src_title = task.get("source_title") or target_title or "AI Studio"

                print("\n" + "=" * 72)
                print(f"【AFL v5.3 统帅裁决已送达 · Reactive Wakeup 自动唤醒】")
                print(f"  来源会话 : [{src_title}]")
                print(f"  事务令牌 : {ticket_id}")
                print(f"  字符总数 : {len(raw_text)} 字符")
                print(f"  专属文件 : {saved_path}")
                print("=" * 72 + "\n")

                if len(raw_text) <= 2500:
                    print(raw_text)
                    print("\n" + "=" * 72)
                else:
                    preview = raw_text[:500]
                    print(f"【前 500 字符摘要预览】：\n{preview}...\n")
                    print("=" * 72)
                    print(f"⚡【第一反射指令】：因统帅批复长达 {len(raw_text)} 字符，完整无损原典已落盘至：")
                    print(f"👉 `{saved_path}`")
                    print("请立即调用文件读取工具 (read_file / view_file) 查阅上述路径全文，并严格遵照执行！")
                    print("=" * 72)

                sys.stdout.flush()
                return True

        except KeyboardInterrupt:
            print("[AFL_CONSULT] Wait interrupted by user.")
            return False
        except Exception:
            time.sleep(1.5)

    print(f"[AFL_CONSULT] Timeout after {max_wait_sec}s waiting for Ticket [{ticket_id}].")
    return False


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    raw_args = get_windows_unicode_argv()[1:]
    parser = argparse.ArgumentParser(description="Send consultation capsule to AI Studio Argon (v5.3 Automated File Conduit Edition)")
    parser.add_argument("--file", "-f", help="Markdown file containing the consultation capsule")
    parser.add_argument("--text", "-t", help="Raw consultation text")
    parser.add_argument("--attach", "-a", action="append", default=[], help="File path(s) or glob pattern(s) to attach (supports wildcards, comma-separated, or multiple -a)")
    parser.add_argument("--attach-mode", choices=["chip", "inline"], default="chip", help="Attachment mode: 'chip' (mount as native file chip) or 'inline' (embed as text in prompt body)")
    parser.add_argument("--target-title", "-tt", help="Target AI Studio prompt title for 1-to-1 routing")
    parser.add_argument("--wait", "-w", action="store_true", default=True, help="Block until reply arrives to trigger Reactive Wakeup (default: True)")
    parser.add_argument("--no-wait", action="store_true", help="Exit immediately after queueing without waiting")
    parser.add_argument("--timeout", type=int, default=3600, help="Maximum wait timeout in seconds (default: 3600)")
    parser.add_argument("pos_text", nargs="*", help="Positional text")
    args = parser.parse_args(raw_args)

    target_title = None
    if args.target_title and args.target_title.strip():
        target_title = args.target_title.strip()
    else:
        cfg, cfg_path = find_project_config()
        if cfg and cfg.get("target_title"):
            target_title = cfg.get("target_title").strip()

    content = ""
    if args.text:
        content = args.text
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            print(f"[AFL_CONSULT] Error: File {args.file} not found.")
            sys.exit(1)
    elif args.pos_text:
        content = " ".join(args.pos_text)
    elif os.path.exists(DEFAULT_OUTGOING):
        with open(DEFAULT_OUTGOING, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

    if not content.strip():
        print("[AFL_CONSULT] Error: Empty consultation content.")
        sys.exit(1)

    # AFL Capsule Provenance Guard: Ensure explicit capsule signature exists
    capsule_markers = ["【AFL", "AFL_CAPSULE", "咨询胶囊", "呈报对象", "[AFL_READY_FOR_DECISION]"]
    if not any(m in content for m in capsule_markers):
        content = content.rstrip() + "\n\n<!-- [AFL_CAPSULE] -->\n"

    # Package attachments
    attachments = collect_attachments(args.attach)

    should_wait = False if args.no_wait else args.wait
    ok = send_and_optionally_wait(
        content,
        target_title=target_title,
        wait_for_reply=should_wait,
        max_wait_sec=args.timeout,
        attachments=attachments,
        attach_mode=args.attach_mode
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
