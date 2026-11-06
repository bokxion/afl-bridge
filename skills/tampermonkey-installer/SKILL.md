---
name: tampermonkey-installer
description: 安装与更新油猴 (Tampermonkey) 脚本/插件的标准工程技能。当用户提到“安装油猴脚本”、“更新油猴脚本”、“更新油猴插件”、“油猴更新”、“tampermonkey install”或在 AI Studio (AFL) 直连协同中需要部署/刷新浏览器端中继脚本时激活。提供 Windows 隔离桌面跨越、前台焦点锁解除、本地 HTTP MIME 伺服与 Chrome 原生油猴拦截唤起的完整标准化执行流程。
---

# 油猴 (Tampermonkey) 脚本唤起安装与更新标准作业工程规范

本技能专为在 Windows 环境下**安全、确定性地穿透沙盒、唤起 Google Chrome 浏览器并激活 Tampermonkey 原生安装/更新界面**而设计。彻底攻克了智能体/终端在隔离桌面沙盒中无法弹出前台窗口、焦点被系统锁定、Edge 协议劫持、MIME 错乱以及普通脚本挂死的深层系统级难题。

---

## 一、 为什么普通命令行或 Start-Process 必定失败（五大致命物理陷阱）

在自动化运维或智能体执行中，直接调用 PowerShell 的 `Start-Process http://...`、Python 的 `webbrowser.open()` 或普通命令行 `chrome.exe <url>` 经常发生“命令执行成功但用户屏幕毫无反应”或“脚本卡死”，其底层原因由 Windows 内核与浏览器安全机制共同决定：

1. **Windows 桌面沙盒隔离 (Desktop Sandbox Isolation)**：
   - Antigravity、后台服务进程（Windows Services）或受限子进程通常运行在独立的桌面窗口站分支中（如 `WinSta0\exebox-...` 或非交互 Session）；
   - 在此隔离环境中直接启动的 GUI 子进程默认被拘束在隐藏的隔离桌面上，**根本无法在用户当前正在注视的主交互桌面 (`WinSta0\Default`) 上渲染和弹出**。
2. **Windows 前台焦点锁定机制 (LockSetForegroundWindow)**：
   - 现代 Windows 系统为了防止恶意软件抢占用户键盘鼠标，实施了严格的前台焦点锁保护（`LockSetForegroundWindow` / `ForegroundLockTimeout`）；
   - 处于后台或非激活会话的进程调用 `SetForegroundWindow()` 会被系统内核强行拦截，窗口只能在任务栏闪烁橙色图标，无法自动置顶弹到用户视线正中央。
3. **系统默认浏览器劫持与多浏览器混用冲突**：
   - 使用系统 `Start-Process` 或 URL 协议调用时，Windows 会将请求路由到系统默认浏览器（通常为 Microsoft Edge）；
   - 但公子的 AFL 统帅直连环境与 Tampermonkey 插件通常部署在 **Google Chrome** 中。若唤起 Edge，因其未安装油猴，将直接表现为纯文本展示或文件下载，安装流程彻底中断。
4. **缺少 `.user.js` 后缀或 MIME 类型错乱导致油猴拦截失效**：
   - Tampermonkey 扩展在浏览器内核中注册的网络请求/导航拦截器，**严格依赖 URL 末尾是否以 `.user.js` 结尾**，以及 HTTP 响应头是否为合法的 JavaScript MIME 类型（如 `text/javascript; charset=utf-8`）；
   - 若向浏览器投递普通的 `/userscript`、`/download` 或 API 路由而未带 `.user.js` 后缀，Chrome 会直接触发常规文件下载或在页面中直接打印源码，无法唤起 Tampermonkey 原生的代码对比与安装确认面板。
5. **Python 原生 HTTP 服务器 Keep-Alive 挂死**：
   - Chrome 在发起请求拉取 userscript 时，默认发送 HTTP/1.1 长连接（`Connection: keep-alive`）；
   - 若本地中继服务器未在多线程中并发响应，极易被 Chrome 的持续挂起连接锁死主线程，造成网关彻底假死。

---

## 二、 核心底层机理：Win32 跨桌面穿透与强行置顶

必须通过 Python `ctypes` 调用底层的 Win32 API 实施以下精准技术穿透：

```
[ Antigravity / Flash 执行官 ] (处于 WinSta0\exebox-...)
        │
        ▼ 1. OpenDesktopW("Default") & SetThreadDesktop
  [ 跨越桌面壁垒，当前线程挂接至 WinSta0\Default 主交互桌面 ]
        │
        ▼ 2. CreateProcessW(lpDesktop="WinSta0\\Default", cmd="chrome.exe <url>")
  [ 在主交互桌面精准唤起 Chrome 实例并直达 .user.js 路由 ]
        │
        ▼ 3. keybd_event(VK_MENU / Alt) + AttachThreadInput
  [ 模拟按下 Alt 键击穿 Windows LockSetForegroundWindow 焦点锁，挂接输入队列 ]
        │
        ▼ 4. ShowWindow(SW_RESTORE) + SetForegroundWindow + BringWindowToTop
  [ 强制将 Chrome 窗口恢复/置顶于屏幕最前方，Tampermonkey 自动拦截呈现安装页 ]
```

---

## 三、 本地 HTTP 网关与 Tampermonkey 拦截协议

1. **URL 路由必须严格以 `.user.js` 结尾**：
   - 标准路径：`http://127.0.0.1:8790/argon_commander.user.js`
   - 油猴后台监听 `*://*/*.user.js` 导航事件，截获并跳转至扩展内置安装页面。
2. **标准响应头规范**：
   ```http
   HTTP/1.1 200 OK
   Content-Type: text/javascript; charset=utf-8
   Content-Length: <文件字节数>
   Access-Control-Allow-Origin: *
   Cache-Control: no-cache, no-store, must-revalidate
   ```
3. **前置守护自愈机制**：
   - `open_userscript_install.py` 内部在唤起 Chrome 前，先探测 `http://127.0.0.1:8790/api/status`；若网关未运行，自动在后台拉起 `start_bridge.bat` 或 `bridge_server.py`，确认健康后再通知 Chrome 访问，杜绝连接拒绝报错。

---

## 四、 唯一标准执行规范 (SOP)

凡是需要安装或更新油猴脚本（包括但不限于 `argon_commander.user.js`），智能体**严禁使用任何 `Start-Process`、`cmd /c start` 或临时脚本**，必须执行以下标准工具：

### 1. 唯一标准执行命令
```powershell
# 执行 AFL 仓库或工程目录下的穿透安装器
python <工程目录>/src/open_userscript_install.py
```
如需安装指定 URL 的油猴脚本：
```powershell
python <工程目录>/src/open_userscript_install.py "http://127.0.0.1:8790/your_script.user.js"
```

### 2. 标准人机协同交互话术
脚本执行成功后，Chrome 已在前台置顶弹出油猴安装页。智能体向主君汇报时，必须遵循纯叙事温声播报规范：
> “已为公子在主屏幕置顶唤起 Chrome 浏览器的油猴脚本安装页面。请公子移步浏览器，在页面中央点击绿色的【Install】（安装）或【Update】（更新）按键，即可完成最新版本脚本的部署。”

### 3. 安装后闭环验证
当主君完成点击并刷新 AI Studio 页面后，运行握手验证脚本核实心跳：
```powershell
python <工程目录>/src/check_handshake.py
```
确认输出中 AI Studio 油猴脚本心跳在线（ONLINE），即证明部署圆满闭环。

---

## 五、 排障与异常自愈指南 (Troubleshooting)

| 异常现象 | 物理根因 | 自愈与解决对策 |
| :--- | :--- | :--- |
| **Chrome 未弹出或无反应** | 系统未安装 Chrome 或未在默认路径 | 检查 Chrome 二进制路径，支持常见安装目录及注册表自动探测。 |
| **打开了 Edge 而非 Chrome** | 错误地使用了系统原生关联打开 | 强制调用 `open_userscript_install.py`，其内部显式检索 `chrome.exe` 二进制路径启动。 |
| **Chrome 仅在任务栏闪烁** | Win32 焦点锁阻止后台应用抢夺焦点 | 脚本内部已集成 `VK_MENU` 击穿与 `AttachThreadInput` 挂接；可再次运行一次置顶。 |
| **浏览器显示代码源码而非安装页** | 目标 URL 未以 `.user.js` 结尾，或 Content-Type 不对 | 确保 URL 为 `http://127.0.0.1:8790/argon_commander.user.js`，网关正确下发 `text/javascript; charset=utf-8`。 |
| **浏览器报连接被拒绝 (ERR_CONNECTION_REFUSED)** | 本地网关 (8790 端口) 未启动 | `open_userscript_install.py` 会自动后台启动网关；如遇占用，检查端口 `netstat -ano \| findstr :8790`。 |
| **油猴扩展未拦截** | Chrome 未启用 Tampermonkey 扩展或未开启“开发者模式” | 检查 Chrome 扩展页面 `chrome://extensions`，确保 Tampermonkey 处于启用状态，并勾选“允许访问文件网址”与“开发者模式”。 |
