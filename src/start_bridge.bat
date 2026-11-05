@echo off
chcp 936 >nul
title AFL Bridge - AI Studio & Antigravity 协作中枢
cd /d "%~dp0"
echo =======================================================
echo   Project Argon-Flash Link (AFL) 智能体直连协作网关
echo   本地双向网关端口: 8790
echo =======================================================
echo.
echo 正在启动 AFL Bridge 调度服务...
python bridge_server.py
pause
