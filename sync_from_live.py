"""
AFL Bridge - Repository Sync Utility
Syncs latest production scripts, documents, and skills from live workspace into this Git repository.
"""

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
LIVE_WORKSPACE = REPO_ROOT.parent

LIVE_AFL_DIR = LIVE_WORKSPACE / "argon_anti_bridge"
LIVE_SKILLS_DIR = LIVE_WORKSPACE / ".agents" / "skills"

CORE_SCRIPTS = [
    "bridge_server.py",
    "send_to_argon.py",
    "open_userscript_install.py",
    "check_handshake.py",
    "background_window.py",
    "argon_commander.user.js",
    "start_bridge.bat",
    "launch_afl_chrome.bat",
]

DOCS = [
    "AFL_Bridge_全栈搭建与疑难排障终极宝典.md",
    "capsule_netroom_dedup_autopsy.md",
]

SKILLS = [
    "aistudio",
    "argon-collab-bridge",
    "argon-flash-commander",
    "tampermonkey-installer",
]


def sync():
    print("[SYNC] Syncing core scripts...")
    dst_src = REPO_ROOT / "src"
    dst_src.mkdir(parents=True, exist_ok=True)
    for fname in CORE_SCRIPTS:
        src_path = LIVE_AFL_DIR / fname
        if src_path.exists():
            shutil.copy2(src_path, dst_src / fname)
            print(f"  -> Synced: src/{fname}")

    print("[SYNC] Syncing docs...")
    dst_docs = REPO_ROOT / "docs"
    dst_docs.mkdir(parents=True, exist_ok=True)
    for fname in DOCS:
        src_path = LIVE_AFL_DIR / fname
        if src_path.exists():
            shutil.copy2(src_path, dst_docs / fname)
            print(f"  -> Synced: docs/{fname}")

    print("[SYNC] Syncing skills...")
    dst_skills = REPO_ROOT / "skills"
    for skill_name in SKILLS:
        skill_src = LIVE_SKILLS_DIR / skill_name
        skill_dst = dst_skills / skill_name
        skill_dst.mkdir(parents=True, exist_ok=True)
        for item in skill_src.rglob("*"):
            if item.is_file():
                rel = item.relative_to(skill_src)
                target = skill_dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
        print(f"  -> Synced: skills/{skill_name}")

    print("[SYNC] Sync completed successfully!")


if __name__ == "__main__":
    sync()
