---
name: argon-collab-bridge
description: >-
  Antigravity 本地终端向云端 Argon/Gemini 架构统帅呈报咨询、跨账号/跨设备转运消息的协同中继总纲。将 AFL (Argon-Flash Link) v6.0+ 全自动化直连通道（send_to_argon.py + 8790网关 + 油猴v6.0+）确立为首席主通道，涵盖通用解耦草稿箱模式与法定前置契约约定(Mandatory Inbox Contract Agreement Protocol)、多会话定向单播与算力分层拓扑、50ms状态机精准防吞单次原子点火与250ms防抖、第二桌面常驻展开铁律、交织思考跨块DOM全量缝合(compareDocumentPosition)、微秒级原子防重及内存纯文本内联；同时保留无状态剪贴板中继（argon_bridge.py）作为离线降级容灾方案。当用户提到“呈报Argon”、“发给Argon”、“咨询Argon”、“领旨”、“读取Argon回复”、“转运消息给Argon”、“换号前情提要”时激活。
---

# Antigravity × Argon 消息转运与协同中继总纲 (Argon Collab Bridge v6.0+)

本技能专为 **Antigravity 本地工程终端** 与 **云端 Gemini Argon / 模型集群** 之间的高效、无损、连续的消息转运而设计。为解决跨账号配额轮换、多任务并发隔离、算力效能优化以及自动化流水线调优需求，本技能确立了**“AFL 全自动直连主通道优先，无状态剪贴板容灾降级兜底”**的双轨立体架构，确保任何智能体接令后均能以最高确定性完成消息转运与领旨闭环。

---

## 一、 双轨协同中继架构概览 (Dual-Track Architecture)

```
                     ┌──────────────────────────────────────────────┐
                     │ 主君下达：“呈报 Argon / 咨询统帅 / 转运消息”  │
                     └──────────────────────┬───────────────────────┘
                                            │
                                   [ 路由决策判断 ]
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
     【首席通道 · AFL 全自动直连中继】             【次席通道 · 剪贴板无状态降级中继】
       (首选 100% 自动化主通道 v6.0+)                (离线 / 跨机 / 应急容灾备用)
    ┌───────────────────────────────┐               ┌───────────────────────────────┐
    │ 1. 草稿箱提取/案前显式策展    │               │ 1. 撰写本轮增量报告 .md       │
    │ 2. check_handshake.py 巡检    │               │ 2. argon_bridge.py push       │
    │ 3. send_to_argon.py 投递      │               │ 3. 主君手动粘贴至网页/客户端  │
    │ 4. 8790 微秒原子锁 + 油猴脉冲 │               │ 4. argon_bridge.py pull       │
    │ 5. 50ms 单次原子点火 + DOM 缝合│               │ 5. 读取 argon_latest_reply.md │
    │ 6. 原生 Reactive Wakeup 唤醒  │               └───────────────────────────────┘
    │ 7. 终端回显 / 专属落盘第一反射│
    └───────────────────────────────┘
```

1. **首席自动化主通道 (AFL Automated Direct Link Pipeline v6.0+ - 优先调用)**：
   - 基于 `d:\maid-coding-space\argon_anti_bridge` 工具链；
   - 依赖 8790 端口常驻守护网关、Tampermonkey 油猴脚本（AFL v6.0+ 特权 IPC 脉冲）、原生 Reactive Wakeup 阻塞唤醒机制；
   - **核心优势**：
     - **通用解耦草稿箱模式与法定前置契约约定**：前台服务程序接入必须显式与 Antigravity 约定草稿箱路径（严禁无契约转发与野蛮落盘），前台毫秒级落盘释放，主意识显式受控调度，严禁孤儿后台盲转；
     - **多会话定向单播与算力分层**：通过 `--target-title` 精准路由至架构裁决专席或高速伴读专席，实现算力效能最优化；
     - **第六代油猴中继韧性准则**：50ms 状态机精准防吞点火与单次确定性原子击发 (Single-Shot Physical Click & 250ms Anti-Debounce)、`compareDocumentPosition` 交织思考跨块 DOM 全量缝合、内存纯文本内联抗脆弱性、微秒级网关取件原子防重锁；
     - 全后台运行、第二桌面永久常驻展开（坚决禁止最小化）、全面内存纯文本内联（In-memory Markdown Inlining）、无需任何手动复制粘贴。
2. **次席降级中继通道 (Clipboard Stateless Fallback Pipeline - 容灾备用)**：
   - 基于 `D:\maid-coding-space\argon_bridge.py` 与 `argon_context_header.md`；
   - 依赖 Windows 双模剪贴板（`CF_HDROP` 虚拟文件流 + `CF_UNICODETEXT` 全量 UTF-8 文本）；
   - **核心优势**：无外部端口依赖，在网关离线、网络隔离、跨物理机操作或主君手动快速跨账号轮换时，依然能实现 100% 无状态上下文继承与无损代码拉取。

---

## 二、 首席通道：AFL 全自动直连转运规范 (Primary Pipeline)

任何智能体在收到向 Argon 呈报或转运消息的指令时，**必须默认首先尝试此通道**：

### 1. 通用解耦草稿箱模式与法定前置契约约定 (Generic Decoupled Inbox & Mandatory Contract Agreement)
- **【草稿箱前置契约约定铁律 (Mandatory Inbox Contract Agreement Protocol)】**：
  - 任何前端服务程序、独立 UI 终端、移动端业务模块或微服务后台，凡需经由 Antigravity 调度转发至 AI Studio，**必须在系统接入或功能初始化之初，显式与 Antigravity 案前主智能体约定并配置标准化的草稿箱路径（例如工作区约定的 `data/<service_name>_inbox/` 专用目录）**，方允许启动消息转发与提问提交流程；
  - **严禁无契约转发与野蛮落盘**：严禁在未与 Antigravity 显式对齐草稿箱路径的情况下擅自生成临时文件或盲目分发；严禁前端直接跨层绕过 Antigravity 去强行触碰 AI Studio 网关。草稿箱路径的显式约定是建立“前端毫秒级释放、案前智能体显式策展、双向响应式闭环回传”的法定前置准入契约。
- **解耦提取与案前显式策展流程**：
  - 若待转运内容源于前台独立 UI、移动客户端、前端服务程序或伴读子系统，业务端必须严格按照约定契约将数据轻量写入专用草稿箱目录（如 `data/<service_name>_inbox/draft_<timestamp>.md`）；
  - 主智能体在案前使用 `read_file` 显式读取该草稿，杜绝启动脱机后台硬轮询盲转脚本（严禁 `watch_*`、`forward_*` 私自截胡）；
  - 智能体进行业务上下文校验与提示词工程策展，附带协议信标后发起受控投递。

### 2. 前置健康巡检与专属会话核验
```powershell
python d:\maid-coding-space\argon_anti_bridge\check_handshake.py
```
- 检查当前工作区是否配置了 `.aistudio_config.json`；若未配置，主动向主君请示配对会话标题；
- 巡检输出 `【巡检结论】：协作链路 100% 畅通！` 且确认目标标签页在线时，方可进行发信。

### 3. 多会话定向单播与算力分层投递 (Unicast & Tiered Model Dispatch)
根据任务性质定向单播至对应算力专席：
- **高阶架构裁决专席（如 Argon 统帅、Pro 深度思考）**：处理底层物理根因、状态机设计、复杂代码重构；
- **高速创作与伴读专席（如 Gemini 3.1 Pro、Flash 系列）**：处理长文切片审读、高频文学伴读、常态化报告分析。

运行投递命令：
```powershell
# 1. 基础纯文本胶囊转运（阻塞等待，触发 Reactive Wakeup 自我苏醒）
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <咨询文件路径> --wait

# 2. 内存纯文本内联模式（超万字长文本与多工程源码强烈推荐）：
# 在案前将工程源码与上下文直接在内存中编织入 Markdown 胶囊，彻底避开伪造文件上传锁、格式白名单拦截与 DOM 重构摧毁输入框的物理深坑
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <包含内联源码与上下文的Markdown文件> --wait

# 3. 指定多会话定向单播路由（覆盖默认绑定）
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <咨询文件路径> --target-title "<目标会话标题>" --wait
```

### 4. 双模自适应接令与第一反射
- **短文直读（≤ 2500 字符）**：`send_to_argon.py` 终端 stdout 已输出完整裁决，执行官直接读取推进；
- **长文展卷（> 2500 字符）**：终端输出前 500 字符摘要，并提示落盘文件 `data/tasks/<ticket_id>_reply.md`。
  - **【第一反射铁律】**：苏醒后首个工具调用必须且只能是 `read_file` 查阅该专属落盘文件！
- **归档写回**：将产出结论清洗后写回业务子系统的归档卷帙中，并安全清理草稿箱。

---

## 三、 次席通道：无状态剪贴板降级中继规范 (Stateless Clipboard Fallback)

当检测到 8790 端口网关不可用、处于受限隔离环境，或主君明确指示“用剪贴板发”、“复制到剪贴板”、“手动中转”时，无缝切换至次席通道：

### 1. 核心资产分布
- **滚动无状态前情提要矩阵**：`D:\maid-coding-space\argon_context_header.md`
  - 浓缩沉淀宿主不动基线、已证伪死路禁令、已实装防线清单及历史崩溃台账。
- **统一双向剪贴板引擎**：`D:\maid-coding-space\argon_bridge.py`
  - 负责自包含胶囊组装（`push`）、无损拉取（`pull`）与记忆更新（`update-state`）。
- **下行无损收件箱**：`D:\maid-coding-space\temp_files\argon_latest_reply.md`
  - 避免聊天框直接粘贴造成的格式破损与代码截断。

### 2. 标准作业流程 (SOP)

#### 场景 A：上行呈报（装填换号幂等胶囊）
1. 在 `D:\maid-coding-space\temp_files\` 下编写本轮增量取证报告（例如 `2026-10-26_issue_autopsy.md`）；
2. 运行一键装填命令：
   ```powershell
   python D:\maid-coding-space\argon_bridge.py push "D:\maid-coding-space\temp_files\2026-10-26_issue_autopsy.md"
   ```
   - 若省略路径，直接运行 `python D:\maid-coding-space\argon_bridge.py push`，脚本会自动寻找 `temp_files` 中最新修改的 `.md`；
   - 脚本自动将 `argon_context_header.md`（前情头）+ 本轮正文 + 协议尾合并，以 `CF_HDROP` 与 `CF_UNICODETEXT` 双模注入主君剪贴板；
   - 主君在任何浏览器/客户端中直接按 `Ctrl+V` 粘贴，Argon 统帅即可瞬间获得无缝上下文。

#### 场景 B：下行领旨（无损接收 Argon 方案）
1. 主君在 Argon 答复页面点击“复制”后，发送指令（如“领旨”或“已复制”）；
2. 智能体执行无损拉取：
   ```powershell
   python D:\maid-coding-space\argon_bridge.py pull
   ```
3. 智能体使用 `read_file` 查阅 `D:\maid-coding-space\temp_files\argon_latest_reply.md`，获取无损代码补丁落地。

#### 场景 C：记忆滚雪球更新（阶段性结案同步）
当一轮重大架构改造经公子实机测试验收闭环后，将新结论沉淀入前情矩阵：
```powershell
python D:\maid-coding-space\argon_bridge.py update-state "记录最新证实的物理根因或已部署防线"
```

---

## 四、 跨通道自适应决策矩阵 (Routing Matrix)

| 场景条件 | 推荐中继通道 | 核心触发指令 / 脚本 |
| :--- | :--- | :--- |
| **常规日常开发、需要全自动全后台运转** | **AFL 全自动直连主通道** | `python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file ... --wait` |
| **大文本量切片、万字富上下文与工程源码呈报** | **AFL 全自动直连主通道（内存纯文本内联）** | `python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <内联Markdown> --wait` |
| **指向特定算力专席（如高速创作/伴读专席）** | **AFL 多会话定向单播路由** | `python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file ... --target-title "<专席标题>" --wait` |
| **Chrome 离线、8790 端口未开启且无法拉起** | **剪贴板降级中继通道** | `python D:\maid-coding-space\argon_bridge.py push <文件>` |
| **主君在其他物理机、移动端或第三方独立客户端** | **剪贴板降级中继通道** | `python D:\maid-coding-space\argon_bridge.py push / pull` |
| **油猴脚本需要安装或升级至 v6.0+** | **跨桌面特权穿透工具** | `python d:\maid-coding-space\argon_anti_bridge\open_userscript_install.py` |

---

## 五、 核心设计范式与执行护栏 (Architectural Guardrails)

1. **通用解耦草稿箱规范与法定前置契约约定铁律 (Mandatory Inbox Contract Agreement Protocol)**：
   - **前置契约法定准入**：任何前端服务程序、独立 UI 终端、移动端业务模块或微服务后台经由 Antigravity 调度转发至 AI Studio，**必须在系统接入或功能初始化之初，显式与 Antigravity 案前主智能体约定并配置标准化的草稿箱路径（例如工作区约定的 `data/<service_name>_inbox/` 专用目录）**，方允许启动消息转发与提问提交流程；
   - **严禁无契约转发与野蛮落盘**：严禁在未与 Antigravity 显式对齐草稿箱路径的情况下擅自生成临时文件或盲目分发；严禁前端直接跨层绕过 Antigravity 去强行触碰 AI Studio 网关。草稿箱路径的显式约定是建立“前端毫秒级释放、案前智能体显式策展、双向响应式闭环回传”的法定前置准入契约；
   - **毫秒级落盘与秒级释放**：外部调用客户端与前台 UI 一律以“毫秒级落盘、秒级释放”写入已约定的契约草稿箱；
   - **绝对严禁孤儿后台盲转**：禁止私自启动脱离主意识的后台硬轮询盲转脚本（如 `watch_*`、`forward_*`）私自截胡发件；调度权必须牢牢掌握在主智能体案前。
2. **算力分层与配额保护**：
   - 严禁将大模型高阶推演专席用于琐碎体力排版或粗粒度文本搬运；
   - 高频、大文本量、高吞吐场景统一路由至高速模型专席（`--target-title`）。
3. **第六代油猴中继韧性准则**：
   - **50ms 状态机精准防吞点火与单次确定性原子击发**：彻底拔除盲目的 300ms 二次重发扳机（`else triggerRun`）与多阶连续扫射叩击，收敛为每 50ms 侦测 Angular Tokenizer 解锁后微秒级单次物理原子点击，配合 250ms 防抖流控与网关微秒级原子锁，从物理上彻底根除重发风暴与交织思考条在正文中穿插分裂的故障；
   - **交织思考跨块 DOM 全量缝合**：采用 `compareDocumentPosition` 穿透算法收集 User Prompt 后的所有有效 Model 块，杜绝长文或文学正文被截断；
   - **内存纯文本内联抗脆弱性**：超万字切片与多工程源码在本地内存拼接为纯文本统一打入输入框，彻底规避平台内部上传锁、白名单拦截与 DOM 节点动态销毁重构导致 `<textarea>` 沦为孤儿节点的物理深坑；
   - **微秒级原子防重锁**：网关轮询取件时实施即时原子锁定，物理杜绝多标签页并发竞争风暴。
4. **第二桌面常驻展开铁律（坚决禁止最小化）**：Windows DWM 在窗口最小化时会停止 GPU 视口绘制并剥离渲染表面，直接导致宿主浏览器冻结内部事件循环，使 Angular 脏检查、Tokenizer 词元解析与 DOM 渲染彻底停摆。宿主 Chrome 必须永久常驻置于 Windows 第二虚拟桌面展开运行，坚决禁止最小化窗口。
5. **纯英文路径铁律**：所有自动化脚本、日志及落盘文件必须位于纯英文路径（如 `argon_anti_bridge`、`temp_files`），杜绝编码混乱。
6. **Reactive Wakeup 零轮询**：调用 `send_to_argon.py --wait` 后，智能体应立即结束当前步，依赖子进程退出自动唤醒，严禁自行编写 while 循环高频探测。
7. **宗师级完结信标守卫**：无论哪种通道，在呈报文本末尾包含 `<!-- [AFL_EOF_ACK] -->` 均能大幅提升模型回复的规范性，实现极速闭环。
