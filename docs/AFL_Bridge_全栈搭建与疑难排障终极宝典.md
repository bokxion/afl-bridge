# 🏛️ AFL Bridge 全栈搭建与疑难排障终极宝典 (v6.1.0 工业级权威正本)

> **当前版本**：v6.1.0 终极正本 (Single-Shot Physical Click & Off-Screen Deep Water Edition)  
> **核心使命**：实现 Google AI Studio（云端统帅 Argon）与 本地 Antigravity 终端（Flash 执行官）之间的 100% 全后台无感、零延迟、跨桌面隔离的双向自主协同通信。  
> **适用环境**：Windows 10 / Windows 11 / Google Chrome / Tampermonkey / Python 3.10+ / Antigravity

---

## 目录
1. [系统总体物理架构拓扑](#一-系统总体物理架构拓扑)
2. [微观物理根因与架构演进断代史](#二-微观物理根因与架构演进断代史)
3. [单次确定性点火引擎：50ms 状态机与 250ms 防抖破局法则](#三-单次确定性点火引擎50ms-状态机与-250ms-防抖破局法则)
4. [全后台无感通信：第二桌面展开与 -32000 离屏深水区调度](#四-全后台无感通信第二桌面展开与--32000-离屏深水区调度)
5. [下行回传闭环：compareDocumentPosition 思考缝合与 EOF ACK 直通](#五-下行回传闭环comparedocumentposition-思考缝合与-eof-ack-直通)
6. [核心组件与物理文件基石](#六-核心组件与物理文件基石)
7. [跨桌面沙盒穿透与油猴部署 SOP](#七-跨桌面沙盒穿透与油猴部署-sop)
8. [终极疑难排障与自愈矩阵 (Troubleshooting Matrix)](#八-终极疑难排障与自愈矩阵-troubleshooting-matrix)

---

## 一、 系统总体物理架构拓扑

AFL (Argon-Flash Link) 体系采用三层三权分立的工业级拓扑设计，旨在彻底终结人工复制粘贴、手动拖拽与盲目掐表等待，实现云端高维统帅与本地工程执行官之间的无缝协同：

```
+--------------------------------------------------------------------------+
|                  云端统帅中枢 (Google AI Studio)                          |
|             https://aistudio.google.com/prompts/[专属星宿会话]            |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |          油猴常驻脚本 (argon_commander.user.js v6.1.0)           |   |
|   |  - GM_xmlhttpRequest 特权脉冲：击穿 Chromium 后台深度挂起与节流   |   |
|   |  - 纯内存 DOM 探针：零重排 textContent，杜绝页面卡顿与失焦        |   |
|   |  - 50ms 状态机精准防吞点火：单次原子物理点击，杜绝连续盲发重发   |   |
|   |  - 思考全量缝合：compareDocumentPosition 跨块拓扑排序，杜绝丢字  |   |
|   |  - 终极闭环信标：<!-- [AFL_EOF_ACK] --> 绝对行尾拦截与极速回传    |   |
|   +------------------------------------------------------------------+   |
+-----------------------------------^--|-----------------------------------+
                                    |  | (HTTP Keep-Alive 脉冲 / ACK / Dispatch)
                                    |  v
+--------------------------------------------------------------------------+
|                      本地守护中继 (Bridge Server)                         |
|                 http://127.0.0.1:8790 (src/bridge_server.py)             |
|                                                                          |
|   - 独占 Ticket 插槽管理 (Pending -> Dispatched -> Captured)             |
|   - 网关微秒级原子取件锁 (单标签页命中立即锁定，彻底杜绝并发抢单)       |
|   - 原生长轮询阻塞队列 (挂起等待直到 AI 回传或超时，零轮询空耗)          |
|   - 1-to-1 多会话单播定向路由与心跳拓扑校验 (--target-title)             |
|   - 附件与超长工程源码纯内存 Markdown 内联自动流转                       |
+-----------------------------------^--|-----------------------------------+
                                    |  | (原生 Reactive Wakeup 阻塞发件与结果捕获)
                                    |  v
+--------------------------------------------------------------------------+
|                   本地终端案前特遣 (Antigravity IDE / DSH)               |
|                                                                          |
|   - send_to_argon.py --wait 阻塞挂起与唤醒                               |
|   - 双模输出闭环 (<=2500 字符 stdout 直出，>2500 字符落盘秒读)           |
|   - background_window.py 离屏深水区调度 (-32000, -32000) 与防休眠启航   |
|   - Flash 3.8 High 案前实操：原子级改码、编译校验与高信噪比战报呈回       |
+--------------------------------------------------------------------------+
```

---

## 二、 微观物理根因与架构演进断代史

从早期脚本到 v6.1.0 权威正本的演进过程中，AFL 体系历经了五大关键物理病灶的勘查与彻底根治：

### 1. 顶部系统提示词框误寻址（幽灵发信）
* **物理成因**：为支持全后台运行而移除 `offsetParent !== null` 可见性过滤后，`document.querySelector('ms-autosize-textarea textarea')` 误抓了排在 DOM 首部折叠隐藏的 `ms-system-instructions`（系统指令框）。
* **致命现象**：咨询胶囊被填入顶部系统指令栏，底部真实聊天框空空如也，Run 键无反应。
* **终极破局**：严格限定底部包装器 `ms-prompt-input-wrapper textarea`；显式排除祖先容器包含 `ms-system-instructions`、`ms-prompt-header`、`header`、`ms-prompt-title` 的元素。

### 2. 跨沙盒原生 Setter 裸奔抛错（Illegal invocation）
* **物理成因**：在 Tampermonkey 双沙盒下直接调用原型赋值器 `prototypeValueSetter.call(element, value)`，因 Receiver 与 Prototype 跨越沙盒上下文失配而抛出类型错误。
* **终极破局**：构建 `candidateProtos` 级联多层原型回退遍历（`Object.getPrototypeOf` -> `pageWindow` -> `window`），辅以全域 `try...catch` 与 Chromium 原生 `execCommand('insertText')`。

### 3. 右侧设置栏误判与永恒生成状态（Add stop sequence 陷阱）
* **物理成因**：AI Studio 右侧高级参数栏展开后常驻一个按钮名为 **"Add stop sequence"**。旧脚本扫描全页 `button` 且包含 `stop` 字符串，导致误以为页面永远在生成中，发件逻辑自我短路。
* **终极破局**：绝缘按键寻址，严格锁定右下角 `ms-run-button button.run-button`；停止态识别唯认类名 `.stoppable` 或显式属性 `aria-label === 'stop'`。

### 4. 盲目重投与连续扫射导致的“双发撕裂”（v6.0 关键尸检突破）
* **物理成因**：
  - 旧版架构采用“15次×150ms 闭环连击”或“300ms else triggerRun”，试图解决按钮 disabled 问题；
  - 但大文本注入后，Angular Zone.js 微任务与 Tokenizer 词元计数耗时 400ms~800ms，300ms 盲目超时掐表必然导致误判进入 else 触发第二次点火；
  - 加上网关未在 Poll 时原子上锁，导致同一任务被重复下发、同一提示词在前端被点击两次，引发生成流被打断并在正文中穿插分裂出多个思考条（Thinking Bar）。
* **终极破局**：
  - 网关轮询首次命中微秒级加锁 `ready_for_aistudio = False`；
  - 彻底拔除连续扫射与 300ms 盲发，升级为 **50ms 状态机精准防吞点火与单次确定性原子物理点击 (Single-Shot Physical Click & 250ms Anti-Debounce)**。

### 5. Windows 最小化（SW_MINIMIZE）导致的渲染与事件冻结
* **物理成因**：Windows DWM 在窗口最小化时会立即停止 GPU 视口绘制并剥离渲染表面，Chromium 内核触发 `kFrozen` 生命周期挂起，导致 JavaScript 定时器与 Angular 脏检查彻底停摆。
* **终极破局**：废黜窗口最小化，确立 **“第二虚拟桌面常驻展开”** 与 **“background_window.py 坐标离屏深水区 (-32000, -32000)”** 双重无感调度方案。

---

## 三、 单次确定性点火引擎：50ms 状态机与 250ms 防抖破局法则

在 v6.1.0 中，输入注入与点火流程由一套高度精密的原子状态机驱动：

```
[ 网关分配 Ticket ]
       │
       ▼ (特权 IPC 脉冲拉取)
[ 文本双擎注入 (execCommand + Safe Setter) ]
       │
       ▼
[ 状态机每 50ms 轮询侦测 (最多持续 1200ms) ]
       │
   ┌───┴────────────────────────┐
   ▼                            ▼
[ 检测到 disabled 属性剥离 ]   [ 超时 300ms 仍未解锁 ]
   │                            │
   │                            ▼ (DOM API 强制强行剥离 disabled)
   └───────────┬────────────────┘
               ▼
   [ 微秒级执行单次物理原子点击 dispatchPhysicalClick ]
               │
               ▼
   [ 立即将点火状态机锁定为 FIRE_DONE，开启 250ms 防抖 ]
               │
               ▼
   [ 彻底杜绝二次盲发，平稳步入流式生成监听 ]
```

关键实现原则：
1. **单次敲击收敛**：每一次任务投递，在生命周期内**有且仅有一次物理点击事件**；
2. **Tokenizer 状态对齐**：监听前端框架真实解析状态，在其就绪微秒瞬间击发；
3. **网关原子排重**：网关在遍历候选列表时，匹配中立即标记消费状态，阻断任何多标签页并发竞争。

---

## 四、 全后台无感通信：第二桌面展开与 -32000 离屏深水区调度

为了实现“既不打扰主君当前桌面操作，又绝不让 Chrome 触发内核休眠冻结”的极致体验，v6.1.0 提供两种经过严苛验证的窗口调度方案：

### 方案 A：Windows 第二虚拟桌面常驻法（推荐日常伴读）
1. 在 Windows 11 中按下 `Win + Tab`，新建一个“桌面 2”；
2. 将用于协同的 Chrome 浏览器窗口拖至“桌面 2”并保持正常窗口大小展开（切勿点击最小化）；
3. 主君在“桌面 1”进行正常的编码与办公，底层 DWM 维持两个桌面的完整渲染管线，AFL 在后台畅通无阻。

### 方案 B：坐标离屏深水区调度法（`src/background_window.py`）
借助 `src/background_window.py` 提供的 Win32 调度器，将专用窗口在展开状态下平移至虚拟显示坐标之外：
```powershell
# 1. 探查当前 Chrome 窗口状态
python src/background_window.py --status

# 2. 将目标专席窗口沉入深水区 (-32000, -32000)
python src/background_window.py --offscreen --target-title "统帅"

# 3. 需要时随时唤回至主屏幕可见区域 (100, 100)
python src/background_window.py --restore --target-title "统帅"
```
* **防串扰红线保护**：若检测到当前窗口包含主君正在浏览的其他标签页（如包含远程桌面、多标签页），脚本严格拒绝搬移，避免干扰主君日常工作。

---

## 五、 下行回传闭环：compareDocumentPosition 思考缝合与 EOF ACK 直通

针对 Gemini 4 等具有交织思考（Interleaved Thinking）特性的模型，v6.1.0 在回传端构筑了两道钢规：

### 1. `compareDocumentPosition` 跨块 DOM 全量缝合
* 大模型单轮回复经常被拆分成思考块（`ms-thought-chunk`）、正文块（`ms-text-chunk`）、代码块（`ms-code-chunk`）交错渲染；
* 脚本采用原生 DOM 树拓扑位置算法，精确比对位于当前轮次最新 User Prompt 之后的所有有效 Model 块；
* 剥离思考容器与错误容器，按文档流物理先后顺序将正文全量缝合拼接，杜绝任何断章、丢字或只取末尾块的事故。

### 2. 行尾绝对锚定信标直通车 (`[AFL_EOF_ACK]`)
* 正则表达式严格锚定行尾：
  ```javascript
  const EOF_TAIL_REGEX = new RegExp('\\[AFL_EOF_' + 'ACK\\]\\s*(?:-->)?\\s*`{0,3}\\s*$');
  ```
* 唯有当信标出现在全篇回复的绝对末尾时，立即短路跳过 2.2 秒静默倒计时，毫秒级回传网关；
* 正文中若有对信标的代码引用或讨论，因未处于末行而被安全放行；回传前自动剥离信标，确保归档文本绝对纯净。

---

## 六、 核心组件与物理文件基石

```
afl-bridge/
├── README.md                           # 顶层架构与极速上手指南 (v6.1.0)
├── sync_from_live.py                   # 宿主工作区与 Git 仓库双向同步工具
├── docs/                               # 深度技术文档
│   ├── AFL_Bridge_全栈搭建与疑难排障终极宝典.md # 本宝典正本 (v6.1.0)
│   └── capsule_netroom_dedup_autopsy.md         # 双发与思考条分裂微观尸检报告
├── src/                                # 核心运行时组件
│   ├── bridge_server.py                # 本地 8790 端口中继守护网关
│   ├── send_to_argon.py                # 阻塞投递与长轮询挂起脚本
│   ├── check_handshake.py              # 全链路三方握手与便携会话绑定
│   ├── open_userscript_install.py      # Win32 沙盒穿透油猴安装器
│   ├── background_window.py            # 深水离屏 (-32000) 窗口调度器
│   ├── argon_commander.user.js         # v6.1.0 生产级油猴中继脚本
│   ├── start_bridge.bat                # 网关一键脱壳启动批处理
│   └── launch_afl_chrome.bat           # Chrome 防休眠专用参数启动器
└── skills/                             # Antigravity 智能体专属法典
    ├── aistudio/                       # AFL 自动化发件与双端协同权威技能大正本
    ├── argon-flash-commander/          # Argon 统帅 vs Flash 执行官双层节流规范
    └── tampermonkey-installer/         # 油猴脚本跨桌面沙盒穿透安装标准技能
```

---

## 七、 跨桌面沙盒穿透与油猴部署 SOP

当新电脑初次部署或油猴脚本升级至 v6.1.0 时，智能体**严禁使用任何 `Start-Process` 或普通系统关联调用**，必须执行专用 Win32 穿透器：

```powershell
python src/open_userscript_install.py
```

### 底层穿透四部曲：
1. `OpenDesktopW("Default")` + `SetThreadDesktop`：将执行线程切入用户交互桌面；
2. `STARTUPINFO.lpDesktop = "WinSta0\\Default"`：强制在主屏幕生成 Chrome 进程；
3. `keybd_event(VK_MENU, ...)` + `AttachThreadInput`：击穿 Windows 前台焦点锁；
4. `ShowWindow(SW_RESTORE)` + `SetForegroundWindow`：将 Chrome 窗口置顶呈现。

主君移步至弹出的 Chrome 页面，轻点中央绿色的 **Install** 或 **Update** 按键，刷新 AI Studio 页面，即可见右下角亮起翠绿色的 `⚡ AFL v6.1.0 智能路由` 浮窗。

---

## 八、 终极疑难排障与自愈矩阵 (Troubleshooting Matrix)

| 异常现象 | 物理根因分析 | 唯一权威对策 |
| :--- | :--- | :--- |
| **8790 端口连接被拒绝 (Connection Refused)** | `bridge_server.py` 未启动或进程异常退出 | 运行 `python src/check_handshake.py`（内部会自动后台拉起），或手动运行 `src/start_bridge.bat`。 |
| **三方巡检显示 AI Studio 标签页未找到** | Chrome 未打开 AI Studio，或页面标题与配置不匹配 | 打开 AI Studio 页面；核验左上角会话标题与 `.aistudio_config.json` 中的 `target_title` 是否一致。 |
| **发送时文字被填入顶部系统提示词栏** | DOM 选择器抓中折叠的 `ms-system-instructions` | 确保使用的是 v6.1.0 脚本，已部署祖先容器过滤与底部包装器强约束。 |
| **同一条消息被发送两次，思考条在正文中穿插** | 旧版脚本 15x150ms 连击或 300ms 盲发触发二次点击 | 升级至 v6.1.0 脚本，已收敛为 50ms 状态机单次物理原子点击并配合网关原子锁。 |
| **长篇回复或文学正文前半部分被截断** | 模型交织思考分裂多 DOM 容器，旧提取器误抓末尾块 | v6.1.0 已集成 `compareDocumentPosition` 穿透算法，全量缝合最新 User 后的全部正文。 |
| **后台运行一段时间后不再接收新任务** | Chrome 窗口被最小化，DWM 剥离渲染导致内核休眠 | 坚决禁止最小化；使用第二虚拟桌面常驻展开，或运行 `python src/background_window.py --offscreen`。 |
| **发信命令瞬间退出且未等待回复** | 误加了 `--no-wait` 参数跳过了长轮询 | 必须使用 `python src/send_to_argon.py --file <胶囊> --wait` 发起长轮询阻塞等待。 |
