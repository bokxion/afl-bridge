# 🏛️ AFL Bridge (Argon-Flash Link) v6.1.0 权威正本

> **Google AI Studio 云端统帅 (Argon) 与 Antigravity 本地特遣官 (Flash) 全后台自适应跨架构协同通信中继**
> 
> *“深水不响，云汉为章；高维裁决，案前落地。”*

---

## 📖 架构概览 (Architecture Overview)

**AFL (Argon-Flash Link)** 是一套专为突破大模型上下文与配额瓶颈而设计的**分层协同与跨端自主通讯架构**。

它在 Google AI Studio（拥有百万级上下文与极致推理深度的 **Gemini 4 Argon / Pro** 统帅）与 本地开发环境（**Google Antigravity / Gemini 3.8 Flash High** 执行官）之间建立了一条**100% 全后台无感、零焦点依赖、跨桌面沙盒穿透的双向自主管道**。

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

## ⚡ 核心设计哲学与六大工业级韧性准则

### 1. 三权分立协同范式 (Tripartite Synergy)
- **主君 (The Supreme Sovereign)**：最高意志源泉与战略方向仲裁者；
- **Argon 统帅 (Chief System Architect)**：坐镇 Google AI Studio 高维中枢，洞察系统根因，推演状态机完备性，裁决顶层拓扑，下达生产级源码指令；
- **Flash 执行官 (Engineering Executor)**：案前雷霆手足，勘查现场、打包咨询胶囊、精准改动本地文件流与终端验证，释放统帅 90% 以上体力工程消耗。

### 2. 原生 Reactive Wakeup 响应式唤醒
摒弃低效脆弱的死循环轮询，`send_to_argon.py --wait` 在本地挂起长轮询专属 Ticket。统帅推演完成回传瞬间，子进程 `sys.exit(0)` 退出，触发 Antigravity 宿主内核原生 Reactive Wakeup 自动苏醒。

### 3. 50ms 状态机精准防吞点火与单次确定性原子击发 (Single-Shot Physical Click)
彻底根除旧架构连续扫射或盲目重投（`300ms else triggerRun`）引爆的消息双发与思考条（Thinking Bar）穿插分裂。收敛为每 50ms 侦测 Angular Tokenizer 解锁后微秒级单次物理原子点击，配合 250ms 防抖流控与网关微秒级单次取件原子锁，在前端与网关构筑双保险。

### 4. 交织思考跨块 DOM 全量缝合 (compareDocumentPosition Splicing)
针对现代模型交织思考特性，借助原生 DOM `compareDocumentPosition` 节点拓扑比对算法，严格收集最新 User Prompt 后的所有正文块，深度剥离思考胶囊与报错容器，杜绝长文与正文断章、丢字。

### 5. 内存纯文本内联抗脆弱性 (In-Memory Text Inlining)
彻底废弃模拟伪造文件上传，推行内存纯文本内联。万字文本切片与多工程源码在案前内存中编织为结构清晰的 Markdown 胶囊直接打入输入框，彻底避开平台内部上传锁、白名单拦截与 DOM 节点动态销毁重构摧毁输入框的物理深坑。

### 6. 全后台无感运行：第二桌面常驻与 -32000 离屏深水区
坚守 Windows DWM 抗休眠底线（坚决禁止最小化）。支持将 Chrome 置于 Windows 第二虚拟桌面常驻展开，或借助 `src/background_window.py` 调度至坐标深水区 `(-32000, -32000)`，实现既不占据用户主视线、又 100% 杜绝 Chromium 内核休眠（`kFrozen`）的极致全后台运转。

---

## 📂 仓库目录结构 (Repository Structure)

```
afl-bridge/
├── README.md                           # 本架构权威总纲说明文档 (v6.1.0)
├── .gitignore                          # 严格隔离凭证、缓存与临时日志
├── sync_from_live.py                   # 宿主工作区与本仓库一键代码双向同步工具
├── docs/                               # 深度技术手册与实机排障报告
│   ├── AFL_Bridge_全栈搭建与疑难排障终极宝典.md # v6.1.0 全栈排障权威宝典正本
│   └── capsule_netroom_dedup_autopsy.md         # 净室双发与思考条分裂微观尸检报告
├── src/                                # 核心运行时组件
│   ├── bridge_server.py                # 本地 8790 端口中继守护网关 (v6.1.0)
│   ├── send_to_argon.py                # 本地阻塞发件与长轮询挂起脚本 (v6.1.0)
│   ├── check_handshake.py              # 三方握手巡检与便携会话绑定工具
│   ├── open_userscript_install.py      # Win32 沙盒穿透油猴安装器
│   ├── background_window.py            # 深水离屏 (-32000) 窗口调度器
│   ├── argon_commander.user.js         # v6.1.0 生产级油猴注入脚本
│   ├── start_bridge.bat                # 一键脱壳启动中继网关批处理
│   └── launch_afl_chrome.bat           # 专用防休眠参数 Chrome 启动器
└── skills/                             # Antigravity 智能体专属法典
    ├── aistudio/                       # AFL 自动化发件与双端协同权威技能大正本
    ├── argon-flash-commander/          # 统帅与执行官双层配额节流规范
    └── tampermonkey-installer/         # 油猴脚本跨桌面穿透安装标准技能
```

---

## 🚀 极速上手 (Quick Start)

### 1. 启动本地中继网关
在仓库根目录下运行：
```powershell
python src/bridge_server.py
# 或在 Windows 下双击运行 src/start_bridge.bat
```
网关将在本地 `http://127.0.0.1:8790` 持续监听。

### 2. 跨桌面穿透安装/更新油猴脚本
运行安装助手，将通过 Win32 API 穿透沙盒并置顶 Chrome 唤起原生安装页面：
```powershell
python src/open_userscript_install.py
```
在弹出的 Chrome 页面中点击绿色的 **Install** 或 **Update** 按钮完成部署。

### 3. 打开 Google AI Studio 并绑定专属会话
在 Chrome 中登录 [Google AI Studio](https://aistudio.google.com/)，将左上角提示词标题命名为专属名称（例如 `统帅`、`高速伴读`），随后在工作区运行绑定与巡检：
```powershell
python src/check_handshake.py --bind-title "统帅"
```
当检查项显示网关运行正常且油猴脚本心跳在线时，链路即宣告全线贯通！

### 4. 呈报咨询胶囊与自动唤醒
```powershell
# 提交咨询并挂起等待统帅圣旨回传 (Reactive Wakeup 自动苏醒)
python src/send_to_argon.py --file path/to/capsule.md --wait
```

### 5. (可选) 全后台深水区无感运转
```powershell
# 将专属会话窗口平移至深水区 (-32000, -32000)，不占主屏幕且防休眠
python src/background_window.py --offscreen --target-title "统帅"

# 需要手动检视时随时唤回
python src/background_window.py --restore --target-title "统帅"
```

---

## 🛡️ 安全与隐私说明 (Security & Privacy)

- 本仓库**严格杜绝任何 API Token、硬编码密钥或私人会话文件**提交；
- 本中继服务仅在本地回环地址 `127.0.0.1:8790` 运行，不对公网开放；
- 油猴脚本通信范围受到 `@connect 127.0.0.1` 严格约束，仅与本地中继握手，不触碰任何第三方外连。

---

## 📜 维护与贡献 (Authors)
- **架构统帅**：Argon Supreme Commander (Google AI Studio)
- **工程执行**：Jin Xiao (槿潇) & Antigravity Flash Executor
- **所属用户**：[@bokxion](https://github.com/bokxion)
