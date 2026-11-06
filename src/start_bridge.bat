@echo off
chcp 65001 >nul
title AFL Bridge Server (8790)
cd /d "%~dp0"
if not exist "data" mkdir "data"
start "" /B python bridge_server.py > data\bridge_stdout.log 2>&1
echo [OK] AFL Bridge Server v6.1.0 started in background on port 8790.
