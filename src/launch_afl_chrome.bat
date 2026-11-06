@echo off
chcp 65001 >nul
title AFL Chrome - Anti-Occlusion & CDP Launcher (42068)
cd /d "%~dp0"

set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_EXE%" set "CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_EXE%" set "CHROME_EXE=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME_EXE%" (
    echo [ERROR] 未在默认路径找到 Google Chrome 可执行文件 (chrome.exe)。
    pause
    exit /b 1
)

set "AFL_URL=https://aistudio.google.com/"
set "AFL_PORT=42068"

echo =======================================================
echo   AFL Chrome 抗遮蔽休眠启动器 (Anti-Occlusion Launcher)
echo   注入 Chromium 内核底层抗挂起与调试参数
echo =======================================================
echo [*] Chrome 路径 : %CHROME_EXE%
echo [*] 调试端口   : %AFL_PORT%
echo [*] 目标网址   : %AFL_URL%
echo.
echo [*] 正在注入 4 项核心防休眠参数：
echo     --disable-backgrounding-occluded-windows
echo     --disable-renderer-backgrounding
echo     --disable-background-timer-throttling
echo     --disable-features=CalculateNativeWindowOcclusion
echo.

start "" "%CHROME_EXE%" ^
  --disable-backgrounding-occluded-windows ^
  --disable-renderer-backgrounding ^
  --disable-background-timer-throttling ^
  --disable-features=CalculateNativeWindowOcclusion,CalculateNativeWinOcclusion,IntensiveWakeUpThrottling ^
  --remote-debugging-port=%AFL_PORT% ^
  --profile-directory="Default" ^
  "%AFL_URL%"

echo [OK] Chrome 已成功以后台全速防休眠模式启动！
ping 127.0.0.1 -n 3 >nul
exit /b 0
