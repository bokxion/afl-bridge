# 🏛️ AFL Bridge 全栈搭建与疑难排障终极宝典 (v5.8.0)

> **版本**：v5.8.0 闭环防误判终极版  
> **核心使命**：实现 Google AI Studio（云端统帅 Argon）与 本地 Antigravity 终端之间的 100% 全后台无感、零延迟、跨桌面隔离的双向自主协同通信。  
> **适用环境**：Windows 11 / Chrome / Tampermonkey / Python 3.10+ / Antigravity

---

## 目录
1. [系统总体物理架构拓扑](#一-系统总体物理架构拓扑)
2. [微观尸检：五大上行排异反应与 v5.8.0 终极破局法则](#二-微观尸检五大上行排异反应与-v580-终极破局法则)
3. [闭环点火引擎：15次×150ms 真实清空上屏保障机制](#三-闭环点火引擎15次150ms-真实清空上屏保障机制)
4. [下行心跳与信标：全后台特权时钟与防早泄铁闸](#四-下行心跳与信标全后台特权时钟与防早泄铁闸)
5. [核心代码基石与接口清单](#五-核心代码基石与接口清单)
6. [跨桌面沙盒穿透与油猴部署 SOP](#六-跨桌面沙盒穿透与油猴部署-sop)
7. [终极疑难排障矩阵 (Troubleshooting Matrix)](#七-终极疑难排障矩阵-troubleshooting-matrix)

---

## 一、 系统总体物理架构拓扑

AFL (Argon-Flash Link) 体系采用三层三权分立的工业级拓扑设计：

```
+--------------------------------------------------------------------------+
|                        云端统帅 (Google AI Studio)                       |
|               https://aistudio.google.com/prompts/[专属会话]              |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |         油猴常驻脚本 (argon_commander.user.js v5.8.0)            |   |
|   |  - 扩展特权脉冲 (GM_xmlhttpRequest) 击穿 Chromium 后台深度节流   |   |
|   |  - 纯内存 DOM 探针 (零重排 textContent，绝不调用 innerText)      |   |
|   |  - 底部输入框精准寻址 (排除顶部 System Prompt 与标题栏)          |   |
|   |  - 双擎填字 (Chromium execCommand + 跨沙盒安全 Setter)           |   |
|   |  - 绝缘 Run 按键寻址 (禁扫全页 Button，杜绝 Add stop sequence)   |   |
|   |  - 15次×150ms 闭环连击 (以输入框清空上屏为唯一自停判据)         |   |
|   |  - 单调递增回合守卫 + 行尾绝对锚定 EOF ACK 拦截器               |   |
|   +------------------------------------------------------------------+   |
+-----------------------------------^--|-----------------------------------+
                                    |  | (HTTP Keep-Alive 脉冲 / ACK / Dispatch)
                                    |  v
+--------------------------------------------------------------------------+
|                        本地守护中继 (Bridge Server)                       |
|                 http://127.0.0.1:8790 (bridge_server.py)                 |
|                                                                          |
|   - 维护独占 Ticket 插槽 (Pending -> Dispatched -> Captured)             |
|   - 原生长轮询阻塞队列 (挂起等待直到 AI 回传或超时)                     |
|   - 附件与工程文件 Base64 自动分发与暂存                                 |
+-----------------------------------^--|-----------------------------------+
                                    |  |
                                    |  v (Subprocess 长轮询 / Exit 0 唤醒)
+--------------------------------------------------------------------------+
|                     本地执行端 (Antigravity Terminal)                     |
|                                                                          |
|   - 发令脚本：send_to_argon.py --file <胶囊路径> --wait                  |
|   - 握手巡检：check_handshake.py (网关/CDP/油猴三位一体核验)             |
|   - 响应式苏醒：Reactive Wakeup 自我唤醒 (<=2500 stdout, >2500 落盘)     |
|   - 穿透安装：open_userscript_install.py (Win32 API 跨桌面置顶)           |
+--------------------------------------------------------------------------+
```

---

## 二、 微观尸检：五大上行排异反应与 v5.8.0 终极破局法则

在探索浏览器全后台最小化（`SW_MINIMIZE`）无感发信与极端界面状态的过程中，隔壁净室项目与 AFL 系统的实机大考共同揭开了五大隐秘病灶的物理成因：

### 1. 排异一：顶部系统提示词框误寻址（幽灵发信）

* **物理成因**：为了支持最小化移除了 `offsetParent !== null`，导致 `document.querySelector('ms-autosize-textarea textarea')` 失去了可见性过滤，精准抓中了排在 DOM 首部折叠隐藏的 `ms-system-instructions`（系统指令框）。
* **致命现象**：咨询胶囊被填入顶部系统提示词栏，底部真实聊天框空空如也，Run 键无反应，手机端刷新不见任何新消息。
* **破局法则**：
  - 祖先容器阻断：严禁命中包含 `ms-system-instructions`、`ms-prompt-header`、`header`、`ms-prompt-title` 的元素；
  - 语义属性过滤：排除 `aria-label` / `placeholder` 包含 `system`、`instruction`、`title` 的输入框；
  - 优先锁定底部包装器 `ms-prompt-input-wrapper textarea`，回退时取 DOM 序末位聊天框。

### 2. 排异二：跨沙盒 原生 Setter 裸奔抛 `TypeError: Illegal invocation`

* **物理成因**：在 `@grant unsafeWindow` 双沙盒下直接调用原型赋值器 `prototypeValueSetter.call(element, value)`，因 Receiver 与 Prototype 跨越沙盒上下文失配而抛出类型错误，且外层缺少 `try...catch` 保护。
* **致命现象**：JavaScript 执行流瞬间崩溃，紧随其后的 `triggerRun()` 根本来不及执行。
* **破局法则**：
  - 构建 `candidateProtos` 级联多层原型回退遍历（`Object.getPrototypeOf` -> `pageWindow` -> `window`）；
  - 全域 `try...catch` 包裹，绝不让跨界异常穿透；
  - 辅以 Chromium C++ 级 `execCommand('insertText')` 原生触发表单校验。

### 3. 排异三：0ms 同步点击遭 Angular `runBtn.disabled` 锁阻断

* **物理成因**：填入文本同一毫秒内，Angular Zone.js 微任务表单校验尚未执行完毕，`runBtn.disabled` 依然保持 `true`。旧代码 `if (!isDisabled) runBtn.click();` 恒定被跳过。
* **致命现象**：HUD 抢跑显示 `THINKING`，但实际物理点击被 `disabled` 属性死死挡住，未向后端发出网络请求。
* **破局法则**：
  - 撬锁瞬发：0ms 点击前强行剥离 `runBtn.disabled = false` 与 `mat-mdc-button-disabled` 样式；
  - 配合 15次×150ms 闭环补点，确保 Zone.js 消化微任务后完成彻底击发。

### 4. 排异四：全页面扫描 Button 误中右侧设置栏 `Add stop sequence` 陷阱（v5.8.0 关键突破）

* **物理成因**：
  - 在 Google AI Studio 右侧的高级参数栏（Run Settings）中，展开后常驻一个按钮名为 **"Add stop sequence"**（添加停止序列）；
  - 旧版 `findRunButton` 与 `isRunButtonInStopState` 使用 `document.querySelectorAll('button')` 并在全页范围匹配 `text.includes('stop')`；
  - 一旦用户或页面展开了右侧参数栏，该全页面扫描立刻抓中 `Add stop sequence` 按钮！
* **双重短路灾难**：
  - `checkAiStudioGenerating()` 判定存在包含 `stop` 的按钮，导致其 **24 小时恒定返回 `true`（误以为永远在生成）**；
  - `triggerRun()` 在第 1 行执行 `if (checkAiStudioGenerating()) return;`，直接被自我短路拦截，填完文字后拒绝点击发送！
  - `pollForConsultations()` 轮询接单逻辑同样因为检测到“正在生成”而拒绝接收 Antigravity 派发的新胶囊！
* **破局法则**：
  - **绝缘 Run 按键寻址**：严禁使用 `querySelectorAll('button')` 扫描全页面普通按钮！严格锁定右下角 `ms-run-button button`：
    ```javascript
    function findRunButton() {
        return document.querySelector(
            "ms-run-button button.run-button, ms-run-button button[type='submit'], ms-run-button button, button.run-button"
        );
    }
    ```
  - **精准停止态识别**：唯认 AI Studio 原生类名 `.stoppable` 或明确的 `aria-label === 'stop'`，严禁使用盲目的 `textContent.includes('stop')`。

### 5. 排异五：隐藏子节点文字污染（v5.8.0 关键突破）

* **物理成因**：
  - 即使仅扫描 `ms-run-button button`，由于使用了 `textContent`，按钮内部未激活的隐藏子图标名字（例如 `<mat-icon>stop_circle</mat-icon>`）也会被读入文本中；
  - 若代码直接判断 `btn.textContent.includes('stop')`，在正常等待状态下也会被误判为停止状态。
* **破局法则**：
  ```javascript
  function isRunButtonInStopState(btn) {
      const runBtn = btn || findRunButton();
      if (!runBtn || runBtn.disabled) return false;
      // 唯认 AI Studio 生成态专属类名 stoppable 或明确的 aria-label
      if (runBtn.classList.contains('stoppable')) return true;
      const aria = (runBtn.getAttribute('aria-label') || '').trim().toLowerCase();
      if (aria === 'stop' || aria.startsWith('stop ') || aria.includes('停止')) return true;
      return false;
  }
  ```

---

## 三、 闭环点火引擎：15次×150ms 真实清空上屏保障机制

在 v5.8.0 中，`triggerRun` 彻底拔除了 `checkAiStudioGenerating()` 的前置短路，改为闭环递归验证引擎：

```javascript
function triggerRun(textarea, attempt = 0) {
    if (!isBridgeActive || !isCommanderTab() || attempt > 15) return false;
    try { pumpMainWorldVirtualFrames(); } catch (e) {}

    const activeArea = textarea || findInputTextarea();
    const currentInputVal = activeArea ? (activeArea.value || activeArea.textContent || '').trim() : '';
    const runBtn = findRunButton();

    // 唯一停止重试判据：当 attempt > 0 时，输入框已被清空上屏，或者 Run 按钮已挂上 stoppable 类名进入停止态
    if (attempt > 0 && (currentInputVal.length === 0 || isRunButtonInStopState(runBtn))) {
        generationPhase = 'PHASE1_GENERATING';
        isGenerating = true;
        quietCountdownStart = 0;
        updateHUDStatus();
        return true;
    }

    // 若文字仍在框内，再次派发 input 事件唤醒 Angular 按钮解禁
    if (attempt >= 1 && activeArea) {
        try {
            const Evt = pageWindow.Event || window.Event;
            activeArea.dispatchEvent(new Evt('input', { bubbles: true, composed: true }));
            pumpMainWorldVirtualFrames();
        } catch (e) {}
    }

    if (runBtn && !isRunButtonInStopState(runBtn)) {
        try {
            // 强行摘除 disabled 锁并触发完整鼠标点击事件链 (mousedown -> mouseup -> click)
            runBtn.disabled = false;
            runBtn.removeAttribute('disabled');
            runBtn.removeAttribute('aria-disabled');
            runBtn.classList.remove('mat-mdc-button-disabled');
            const MEvent = pageWindow.MouseEvent || window.MouseEvent;
            runBtn.dispatchEvent(new MEvent('mousedown', { bubbles: true, cancelable: true }));
            runBtn.dispatchEvent(new MEvent('mouseup', { bubbles: true, cancelable: true }));
            lastAttemptTimestamp = Date.now();
            runBtn.click();
        } catch (e) {}
    }

    // 双重保险：从第 1 次补点起，同步向输入框派发 Ctrl+Enter 快捷键
    if (attempt >= 1 && activeArea) {
        try {
            activeArea.focus();
            const KEvent = pageWindow.KeyboardEvent || window.KeyboardEvent;
            activeArea.dispatchEvent(new KEvent('keydown', {
                key: 'Enter', code: 'Enter', keyCode: 13, which: 13, ctrlKey: true, bubbles: true, cancelable: true
            }));
        } catch (e) {}
    }

    try { pumpMainWorldVirtualFrames(); } catch (e) {}
    setTimeout(() => triggerRun(activeArea, attempt + 1), 150);
    return true;
}
```

---

## 四、 下行心跳与信标：全后台特权时钟与防早泄铁闸

1. **特权扩展脉冲引擎 (GM_xmlhttpRequest Clock)**：油猴扩展后台进程不受标签页后台深度降频限制，维持永不降频的高精度时钟。
2. **回合单调递增守卫 (Turn-Count Monotonic Guard)**：记录基线模型回合数量 `AFL_BASELINE_MODEL_COUNT`，模型回答块数量必须达到 `baseline + 1` 方可捕获。
3. **行尾绝对锚定正则 (`AFL_EOF_ACK_REGEX`)**：
   ```javascript
   const AFL_EOF_ACK_REGEX = new RegExp('\\[' + 'AFL_EOF_' + 'ACK\\]\\s*(?:-->)?\\s*$');
   ```
   杜绝正文中引述信标引发的提早截断回传。

---

## 五、 核心代码基石与接口清单

* 本地网关：`http://127.0.0.1:8790` (`bridge_server.py`)
* 发信与等待：`python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <胶囊> --wait`
* 握手巡检：`python d:\maid-coding-space\argon_anti_bridge\check_handshake.py`
* 穿透安装：`python d:\maid-coding-space\argon_anti_bridge\open_userscript_install.py`

---

## 六、 跨桌面沙盒穿透与油猴部署 SOP

运行命令：
```bash
python d:\maid-coding-space\argon_anti_bridge\open_userscript_install.py
```
通过 Win32 API 切换 `WinSta0\Default` 桌面，调用 `keybd_event(VK_MENU)` + `AttachThreadInput` 击穿 Windows 前台焦点锁，置顶唤起 Chrome 访问 `http://127.0.0.1:8790/argon_commander.user.js`，点击页面中央绿色【Install / Update】按键即可秒级完成部署。

---

## 七、 终极疑难排障矩阵 (Troubleshooting Matrix)

| 故障现象 | 微观物理根因 | 终极破局对策 |
| :--- | :--- | :--- |
| **右侧设置栏展开后脚本彻底瘫痪** | 误把右侧参数栏 `Add stop sequence` 当成 Stop 按钮 | 升级 v5.8.0，只锁定 `ms-run-button button`，认准 `.stoppable` |
| **填完文字后拒绝点击发送** | `checkAiStudioGenerating` 误判为 true，短路了 `triggerRun` | 升级 v5.8.0，拔除前置短路，以“输入框清空上屏”为唯一判据 |
| **手机上看未发出，聊天框空白** | `findInputTextarea` 命中顶部折叠的系统提示词框 | 升级 v5.7.0+，使用包含祖先排除与末位过滤的精准寻址 |
| **控制台报错 `Illegal invocation`** | `@grant unsafeWindow` 跨沙盒原型 Setter Receiver 失配 | `candidateProtos` 级联回退遍历，全 try-catch 包裹 |
| **0ms 点击失效，显示 THINKING 却未发** | Angular Zone.js 未消化微任务，`runBtn.disabled` 挡回点击 | 强行剥离 disabled 属性，15次×150ms 闭环连击 |
| **引述信标导致回复被截断早泄** | 使用了模糊 `includes('[AFL_EOF_ACK]')` 匹配 | 采用严格行尾锚定正则 `AFL_EOF_ACK_REGEX` |
| **窗口最小化时 16 分钟无响应** | Chromium 深度降频导致 DOMTimer 冻结 | 启用基于 `GM_xmlhttpRequest` 的扩展级特权脉冲引擎 |
| **调用安装脚本但在前台看不见窗口** | 后台会话隔离于独立 Desktop，或受焦点锁拦截 | 使用 `open_userscript_install.py` 执行 Win32 API 穿透置顶 |

---
*宝典升级至 v5.8.0，扫除全域隐患，闭环大成。*
