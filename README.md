# 🏛️ AFL Bridge (Argon-Flash Link) v6.1.0

> **Google AI Studio 云端统帅 (Argon) 与 Antigravity 本地特遣官 (Flash) 全后台自适应跨架构协同通信中继**
> 
> *“深水不响，云汉为章；高维裁决，案前落地。”*

---

## 📖 架构概览 (Architecture Overview)

**AFL (Argon-Flash Link)** 是一套专为突破大模型上下文与配额瓶颈而设计的**分层协同与跨端自主通讯架构**。

它在 Google AI Studio（拥有百万级上下文与极致推理深度的 **Gemini 4 Argon** 统帅）与 本地开发环境（**Google Antigravity / Gemini 3.8 Flash High** 执行官）之间建立了一条**100% 全后台无感、零焦点依赖、跨桌面沙盒穿透的双向自主管道**。

```
+--------------------------------------------------------------------------+
|                  云端统帅中枢 (Google AI Studio)                          |
|             https://aistudio.google.com/prompts/[专属星宿会话]            |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |          油猴常驻脚本 (argon_commander.user.js v6.1.0)           |   |
|   |  - GM_xmlhttpRequest 特权脉冲：击穿 Chromium 后台深度挂起与节流   |   |
|   |  - 纯内存 DOM 探针：零重排 textContent，杜绝页面卡顿与失焦        |   |
|   |  - 双擎填字与原子点火：execCommand + 跨沙盒安全 Setter，150ms 闭环|   |
|   |  - 交织思考全量缝合：compareDocumentPosition 跨块拓扑排序       |   |
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
|   - 原生长轮询阻塞队列 (挂起等待直到 AI 回传或超时，零轮询空耗)          |
|   - 1-to-1 多会话单播定向路由与心跳拓扑校验                              |
|   - 附件与超长工程源码纯内存 Markdown 内联自动流转                       |
+-----------------------------------^--|-----------------------------------+
                                    |  | (原生 Reactive Wakeup 阻塞发件与结果捕获)
                                    |  v
+--------------------------------------------------------------------------+
|                   本地终端案前特遣 (Antigravity IDE / DSH)               |
|                                                                          |
|   - send_to_argon.py --wait 阻塞挂起与唤醒                               |
|   - 双模输出闭环 (<=2500 字符 stdout 直出，>2500 字符落盘秒读)           |
|   - Flash 3.8 High 案前实操：原子级改码、编译校验与高信噪比战报呈回       |
+--------------------------------------------------------------------------+
```

---

## ⚡ 核心设计哲学 (Core Principles)

### 1. 三权分立协同范式 (Tripartite Synergy)
- **主君 (The Supreme Sovereign)**：最高意志源泉与战略方向仲裁者。
- **Argon 统帅 (Chief System Architect)**：坐镇 Google AI Studio 高维中枢，洞察系统根因，推演状态机完备性，裁决顶层拓扑，下达生产级源码指令。
- **Flash 执行官 (Engineering Executor)**：案前雷霆手足，勘查现场、打包咨询胶囊、精准改动本地文件流与终端验证，释放统帅 90% 以上体力工程消耗。

### 2. 原生 Reactive Wakeup 响应式唤醒
摒弃低效脆弱的循环轮询，`send_to_argon.py --wait` 在本地挂起长轮询专属 Ticket。统帅推演完成回传瞬间，子进程 `exit(0)` 退出，触发 Antigravity 原生 Reactive Wakeup 立即自苏醒。

### 3. 交织思考全量缝合 (Interleaved Thinking Splicing)
借助 DOM `compareDocumentPosition` 节点位置比对算法，自动将 AI Studio 中思考过程（Thought Blocks）与正文回答按物理渲染顺序完整拼接，杜绝长文本或多轮输出中的乱序与丢块。

### 4. 跨桌面沙盒穿透与油猴无损安装 (Desktop Sandbox Piercing)
针对 Windows 隔离桌面、前台焦点锁以及 Edge 劫持痛点，提供 `open_userscript_install.py`，以原生 Win32 API 穿透沙盒并置顶 Chrome，唤起原生 Tampermonkey 绿色安装界面。

---

## 📂 仓库目录结构 (Repository Structure)

```
afl-bridge/
├── README.md                           # 本架构说明文档
├── .gitignore                          # 严格隔离凭证、缓存与临时日志
├── sync_from_live.py                   # 工作区与本仓库一键代码同步工具
├── docs/                               # 深度技术手册与尸检报告
│   ├── AFL_Bridge_全栈搭建与疑难排障终极宝典.md
│   └── capsule_netroom_dedup_autopsy.md
├── src/                                # 核心运行时组件
│   ├── bridge_server.py                # 本地 8790 端口中继守护服务器
│   ├── send_to_argon.py                # 本地终端发件与长轮询挂起脚本
│   ├── check_handshake.py              # 全链路心跳与星宿会话健康诊断
│   ├── open_userscript_install.py      # Win32 沙盒穿透油猴安装唤起
│   ├── background_window.py            # Windows 后台窗口句柄与焦点调度
│   ├── argon_commander.user.js         # v6.1.0 生产级油猴注入脚本
│   ├── start_bridge.bat                # 一键启动中继服务批处理
│   └── launch_afl_chrome.bat           # 启动专用调试 Chrome 实例
└── skills/                             # Antigravity 智能体专属技能
    ├── aistudio/                       # AFL 自动化发件与统帅请旨核心技能
    ├── argon-collab-bridge/            # 统帅协同中继总纲
    ├── argon-flash-commander/          # 统帅与执行官双层配额节流规范
    └── tampermonkey-installer/         # 油猴脚本标准化安装更新技能
```

---

## 🚀 快速上手 (Quick Start)

### 1. 启动本地中继服务
在中继服务根目录运行：
```bash
python src/bridge_server.py
# 或在 Windows 下双击运行 src/start_bridge.bat
```
服务将在本地 `http://127.0.0.1:8790` 监听。

### 2. 安装/更新油猴脚本
运行安装助手，将自动唤起 Chrome 打开原生安装页面：
```bash
python src/open_userscript_install.py
```
在弹出的 Chrome 页面中点击绿色的 **Install** 或 **Update** 按钮完成部署。

### 3. 打开 Google AI Studio 并绑定会话
在 Chrome 中登录 [Google AI Studio](https://aistudio.google.com/)，打开或新建专属协同会话（例如会话标题包含 `ds` 或指定工程名）。

### 4. 链路健康自检
在终端运行诊断命令：
```bash
python src/check_handshake.py
```
若检查项全部通过（8790 端口就绪、Chrome 进程在线、Tampermonkey 心跳正常），则链路已全线贯通！

### 5. 呈报咨询胶囊
```bash
# 提交咨询并挂起等待统帅圣旨回传
python src/send_to_argon.py --file path/to/capsule.md --wait
```

---

## 🛡️ 安全与合规说明 (Security & Privacy)

- 本仓库**严格杜绝任何 API Token、硬编码密钥或私人会话文件**提交。
- 本中继服务仅在本地回环地址 `127.0.0.1:8790` 运行，不对公网开放。
- 油猴脚本通信范围受到 `@connect 127.0.0.1` 严格约束，仅与本地中继握手，不触碰任何第三方外连。

---

## 📜 维护与贡献 (Authors)
- **架构统帅**：Argon Supreme Commander (Google AI Studio)
- **工程执行**：Jin Xiao (槿潇) & Antigravity Flash Executor
- **所属用户**：[@bokxion](https://github.com/bokxion)
