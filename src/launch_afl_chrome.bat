@echo off

chcp 936 >nul

title AFL Chrome - Anti-Occlusion & CDP Launcher (42068)

cd /d "%~dp0"



set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME_EXE%" set "CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME_EXE%" set "CHROME_EXE=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"



if not exist "%CHROME_EXE%" (

    echo [错误] 未能在默认路径找到 Google Chrome 浏览器 (chrome.exe)！

    pause

    exit /b 1

)



set "AFL_URL=https://aistudio.google.com/"

set "AFL_PORT=42068"



echo =======================================================

echo   AFL Chrome 工业级抗遮蔽启动器 (Anti-Occlusion Launcher)

echo   Chromium 156 彻底关闭窗口遮挡休眠与渲染冻结

echo =======================================================

echo [*] Chrome 路径 : %CHROME_EXE%

echo [*] 调试端口   : %AFL_PORT%

echo [*] 目标网址   : %AFL_URL%

echo.

echo [*] 正在注入 4 大抗遮蔽与全速运转启动参数：

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



echo [OK] Chrome 已成功启动！窗口全速运转，无惧任何遮挡或底层叠放。

ping 127.0.0.1 -n 3 >nul

exit /b 0

