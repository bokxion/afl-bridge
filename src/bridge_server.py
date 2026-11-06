# -*- coding: utf-8 -*-
"""
AFL Bridge Server v6.1.0 (Clean Core & Win32 SW_SHOWNOACTIVATE + HWND_BOTTOM Window Conduit)
Port: 8790
"""

import os
import sys
import json
import time
import uuid
import re
import threading
try:
    from http.server import ThreadingHTTPServer as HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

if sys.platform == "win32":
    try:
        if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

PORT = 8790
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TASKS_DIR = os.path.join(DATA_DIR, "tasks")
INCOMING_TASK_FILE = os.path.join(DATA_DIR, "argon_incoming_task.md")
OUTGOING_CONSULT_FILE = os.path.join(DATA_DIR, "antigravity_outgoing_consult.md")
TRANSACTION_LOG_FILE = os.path.join(DATA_DIR, "afl_transactions.jsonl")
USERSCRIPT_FILE = os.path.join(BASE_DIR, "argon_commander.user.js")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

transaction_log_lock = threading.Lock()


def log_transaction(event, data=None):
    try:
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": time.time(),
            "event": event,
            "data": data or {}
        }
        with transaction_log_lock:
            with open(TRANSACTION_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                f.flush()
    except Exception as e:
        print(f"[AFL_BRIDGE] Failed to write transaction log: {e}")


def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|\s]+', '_', str(name or "default")).strip('_')[:40]


# ==============================================================================
# 【v6.0 核心模块】：Win32 后台无感解封最小化与收信自动归位引擎
# ==============================================================================
class Win32WindowConduit:
    """
    当 Chrome 处于最小化 (SW_MINIMIZE) 状态时，Windows DWM 会剥夺其画布导致 Angular 停止渲染 DOM。
    本模块在发信/等待期间，通过 SW_SHOWNOACTIVATE (4) + HWND_BOTTOM (1) 在后台静默恢复 Chrome 画布，
    将其压在当前所有窗口最底层（绝不弹窗、绝不抢焦点）；待收信落盘瞬间，自动将其重新最小化归位！
    """
    SW_SHOWNOACTIVATE = 4
    SW_MINIMIZE = 6
    HWND_BOTTOM = 1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010

    def __init__(self):
        self.lock = threading.Lock()
        self.auto_unminimized_hwnds = set()

    def _attach_interactive_desktop(self):
        if sys.platform != "win32":
            return None
        try:
            import ctypes
            user32 = ctypes.windll.user32
            h_desk = user32.OpenDesktopW("Default", 0, False, 0x10000000)
            if h_desk:
                user32.SetThreadDesktop(h_desk)
                return h_desk
        except Exception:
            pass
        return None

    def _find_chrome_hwnds(self, target_title=None):
        if sys.platform != "win32":
            return []
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        matched_primary = []
        matched_fallback = []

        def enum_cb(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            cls_buf = ctypes.create_unicode_buffer(128)
            user32.GetClassNameW(hwnd, cls_buf, 128)
            if cls_buf.value != "Chrome_WidgetWin_1":
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            title_buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, title_buf, length + 1)
            win_title = title_buf.value
            win_title_low = win_title.lower()

            if "google chrome" not in win_title_low and "ai studio" not in win_title_low:
                return True

            if ("ai studio" in win_title_low) or (target_title and target_title.strip().lower() in win_title_low):
                matched_primary.append((hwnd, win_title))
            else:
                matched_fallback.append((hwnd, win_title))
            return True

        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return matched_primary if matched_primary else matched_fallback

    def ensure_chrome_unminimized_behind(self, target_title=None):
        """若目标 Chrome 窗口处于最小化状态，静默恢复其画布并压至 Z 轴最底层，不抢夺任何焦点。"""
        if sys.platform != "win32":
            return
        with self.lock:
            h_desk = self._attach_interactive_desktop()
            try:
                import ctypes
                user32 = ctypes.windll.user32
                candidates = self._find_chrome_hwnds(target_title)
                for hwnd, win_title in candidates:
                    if user32.IsIconic(hwnd):
                        # 1. 在不激活窗口、不抢键盘焦点的前提下解除最小化，恢复 GPU 画布尺寸
                        user32.ShowWindow(hwnd, self.SW_SHOWNOACTIVATE)
                        # 2. 立即将其压入 Z 轴最底层 (HWND_BOTTOM)，使其躲在 Antigravity 窗口背后
                        user32.SetWindowPos(
                            hwnd,
                            self.HWND_BOTTOM,
                            0, 0, 0, 0,
                            self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOACTIVATE
                        )
                        self.auto_unminimized_hwnds.add(hwnd)
                        print(f"[AFL_WIN32] 🔓 检测到 Chrome 处于最小化，已静默恢复画布并压至最底层: [{win_title}]", flush=True)
            except Exception as e:
                print(f"[AFL_WIN32] ensure_chrome_unminimized_behind error: {e}", flush=True)
            finally:
                if h_desk:
                    try:
                        ctypes.windll.user32.CloseDesktop(h_desk)
                    except Exception:
                        pass

    def restore_minimized_state_if_needed(self):
        """当所有任务收信完毕后，将此前被自动解封的最小化窗口重新缩回任务栏。"""
        if sys.platform != "win32":
            return
        with self.lock:
            if not self.auto_unminimized_hwnds:
                return
            h_desk = self._attach_interactive_desktop()
            try:
                import ctypes
                user32 = ctypes.windll.user32
                for hwnd in list(self.auto_unminimized_hwnds):
                    if user32.IsWindow(hwnd) and not user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, self.SW_MINIMIZE)
                        print(f"[AFL_WIN32] 🔒 收信完毕，已将 Chrome 窗口自动重新最小化归位 (hwnd={hwnd})", flush=True)
                self.auto_unminimized_hwnds.clear()
            except Exception as e:
                print(f"[AFL_WIN32] restore_minimized_state_if_needed error: {e}", flush=True)
            finally:
                if h_desk:
                    try:
                        ctypes.windll.user32.CloseDesktop(h_desk)
                    except Exception:
                        pass


win32_conduit = Win32WindowConduit()


class WorkflowBridgeManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.tickets = {}
        self.ticket_order = []
        self.active_tabs = {}
        self.last_heartbeat = None
        self.is_paused = False
        self.iteration_count = 0

    def _titles_match(self, target_title, tab_title):
        if not target_title:
            return True
        if not tab_title:
            return False
        t_target = target_title.strip().lower()
        t_tab = tab_title.strip().lower()
        if t_target == t_tab:
            return True
        if t_target in t_tab or t_tab in t_target:
            return True
        return False

    def _find_awaiting_ticket_for_tab(self, tab_title):
        if not tab_title:
            return None
        clean_tab = tab_title.strip()
        for tid in reversed(self.ticket_order):
            slot = self.tickets.get(tid)
            if slot and slot.get("status") in ("IN_PROGRESS", "DISPATCHED"):
                if self._titles_match(slot.get("target_title"), clean_tab):
                    return {
                        "id": slot["id"],
                        "target_title": slot.get("target_title"),
                        "prompt_snippet": (slot.get("consult_text") or "").strip()[:80],
                        "consult_text": slot.get("consult_text"),
                        "timestamp": slot.get("timestamp")
                    }
        return None

    def update_heartbeat(self, data):
        with self.lock:
            now = time.time()
            title = (data.get("title") or "Untitled").strip()
            url = data.get("url", "")
            tab_key = f"{title}::{url}" if url else title
            tab_info = dict(data)
            tab_info["received_at"] = now
            self.active_tabs[tab_key] = tab_info
            self.last_heartbeat = tab_info
            self.active_tabs = {k: v for k, v in self.active_tabs.items() if now - v.get("received_at", 0) < 15}
            awaiting = self._find_awaiting_ticket_for_tab(title)
            return {
                "status": "ok",
                "active_tab_count": len(self.active_tabs),
                "awaiting_ticket": awaiting
            }

    def submit_consultation_from_antigravity(self, consult_text, target_title=None, attachments=None, attach_mode="chip", output_path=None):
        clean_title = target_title.strip() if target_title and target_title.strip() else None
        # 发信瞬间：若 Chrome 处于最小化，立即在后台静默恢复画布并压至 Z 轴最底层！
        win32_conduit.ensure_chrome_unminimized_behind(clean_title)

        with self.lock:
            short_uid = uuid.uuid4().hex[:6]
            ticket_id = f"consult_{int(time.time()*1000)}_{short_uid}"
            reply_file = os.path.join(TASKS_DIR, f"{ticket_id}_reply.md")
            attachments = attachments or []

            if "[AFL_CAPSULE]" not in consult_text and "【AFL" not in consult_text and "咨询胶囊】" not in consult_text:
                consult_text = f"{consult_text.rstrip()}\n\n<!-- [AFL_CAPSULE] [AFL_TICKET:{ticket_id}] -->\n"

            slot = {
                "id": ticket_id,
                "consult_text": consult_text,
                "attachments": attachments,
                "attach_mode": attach_mode,
                "output_path": output_path,
                "target_title": clean_title,
                "timestamp": time.time(),
                "ready_for_aistudio": True,
                "status": "PENDING",
                "dispatched_count": 0,
                "event": threading.Event(),
                "reply_text": None,
                "reply_file": reply_file,
                "source_title": None,
                "last_client_event": None,
                "last_client_detail": None
            }
            self.tickets[ticket_id] = slot
            self.ticket_order.append(ticket_id)

            while len(self.ticket_order) > 100:
                old_id = self.ticket_order.pop(0)
                self.tickets.pop(old_id, None)

            try:
                with open(OUTGOING_CONSULT_FILE, "w", encoding="utf-8") as f:
                    f.write(consult_text)
            except Exception:
                pass

            log_transaction("PENDING", {
                "id": ticket_id,
                "target_title": clean_title,
                "chars": len(consult_text),
                "attachments_count": len(attachments),
                "output_path": output_path,
                "timestamp": slot["timestamp"]
            })

            target_desc = f"targeted for [{clean_title}]" if clean_title else "broadcast (any tab)"
            print(f"[AFL_BRIDGE] Queued Ticket [{ticket_id}] ({len(consult_text)} chars, {len(attachments)} files, {target_desc}).", flush=True)
            return {
                "status": "ok",
                "id": ticket_id,
                "target_title": clean_title,
                "reply_file": reply_file,
                "output_path": output_path,
                "message": f"Consultation queued under ticket [{ticket_id}] ({target_desc})."
            }

    def poll_consultation_for_tampermonkey(self, tab_title=None):
        with self.lock:
            if self.is_paused:
                return None
            clean_tab_title = tab_title.strip() if tab_title and tab_title.strip() else ""

            matched_slot = None
            for tid in self.ticket_order:
                slot = self.tickets.get(tid)
                if not slot or not slot.get("ready_for_aistudio"):
                    continue
                target = slot.get("target_title")
                if target and clean_tab_title and target.strip().lower() == clean_tab_title.lower():
                    matched_slot = slot
                    break

            if not matched_slot:
                for tid in self.ticket_order:
                    slot = self.tickets.get(tid)
                    if not slot or not slot.get("ready_for_aistudio"):
                        continue
                    if self._titles_match(slot.get("target_title"), clean_tab_title):
                        matched_slot = slot
                        break

            if matched_slot:
                # 关键单次执行幂等锁：只要被任何标签页匹配拉取，立即原子锁死 ready_for_aistudio = False！
                # 彻底根绝在 Tampermonkey 发送 ack_consultation 之前的网络并发窗口内被二次拉取的致命缺陷！
                matched_slot["ready_for_aistudio"] = False
                matched_slot["status"] = "DISPATCHED"
                matched_slot["dispatched_at"] = time.time()
                matched_slot["dispatched_tab"] = clean_tab_title
                matched_slot["dispatched_count"] = matched_slot.get("dispatched_count", 0) + 1
                log_transaction("DISPATCHED_TO_AISTUDIO", {
                    "id": matched_slot["id"],
                    "target_title": matched_slot.get("target_title"),
                    "tab_title": clean_tab_title,
                    "count": matched_slot["dispatched_count"]
                })
                return {
                    "id": matched_slot["id"],
                    "consult_text": matched_slot["consult_text"],
                    "attachments": matched_slot.get("attachments", []),
                    "attach_mode": matched_slot.get("attach_mode", "chip"),
                    "prompt_snippet": matched_slot["consult_text"].strip()[:80],
                    "target_title": matched_slot["target_title"],
                    "timestamp": matched_slot["timestamp"]
                }

            return None

    def ack_consultation_delivered(self, consult_id=None, tab_title=None):
        with self.lock:
            delivered = False
            if consult_id and consult_id in self.tickets:
                self.tickets[consult_id]["ready_for_aistudio"] = False
                self.tickets[consult_id]["status"] = "IN_PROGRESS"
                delivered = True
            else:
                for tid in self.ticket_order:
                    slot = self.tickets.get(tid)
                    if slot and slot.get("ready_for_aistudio") and self._titles_match(slot.get("target_title"), tab_title):
                        slot["ready_for_aistudio"] = False
                        slot["status"] = "IN_PROGRESS"
                        consult_id = tid
                        delivered = True
                        break

            log_transaction("ACK_DELIVERED", {
                "id": consult_id,
                "tab_title": tab_title,
                "delivered": delivered
            })
            return {"status": "ok", "id": consult_id}

    def report_client_status(self, body):
        with self.lock:
            tid = body.get("ticket_id")
            evt = body.get("event", "STATUS_UPDATE")
            detail = body.get("detail", {})
            if tid and tid in self.tickets:
                self.tickets[tid]["last_client_event"] = evt
                self.tickets[tid]["last_client_detail"] = detail
            log_transaction(evt, body)
            print(f"[AFL_BRIDGE] Status from [{body.get('source_title')}]: {evt} | {detail}", flush=True)
            return {"status": "ok"}

    def dispatch_from_argon(self, raw_text, source_title=None, source_url=None, ticket_id=None):
        if not raw_text or len(raw_text.strip()) < 10:
            return {"status": "ignored", "message": "Ignored empty raw_text."}

        clean_text = raw_text.strip()
        clean_source = (source_title or "Untitled").strip()
        has_remaining_active = False

        with self.lock:
            if self.is_paused:
                return {"status": "paused", "message": "Bridge is currently paused."}

            target_slot = None
            if ticket_id and ticket_id in self.tickets:
                target_slot = self.tickets[ticket_id]

            if not target_slot:
                for tid in reversed(self.ticket_order):
                    slot = self.tickets.get(tid)
                    if slot and slot.get("status") in ("DISPATCHED", "IN_PROGRESS", "PENDING"):
                        if self._titles_match(slot.get("target_title"), clean_source):
                            target_slot = slot
                            break

            if not target_slot:
                print(f"[AFL_BRIDGE] REJECTED unsolicited dispatch from tab [{clean_source}] (ticket={ticket_id}).", flush=True)
                log_transaction("ROGUE_DISPATCH_REJECTED", {
                    "source_title": clean_source,
                    "ticket_id": ticket_id,
                    "chars": len(clean_text)
                })
                return {"status": "ignored", "message": f"No active consultation waiting for tab [{clean_source}]."}

            resolved_tid = target_slot["id"]
            reply_file = target_slot["reply_file"]
            custom_out = target_slot.get("output_path")
            channel_file = os.path.join(TASKS_DIR, f"latest_{safe_filename(clean_source)}.md")

            self.iteration_count += 1
            target_slot["reply_text"] = clean_text
            target_slot["source_title"] = clean_source
            target_slot["status"] = "COMPLETED"
            target_slot["completed_at"] = time.time()

            if custom_out:
                try:
                    os.makedirs(os.path.dirname(os.path.abspath(custom_out)), exist_ok=True)
                except Exception:
                    pass

            for fpath in filter(None, (reply_file, channel_file, INCOMING_TASK_FILE, custom_out)):
                try:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(clean_text)
                except Exception as e:
                    print(f"[AFL_BRIDGE] Failed to write {fpath}: {e}")

            log_transaction("CAPTURED_FROM_AISTUDIO", {
                "ticket_id": resolved_tid,
                "source_title": clean_source,
                "chars": len(clean_text),
                "reply_file": reply_file,
                "output_path": custom_out,
                "iteration": self.iteration_count
            })

            target_slot["event"].set()
            has_remaining_active = any(
                s.get("status") in ("PENDING", "DISPATCHED", "IN_PROGRESS")
                for s in self.tickets.values()
            )
            print(f"[AFL_BRIDGE] Ticket [{resolved_tid}] COMPLETED ({len(clean_text)} chars from [{clean_source}]). Saved & triggered wakeup!", flush=True)

        # 若无其他进行中任务，自动将此前被后台解封的 Chrome 窗口重新最小化回任务栏！
        if not has_remaining_active:
            win32_conduit.restore_minimized_state_if_needed()

        return {
            "status": "ok",
            "ticket_id": resolved_tid,
            "reply_file": reply_file,
            "output_path": custom_out,
            "message": f"Reply routed to ticket [{resolved_tid}]."
        }

    def wait_for_ticket(self, ticket_id=None, target_title=None, timeout=40.0):
        target_slot = None
        with self.lock:
            if ticket_id and ticket_id in self.tickets:
                target_slot = self.tickets[ticket_id]
            elif target_title:
                for tid in reversed(self.ticket_order):
                    slot = self.tickets.get(tid)
                    if slot and self._titles_match(slot.get("target_title"), target_title):
                        target_slot = slot
                        break
            elif self.ticket_order:
                target_slot = self.tickets.get(self.ticket_order[-1])

        if not target_slot:
            return {"status": "error", "message": f"Ticket [{ticket_id}] not found."}

        if target_slot.get("status") == "COMPLETED" and target_slot.get("reply_text"):
            return {
                "status": "has_task",
                "task": {
                    "task_id": target_slot["id"],
                    "source_title": target_slot.get("source_title"),
                    "reply_file": target_slot.get("reply_file"),
                    "output_path": target_slot.get("output_path"),
                    "raw_text": target_slot["reply_text"]
                }
            }

        # 等待期间巡检：若主君在中途随手点了最小化，自动在后台无感恢复画布并压至底层
        win32_conduit.ensure_chrome_unminimized_behind(target_slot.get("target_title"))

        triggered = target_slot["event"].wait(timeout=timeout)
        if triggered and target_slot.get("reply_text"):
            return {
                "status": "has_task",
                "task": {
                    "task_id": target_slot["id"],
                    "source_title": target_slot.get("source_title"),
                    "reply_file": target_slot.get("reply_file"),
                    "output_path": target_slot.get("output_path"),
                    "raw_text": target_slot["reply_text"]
                }
            }
        return {
            "status": "timeout",
            "ticket_id": target_slot["id"],
            "current_state": target_slot.get("status"),
            "client_event": target_slot.get("last_client_event"),
            "client_detail": target_slot.get("last_client_detail")
        }

    def toggle_pause(self):
        with self.lock:
            self.is_paused = not self.is_paused
            return {"status": "ok", "is_paused": self.is_paused}

    def reset(self):
        with self.lock:
            self.iteration_count = 0
            for slot in self.tickets.values():
                slot["event"].set()
            self.tickets.clear()
            self.ticket_order.clear()
            self.is_paused = False
            log_transaction("RESET", {})
            return {"status": "ok", "message": "Reset completed."}

    def get_status(self):
        with self.lock:
            now = time.time()
            alive_tabs = [tab for tab in self.active_tabs.values() if now - tab.get("received_at", 0) < 15]
            active_tickets = [
                {"id": s["id"], "target": s.get("target_title"), "status": s.get("status")}
                for s in self.tickets.values() if s.get("status") in ("PENDING", "DISPATCHED", "IN_PROGRESS")
            ]
            return {
                "status": "running",
                "version": "6.1.0",
                "is_paused": self.is_paused,
                "iteration_count": self.iteration_count,
                "has_pending_consultation": len(active_tickets) > 0,
                "active_tickets": active_tickets,
                "pending_targets": [t["target"] for t in active_tickets if t.get("target")],
                "tampermonkey_connected": len(alive_tabs) > 0,
                "active_tab_count": len(alive_tabs),
                "active_tabs": alive_tabs,
                "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            }


manager = WorkflowBridgeManager()


class BridgeRequestHandler(BaseHTTPRequestHandler):
    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError, TimeoutError):
            pass
        except Exception:
            pass

    def log_message(self, format, *args):
        if any(k in self.path for k in ("poll", "heartbeat", "wait_task", "_ipc_tick", "wait_ms")):
            return
        super().log_message(format, *args)

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self._send_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len == 0:
                return {}
            raw = self.rfile.read(content_len).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        if path in ("/api/status", "/status"):
            try:
                wait_ms = int(query_params.get("wait_ms", ["0"])[0])
                if 0 < wait_ms <= 500:
                    time.sleep(wait_ms / 1000.0)
            except Exception:
                pass
            self._send_json(manager.get_status())

        elif path in ("/api/bridge/poll_consultation", "/api/bridge/poll_report"):
            tab_title = query_params.get("title", [""])[0]
            consult = manager.poll_consultation_for_tampermonkey(tab_title)
            if consult:
                print(f"[AFL_BRIDGE] Tab [{tab_title}] claimed Ticket [{consult.get('id')}]", flush=True)
                self._send_json({"status": "has_consultation", "consultation": consult})
            else:
                with manager.lock:
                    awaiting = manager._find_awaiting_ticket_for_tab(tab_title)
                self._send_json({"status": "idle", "awaiting_ticket": awaiting})

        elif path == "/api/agent/wait_task":
            ticket_id = query_params.get("ticket", [None])[0]
            target_title = query_params.get("title", [None])[0]
            timeout = float(query_params.get("timeout", ["40"])[0])
            res = manager.wait_for_ticket(ticket_id=ticket_id, target_title=target_title, timeout=timeout)
            self._send_json(res)

        elif path == "/api/bridge/userscript" or path.endswith(".user.js"):
            req_fname = os.path.basename(path)
            target_f = os.path.join(BASE_DIR, req_fname) if req_fname.endswith(".user.js") and os.path.exists(os.path.join(BASE_DIR, req_fname)) else USERSCRIPT_FILE
            if os.path.exists(target_f):
                with open(target_f, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self._send_cors()
                self.send_header("Content-Type", "text/javascript; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_json({"status": "error", "message": "Userscript file not found."}, 404)

        elif path in ("/", "/index.html"):
            body = f"<html><body style='background:#1e1e24;color:#abb2bf;font-family:sans-serif;padding:24px;'><h2>AFL Bridge v6.0.2 Constellation Bus</h2><pre>{json.dumps(manager.get_status(), ensure_ascii=False, indent=2)}</pre></body></html>".encode("utf-8")
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._send_json({"status": "error", "message": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path in ("/api/agent/consult", "/api/agent/report"):
            text = body.get("consult_text", body.get("report_text", body.get("text", "")))
            target_title = body.get("target_title", None)
            attachments = body.get("attachments", [])
            attach_mode = body.get("attach_mode", "chip")
            output_path = body.get("output_path", None)
            res = manager.submit_consultation_from_antigravity(
                text, target_title, attachments=attachments, attach_mode=attach_mode, output_path=output_path
            )
            self._send_json(res)

        elif path == "/api/bridge/heartbeat":
            res = manager.update_heartbeat(body)
            self._send_json(res)

        elif path in ("/api/bridge/ack_consultation", "/api/bridge/ack_report"):
            consult_id = body.get("id")
            tab_title = body.get("target_title", body.get("title"))
            res = manager.ack_consultation_delivered(consult_id, tab_title)
            self._send_json(res)

        elif path == "/api/bridge/report_status":
            res = manager.report_client_status(body)
            self._send_json(res)

        elif path == "/api/bridge/dispatch":
            raw_text = body.get("raw_text", body.get("text", ""))
            source_title = body.get("source_title", None)
            source_url = body.get("source_url", None)
            ticket_id = body.get("ticket_id", None)
            res = manager.dispatch_from_argon(raw_text, source_title, source_url, ticket_id=ticket_id)
            self._send_json(res)

        elif path == "/api/bridge/reset":
            self._send_json(manager.reset())

        elif path == "/api/bridge/toggle_pause":
            self._send_json(manager.toggle_pause())

        else:
            self._send_json({"status": "error", "message": "Not Found"}, 404)


def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, BridgeRequestHandler)
    print(f"[AFL_BRIDGE] v6.0.2 Constellation Bus listening at http://127.0.0.1:{PORT}", flush=True)
    while True:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            break
        except Exception:
            time.sleep(0.5)


if __name__ == "__main__":
    run_server()