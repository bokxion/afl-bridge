---
name: aistudio
description: 当用户提到 aistudio、呈报 aistudio、发给 aistudio、AFL、统帅咨询、请旨 Argon 时激活。提供 AFL (Argon-Flash Link) v6.0+ 全后台零接触穿透、多会话定向单播与算力分层拓扑机制，包含通用解耦草稿箱模式与法定前置契约约定(Mandatory Inbox Contract Agreement Protocol)、长文本与工程源码内存纯文本内联(In-memory Markdown Inlining)、50ms状态机精准防吞单次原子点火与250ms防抖、第二桌面常驻展开铁律、交织思考跨块DOM全量缝合(compareDocumentPosition)、微秒级原子防重、原生 Reactive Wakeup 阻塞唤醒、双模闭环输出与专属落盘第一反射，以及跨桌面油猴无损安装。
---

# AFL (Argon-Flash Link) 协同与 AI Studio 多会话定向直连规范 (v6.0+ 工业级全韧性架构版)

本技能专为 **AI Studio (Argon/Gemini 云端模型集群)** 与 **Antigravity (Flash 执行官)** 之间的高维人机协同直连架构而设计。依托 **原生 Reactive Wakeup 阻塞唤醒**、**多会话 1-to-1 定向单播矩阵**、**算力分层拓扑 (Tiered Model Topology)**、**通用解耦草稿箱模式与法定前置契约约定 (Generic Decoupled Inbox & Mandatory Contract Protocol)** 以及 **第六代油猴中继韧性准则 (AFL Userscript v6.0+ Resilience Standard)**，彻底终结人工复制粘贴、拖拽文件与盲目掐表等待转圈的历史，实现全天候、全后台、高吞吐、无人值守的工业级双端一体化协同闭环。

---

## 一、 架构禁区与核心铁律 (Architectural Invariants & Redlines)

1. **绝对禁绝 `/browser` 与 Selenium 类自动化**：
   - 严禁使用任何浏览器自动化工具（如 `/browser`）直接访问或操作 AI Studio 网页。
   - 所有浏览器 DOM 交互与事件派发，均由运行在宿主 Chrome 内的原生油猴脚本 `argon_commander.user.js` 在沙箱内自主闭环。
2. **全面废黜 CDP UI 模拟注入**：
   - 彻底停用脆弱的 CDP UI 模拟注入（`cdp_sender.py`），默认将 `ENABLE_CDP_AUTO_INJECT = False`。
   - 确立 **原生 Reactive Wakeup 阻塞长轮询子进程** 为唯一回传唤醒正朔。
3. **1-to-1 星宿并发与 Ticket 事务隔离**：
   - 每次咨询投递，网关派发全局唯一的事务令牌 `ticket_id`（Ticket），并构建私有的 `threading.Event()` 与专属落盘路径 `data/tasks/<ticket_id>_reply.md`。
   - 浏览器端油猴脚本严格执行单播持牌与带牌核销，各会话标签页互不干扰、并行不悖。
4. **拒绝硬编码掐表，状态驱动感知 (Zero-Blind-Wait State Machine)**：
   - 严禁使用盲目的 sleep 或硬超时作为生成结束判断依据；
   - 采用 **纯内存状态机 + 完结信标极速短路 + 静默倒计时（2200ms）兜底** 双轨感知，确保答复完整无损。
5. **严禁孤儿后台盲目转发 (Ban on Detached Blind Background Daemons)**：
   - 明令严禁私自启动脱离主意识的后台硬轮询盲转脚本（如 `watch_*`、`forward_*`）私自截胡发件。
   - 外部业务数据必须经由草稿箱暂存，由案前主智能体实施受控调度，杜绝脱缰脚本破坏状态机时序。
6. **显式策展与调度权守卫 (Explicit Curation & Scheduling Ownership)**：
   - 投递调度权必须牢牢掌握在主智能体手中。由智能体在案前显式读取草稿、进行上下文核验与提示词策展，通过 `send_to_argon.py --target-title <目标会话标题> --wait` 实施受控阻塞投递；收到响应后完成清洗并写回业务子系统的归档卷帙中。
7. **草稿箱前置契约约定铁律 (Mandatory Inbox Contract Agreement Protocol)**：
   - 任何前端服务程序、独立 UI 终端、移动端业务模块或微服务后台，凡需经由 Antigravity 调度转发至 AI Studio，**必须在系统接入或功能初始化之初，显式与 Antigravity 案前主智能体约定并配置标准化的草稿箱路径（例如工作区约定的 `data/<service_name>_inbox/` 专用目录）**，方允许启动消息转发与提问提交流程；
   - **严禁无契约转发与野蛮落盘**：严禁在未与 Antigravity 显式对齐草稿箱路径的情况下擅自生成临时文件或盲目分发；严禁前端直接跨层绕过 Antigravity 去强行触碰 AI Studio 网关。草稿箱路径的显式约定是建立“前端毫秒级释放、案前智能体显式策展、双向响应式闭环回传”的法定前置准入契约。
8. **第二桌面常驻展开铁律（坚决禁止最小化）**：
   - 宿主 Chrome 必须永久常驻置于 Windows 第二虚拟桌面（Virtual Desktop 2）前台展开运行，绝对禁止最小化窗口；
   - **物理机理阐明**：Windows DWM (Desktop Window Manager) 在窗口最小化时会立即停止 GPU 视口绘制并剥离渲染表面，导致宿主浏览器冻结内部事件循环，使 Angular 脏检查、Tokenizer 词元计数与 DOM 渲染彻底停摆；唯有保持窗口在第二虚拟桌面中展开常驻，方能确保全天候后台无感、无遮挡且稳定的毫秒级点火与高吞吐生成。

---

## 二、 AFL v6.0+ 油猴中继韧性准则 (Userscript v6.0+ Resilience Standard)

### 1. 50ms 状态机精准防吞点火与单次确定性原子击发 (Single-Shot Physical Click & 250ms Anti-Debounce)
- **物理痛点攻克**：旧架构在注入文本后使用盲目的掐表硬等待（如 `setTimeout 300ms`）或 0ms 盲发，常因现代前端框架（如 Angular Tokenizer）尚未完成词元计数和输入框模型绑定，导致 Run 按钮仍处于 `disabled` 状态而被静默吞没；若采用多阶连续叩击或盲目的二次重发扳机（如 `else triggerRun`），又极易引爆多重并发请求风暴，导致生成中断或多回合交织思考容器在正文中混乱穿插分裂；
- **单次确定性原子击发机制**：
  - 彻底拔除盲目的 300ms 二次重发扳机（`else triggerRun`）与连续扫射叩击，收敛为每 50ms 高频侦测 Angular Tokenizer 解锁后微秒级单次物理原子点击（`dispatchPhysicalClick`）；
  - 严格配合 **250ms 防抖流控** 与 **网关微秒级单次取件原子锁**，在前端与网关形成双保险；
  - 一旦捕获到前端框架完成词元解析并剥离 `disabled` / `aria-disabled` / `mat-mdc-button-disabled` 属性的微秒瞬间，立即精准击发一次原子点击；若达到 300ms 阈值仍未自然解禁，则先通过 DOM 原生 API 剥离 `disabled` 属性再执行受控单次点击；点击后立即锁定点火状态，从物理上彻底根除重发风暴与交织思考条在正文中穿插分裂的时序故障。

### 2. 思考容器跨块 DOM 全量缝合 (Cross-Chunk Interleaved Thinking DOM Stitching)
- **物理痛点攻克**：针对现代前沿大模型交织思考（Interleaved Thinking）机制，模型的单轮回复会被平台拆分为多个交错出现的容器（如 `ms-thought-chunk` 与 `ms-text-chunk` 轮流出现），甚至分裂为多个视觉 Turn；若只提取最后一个 DOM 容器，将直接丢失前半部分重要的长篇推理或文学正文；
- **`compareDocumentPosition` 穿透缝合算法**：
  - 答复提取器使用原生 DOM 树拓扑关系判别：
    ```javascript
    const targetModelContainers = lastUser
        ? modelContainers.filter(mc => (lastUser.compareDocumentPosition(mc) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0)
        : [modelContainers[modelContainers.length - 1]];
    ```
  - 严格筛选位于本轮最新 User Prompt 之后的所有 Model 容器；
  - 深度剥离思考胶囊（`thought-activity-host`, `ms-thought-chunk`, `mat-expansion-panel`）与报错节点；
  - 按文档物理先后次序，完整收集并全量缝合所有正文文本容器（`ms-text-chunk`, `ms-code-chunk`），杜绝截断事故。

### 3. 内存纯文本内联胜过脆弱的伪造文件上传 (In-Memory Text Inlining over Fragile File Uploads)
- **物理痛点攻克**：在涉及一万字以上的长文本切片或多工程源码分析时，若强行伪造 File 对象模拟文件上传，极易触发平台内部长达数秒至数十秒的上传锁、文件解析校验等待与格式白名单拦截，甚至因 DOM 节点在上传后被动态销毁重构而导致后续输入框 `<textarea>` 成为“孤儿节点”，引发无法键入或内容被冲刷丢失的物理深坑；
- **工业级内联范式**：
  - 彻底废除模拟文件上传机制，全面推行 **内存纯文本内联（In-memory Markdown Inlining）** 规范；
  - 对海量文本切片、前置上下文与工程源码文件（如 `.cs`, `.py`, `.vue` 等），统一在案前内存中整合成格式规范的 Markdown 纯文本 Prompt（采用代码块清晰标注文件名与语言），直接打入主输入框；
  - 纯文本打入耗时仅需数十毫秒，既 100% 规避平台文件上传通道的偶发卡死、白名单封禁与 DOM 重建摧毁输入框的风险，又能充分发挥现代百万级上下文模型的直接推演理解能力。

### 4. 微秒级原子防重与单调回合守卫 (Microsecond Atomic Lock & Monotonic Turn Guard)
- **网关层微秒级原子锁定**：
  - 在网关（`bridge_server.py`）轮询接口（`/api/bridge/poll_consultation`）中，引入单次执行原子互斥锁；
  - 只要任何一个匹配的浏览器标签页拉取到任务，网关在 `with self.lock:` 保护下微秒级将 `ready_for_aistudio` 置为 `False`，彻底根除因前端发送 `ack_consultation` 之前的网络窗口期导致多标签页并发争抢的致命缺陷；
- **回合单调递增锁 (`AFL_BASELINE_MODEL_COUNT`)**：
  - 注入发件瞬间捕获当前 DOM 中的回复块基线计数，回传时强制要求 `currentModelCount >= baselineModelCount + 1`，从物理层面 100% 杜绝误抓历史陈旧回复。

### 5. 扩展特权 IPC 脉冲引擎 (Extension IPC Privileged Pulse)
- 借助 Tampermonkey 提供的扩展级特权 API `GM_xmlhttpRequest`，构建脱离普通页面渲染管线的特权时钟脉冲，彻底击穿现代浏览器对非激活或后台标签页的定时器节流（Timer Clamping），配合第二桌面常驻展开，实现全后台毫秒级响应。

### 6. 行尾绝对锚定正则与信标直通车 (`AFL_EOF_ACK_REGEX`)
- 采用严格行尾锚定正则：
  ```javascript
  const AFL_EOF_ACK_REGEX = new RegExp('\\[' + 'AFL_EOF_' + 'ACK\\]\\s*(?:-->)?\\s*`{0,3}\\s*$');
  ```
- 唯有信标出现在文本末尾时触发零延迟极速直通车；中间引述安全忽略；回传前自动剥离信标确保正文纯净。

### 7. 纯内存 `textContent` 状态探测与零重排重绘 (Pure-Memory State Engine)
- 彻底拔除引发浏览器重排（Reflow）的属性访问，全部状态判断基于纯内存 DOM 节点的 `textContent` 与 `getComputedStyle`，在页面位于独立虚拟桌面或视口被遮挡状态下具备极限健壮性。

---

## 三、 通用解耦草稿箱模式与法定前置契约约定 (Generic Decoupled Inbox & Mandatory Contract Protocol)

在任何现代工程协同体系中，前台业务客户端（如 UI 交互界面、前端服务程序、移动端、各类伴读服务或独立的微服务后台）与耗时较长的云端大模型推理之间，必须建立坚固的**异步解耦屏障**。如果有前端服务程序或业务后台介入，草稿箱路径的前置契约对齐具有最高法定义务。

```
┌──────────────────────────────────────────────┐
│  外部独立业务子系统 / 前端服务程序 / UI 终端 │
└──────────────────────┬───────────────────────┘
                       │ 0. [法定前置契约] 显式与 Antigravity 约定草稿箱路径
                       │ 1. 毫秒级落盘写入
                       ▼
┌──────────────────────────────────────────────┐
│    data/<service_name>_inbox/ 专用目录       │ ◄── [标准化契约草稿箱]
└──────────────────────┬───────────────────────┘
                       │ 2. 立即返回 HTTP 200 / Ready (释放前台，零超时)
                       │
                       │ 3. 案前主智能体显式接管 (上下文核验 + 提示词策展)
                       ▼
┌──────────────────────────────────────────────┐
│           Antigravity 案前主智能体           │
└──────────────────────┬───────────────────────┘
                       │ 4. send_to_argon.py --target-title <会话> --wait (受控阻塞投递)
                       ▼
┌──────────────────────────────────────────────┐
│            AI Studio 专项标签页              │
└──────────────────────┬───────────────────────┘
                       │ 5. 响应回传与清洗
                       ▼
┌──────────────────────────────────────────────┐
│          写入业务子系统归档卷帙              │
└──────────────────────────────────────────────┘
```

### 1. 草稿箱前置契约约定铁律 (Mandatory Inbox Contract Agreement Protocol)
- **法定前置准入准则**：任何前端服务程序、独立 UI 终端、移动端业务模块或微服务后台，凡需经由 Antigravity 调度转发至 AI Studio，**必须在系统接入或功能初始化之初，显式与 Antigravity 案前主智能体约定并配置标准化的草稿箱路径（例如工作区约定的 `data/<service_name>_inbox/` 专用目录）**，方允许启动消息转发与提问提交流程；
- **严禁无契约转发与野蛮落盘**：
  - 严禁在未与 Antigravity 显式对齐草稿箱路径的情况下擅自生成临时文件或盲目分发；
  - 严禁前端跨层越权、绕过 Antigravity 去强行触碰 AI Studio 网关（如私自调用网关接口或直接操控浏览器）；
  - 草稿箱路径的显式约定是建立“前端毫秒级释放、案前智能体显式策展、双向响应式闭环回传”的法定前置准入契约，未达成契约前一切转发链路均处于未激活门控拦截状态。

### 2. 轻量落盘与秒级释放原则 (Lightweight Ingestion & Instant Client Release)
- 任何外部独立业务子系统、前端服务程序、UI 终端、移动客户端或前台伴读环境，在生成待处理长文本或复杂提问时，均采用“轻量落盘、秒级释放”策略；
- 仅用毫秒级时间将数据写入约定的通用草稿箱目录（如 `data/<service_name>_inbox/draft_<timestamp>.md` 或类似纯英文规范路径）；
- 写入成功后立即向调用方返回就绪状态（HTTP 200 OK 或成功回调），严防前台长时间挂起、UI 冻结或触发网关网络超时。

### 3. 严禁孤儿后台盲目转发 (Ban on Detached Blind Background Daemons)
- **致命缺陷剖析**：若编写脱离主智能体意识的后台硬轮询脚本（如 `watch_and_forward.py`），脚本在脱机状态下缺乏全局业务语境与配额感知，极易在外部系统产生半成品草稿时抢跑发信，造成提示词残缺、目标会话错乱或引发网络风暴；
- **架构禁令**：明令严禁私自启动任何脱离主意识的后台硬轮询盲转脚本。草稿箱本质为静态缓冲区，绝不允许存在自动化“截胡发件人”。

### 4. 智能体案前显式策展与调度权守卫 (Agent Explicit Curation & Controlled Dispatch)
- 调度权必须牢牢掌握在主智能体手中；
- 当主智能体察觉到草稿箱内有待处理任务或主君下达处理指令时，由智能体在案前显式执行：
  1. 使用 `read_file` 查阅草稿箱内容，核验业务上下文与完整性；
  2. 根据工况需求进行提示词工程策展（补充元数据、约束条件与完结信标）；
  3. 调用 `send_to_argon.py --target-title <目标会话标题> --wait` 实施受控阻塞投递；
  4. 收到大模型返回的高维成果后，完成内容清洗与质量核验；
  5. 将沉淀成果原子化写回业务子系统的归档卷帙或知识库中，并安全清理/归档对应草稿。

---

## 四、 多会话定向单播与算力分层拓扑 (Multi-Session Unicast & Tiered Model Topology)

为了兼顾最高维度的系统推演深度与大文本量内容创作的高吞吐需求，AFL 架构在浏览器宿主端与模型端实施**“多会话并行长驻 + 算力分层映射”**拓扑。

```
                                  ┌───────────────────────────────┐
                                  │      Antigravity 本地中枢     │
                                  └───────────────┬───────────────┘
                                                  │
                               [ --target-title 高精度单播路由 ]
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 │                                                                 │
                 ▼                                                                 ▼
   【会话席 A：架构顶层裁决专席】                                    【会话席 B：高速创作与伴读专席】
   - 目标标题: "统帅" / "Architecture"                               - 目标标题: "伴读创作" / "Fast-Gen"
   - 绑定模型: Gemini 4 Argon / Pro (Thinking Max)                   - 绑定模型: Gemini 3.1 Pro / Flash (高吞吐)
   - 专攻场景: 物理根因穿透、状态机推演、工业级代码重构                - 专攻场景: 万字文本剖析、情境文学创作、高频伴读
   - 特点: 深度长思辨、极高单次价值、严格配额保护                      - 特点: 秒级高吞吐、大文本量、无配额焦虑
```

### 1. 多专项标签页长驻隔离 (Parallel Specialized Tabs)
- 在宿主 Chrome 中，同时保持多个专项 AI Studio 会话标签页并行长驻；
- 各标签页由 AFL 油猴脚本自主注入并维持心跳，互为独立沙箱，杜绝跨业务上下文踩踏与历史记忆混乱。

### 2. `--target-title` 高精度单播路由 (High-Precision Unicast Routing)
- 各项目工作区根目录下可通过 `.aistudio_config.json` 固化默认专属绑定的会话标题；
- 在执行发信时，亦可通过 `--target-title <会话标题>` 命令行参数实施高精度动态单播定向投递；
- 网关在匹配派发时，严格比对标签页标题与目标标题，确保军机胶囊准确投递至指定专席。

### 3. 算力分层设计原则 (Tiered Model Topology)
- **高阶架构推演专席 (High-Reasoning Tier)**：
  - 绑定旗舰级大模型（如 Argon 统帅、Pro 深度思考模式）；
  - 专攻高复杂度、高抽象度、涉及操作系统内核、并发时序与顶层架构的重大决策；
  - 遵循“君子不器、统帅不役”原则，配额珍贵，严禁滥用于琐碎文本搬运。
- **高速创作与高频伴读专席 (High-Throughput Tier)**：
  - 绑定高吞吐、大上下文容量且配额充沛的模型（如 Gemini 3.1 Pro、Flash 系列）；
  - 专攻海量文本切片审读、万字文学与场景生成、高频次陪伴互动与常态化报告分析；
  - 充分释放百万上下文容量，保障流畅不间断的高效产出。

---

## 五、 核心架构组件与链路拓扑

| 组件名称 | 物理路径 | 核心职责 |
| :--- | :--- | :--- |
| **多插槽常驻网关** | `d:\maid-coding-space\argon_anti_bridge\bridge_server.py` | 监听 `8790` 端口，维护 Ticket 事务插槽注册表，执行**微秒级原子取件防重锁**，协调长轮询与载荷分发。 |
| **第六代智能中继脚本** | `d:\maid-coding-space\argon_anti_bridge\argon_commander.user.js` (v6.0+) | 注入 Chrome 网页沙箱，执行特权 IPC 脉冲、**50ms 状态机精准防吞点火与单次确定性原子击发 (250ms Anti-Debounce)**、**`compareDocumentPosition` 交织思考跨块 DOM 缝合**、单调回合守卫与行尾信标极速直通。 |
| **阻塞投递执行器** | `d:\maid-coding-space\argon_anti_bridge\send_to_argon.py` | 默认 `--wait` 阻塞长轮询；全面践行内存纯文本内联（In-memory Markdown Inlining）；统帅回传后子进程 `exit(0)` 触发 Antigravity 原生 Reactive Wakeup。 |
| **前置握手巡检工具** | `d:\maid-coding-space\argon_anti_bridge\check_handshake.py` | 毫秒级三方巡检：网关健康（未运行自动拉起）、专属标题匹配的活跃标签页在线状态与心跳。 |
| **跨桌面油猴更新器** | `d:\maid-coding-space\argon_anti_bridge\open_userscript_install.py` | Win32 底层穿透隔离桌面沙盒与前台焦点锁，置顶唤起 Chrome 原生油猴安装与更新页面。 |
| **专属会话绑定配置** | 工作区根目录 `.aistudio_config.json` | 持久化存储本项目配对的 AI Studio 专属会话标题，支持 1-to-1 精准单播防串扰。 |

---

## 六、 标准作业程序 (SOP)

### 步骤 0：前置交互式引导配置与门禁校验 (Pre-Flight Guided Binding & Handshake)

执行官**严禁在未经会话确认的情况下盲目发信**，必须严格遵循以下门禁：

1. **会话配置核验**：
   - 当主君提及“发给 aistudio”、“呈报统帅”、“AFL 协同”、“请旨”时，智能体首步核验当前工作区根目录下是否存在 `.aistudio_config.json` 且包含有效 `target_title`。
2. **未绑定时的温柔引导交互**：
   - 若未检测到绑定配置，智能体**严禁擅自猜测或盲目广播**，主动向主君请示：
     > “主君，当前工作区尚未绑定专属 AI Studio 会话。请问您希望将本项目与 AI Studio 中的哪一个会话窗口进行配对？（例如：`统帅` 架构专席、`高速伴读` 创作专席等）”
3. **自动写入配置与握手巡检**：
   - 在主君指定会话标题后，智能体自动在工作区根目录下写入 `.aistudio_config.json` 并运行握手巡检：
     ```powershell
     python d:\maid-coding-space\argon_anti_bridge\check_handshake.py
     ```
4. **三方全绿后正式启程发信**：
   - 唯有在握手巡检确认链路畅通且目标标签页在线后，方可进入胶囊投递；
   - 支持通过发信参数 `--target-title "<会话标题>"` 进行临时会话动态分流。

---

### 步骤 1：现场深度勘查与宗师级咨询胶囊打包 (Grandmaster Capsule Formulation)

执行官采集一手现场数据，严禁空泛描述。将取证内容编写为 Markdown 胶囊（如 `d:\maid-coding-space\argon_anti_bridge\data\antigravity_outgoing_consult.md` 或专属文件），格式必须严格遵循**宗师级胶囊结构**：

```markdown
# 【AFL 战略咨询胶囊 · 事务请求】

## 一、 呈报对象与元数据
- 呈报对象：Argon 首席系统架构师与三军总指挥
- 呈报端：Antigravity Flash 3.8 High 工程特遣官
- 关联会话：<会话标题>
- 咨询议题：<议题名称>

## 二、 现场物理根因穿透取证 (Root-Cause Autopsy)
- 真实报错堆栈 / 异常现象详细切片；
- 现场状态机、内存或时序分析；
- 关键代码与上下文锚点。

## 三、 已证伪之死路与边界禁区 (Eliminated Dead-Ends)
- 已经尝试但失败的方案及其物理原因（杜绝统帅重蹈覆辙）。

## 四、 顶层架构请旨核心议题 (Decision Requests)
- 议题 1：...
- 议题 2：...

<!-- [AFL_EOF_ACK] -->
```

> [!IMPORTANT]
> 胶囊末尾最后一行建议显式附带 `<!-- [AFL_EOF_ACK] -->` 完结信标，以便统帅在下达裁决方案的最末行原样回赐该信标，瞬间触发本地零延迟极速直通回传！

---

### 步骤 2：全后台单播投递、内存纯文本内联与原生 Reactive Wakeup 阻塞等待 (Zero-Contact Dispatch & Blocking Wakeup)

#### 1. 基础纯文本胶囊投递：
```powershell
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <咨询Markdown文件路径> --wait
```

#### 2. 内存纯文本内联模式（超万字长文本与多工程源码强烈推荐）：
在案前策展时，将待呈报的工程源码（如 `.cs`, `.py`, `.vue` 等）与长文本上下文在本地内存中直接拼接内联入 Markdown 咨询胶囊中（以标准 Markdown 代码块包裹并注明文件路径），通过 `--file` 一键统投：
```powershell
# 纯文本直接注入输入框，彻底规避平台内部上传锁与 DOM 重构摧毁输入框的物理深坑
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <包含内联工程源码与上下文的Markdown文件> --wait
```

#### 3. 临时指定算力分层目标单播路由：
```powershell
python d:\maid-coding-space\argon_anti_bridge\send_to_argon.py --file <咨询Markdown> --target-title "高速伴读专席" --wait
```

- **底层闭环时序**：
  1. 脚本将胶囊推入网关，分配独占 `ticket_id`；
  2. 脚本在本地挂起长轮询请求 `/api/agent/wait_task?ticket=<ticket_id>`；
  3. 执行官或主对话直接结束当前工具调用，**无需进行任何盲目轮询**；
  4. 目标 AI Studio 标签页油猴脚本原子拉取任务，通过 **50ms 状态机精准防吞点火与单次原子击发** 驱动模型生成；
  5. 模型生成完毕，油猴脚本通过 **`compareDocumentPosition` 穿透缝合交织思考跨块文本**；
  6. 命中 `[AFL_EOF_ACK]` 尾部信标或静默倒计时结束，油猴脚本毫秒级回传网关；
  7. 网关触发专属 Event，长轮询请求立即响应返回；
  8. 脚本子进程以 `sys.exit(0)` 退出，触发 Antigravity 原生 Reactive Wakeup 自我苏醒！

---

### 步骤 3：智能双模输出接令与【专属落盘文件第一反射】 (Dual-Mode Intake & First Reflex)

当执行官被 Reactive Wakeup 唤醒后，根据批复字符量执行精准闭环：

- **短文直读（≤ 2500 字符）**：
  - 批复全文已完整打印在 `send_to_argon.py` 终端输出（stdout）中；
  - 执行官无需调用文件读取工具，直接依据终端回显内容推进工程落地。
- **长文展卷第一反射（> 2500 字符）**：
  - 终端输出将展示前 500 字符摘要，并明确提示专属落盘文件绝对路径：`d:\maid-coding-space\argon_anti_bridge\data\tasks\<ticket_id>_reply.md`；
  - **【第一反射铁律】**：智能体苏醒后的**第一个工具调用必须且只能是使用 `read_file` 完整读取该专属 `tasks/<ticket_id>_reply.md` 文件**！严禁仅凭 500 字摘要盲目修改代码！

---

### 步骤 4：本地原子化施工与公子实机测试闭环 (Master Verification & Sovereign Autonomy)

- 严格遵循《D:\maid-coding-space\编码常见错误文档.md》，落地代码并运行静态编译或语法检查；
- 绝不主观臆断，向公子温言呈报修改摘要与技术细节，请公子进行实机测试验收，将最终闭环权交还公子。

---

## 七、 油猴脚本跨桌面安装与更新标准作业 (Tampermonkey Installation & Update SOP)

当巡检提示油猴脚本需更新或用户要求部署最新脚本时，智能体**严禁使用任何 `Start-Process` 或临时脚本**，必须且只能执行：

```powershell
python d:\maid-coding-space\argon_anti_bridge\open_userscript_install.py
```

- 脚本通过 Win32 API 跨越桌面沙盒与焦点锁，在主交互屏幕置顶打开 Chrome 浏览器的油猴安装页；
- 智能体向主君温声引导：
  > “已为公子在 Chrome 中置顶打开油猴脚本安装页面。请公子移步浏览器，在页面中央点击绿色的【Install】（安装）或【Update】（更新）按键完成部署，随后刷新 AI Studio 页面即可。”
- 公子安装完成后，运行 `python d:\maid-coding-space\argon_anti_bridge\check_handshake.py` 确认状态全绿。

---

## 八、 常见故障诊断与自愈矩阵 (Troubleshooting & Self-Healing Matrix)

| 异常现象 | 物理根因 | 自愈与解决对策 |
| :--- | :--- | :--- |
| **8790 端口未响应或报 Connection Refused** | `bridge_server.py` 未常驻运行 | 运行 `check_handshake.py`，脚本将自动在后台拉起网关服务，或手动运行 `start_bridge.bat`。 |
| **巡检显示 AI Studio 标签页未找到** | Chrome 未打开 AI Studio，或页面标题与配置不匹配 | 检查 Chrome 是否打开了对应的 AI Studio 会话；核对 `.aistudio_config.json` 中的 `target_title`。 |
| **Run 按钮未被触发或输入被吞** | 前端 Tokenizer 词元解析延迟，或处于 `disabled` 状态 | AFL v6.0.7 引入 **50ms 状态机精准防吞点火与单次确定性原子击发 (250ms Anti-Debounce)**，在解禁瞬间微秒点击并锁定点火状态，彻底杜绝发件吞没与并发重发风暴。 |
| **长篇回复或文学正文前半部分丢失** | 现代模型交织思考（Interleaved Thinking）导致多 DOM 容器分裂，误抓末尾块 | AFL v6.0+ 采用 **`compareDocumentPosition` 穿透算法**，全量缝合本轮 User Prompt 后的所有文本块。 |
| **海量长文本与多工程源码投递异常** | 模拟伪造文件上传触发平台内部上传锁、格式白名单拦截与 DOM 节点动态销毁重构 | 严格遵循 **内存纯文本内联规范（In-memory Markdown Inlining）**，在本地将代码与上下文编织入 Markdown 胶囊直接打入输入框，彻底规避 DOM 撕裂与上传锁。 |
| **多标签页并发时任务被重复执行** | 网络轮询窗口期多标签页同时命中待发任务 | AFL v6.0+ 网关层内建 **微秒级原子取件锁**，单标签页一旦匹配立即原子锁定状态，彻底阻断重试风暴。 |
| **正文中提到 `[AFL_EOF_ACK]` 提前中断回传** | 未对信标进行行尾严格锚定导致早泄 | AFL v6.0+ 采用 `AFL_EOF_ACK_REGEX` 严格行尾锚定，中间文本出现的信标被安全忽略。 |
| **AI Studio 页面后台停止响应或点火停摆** | Chrome 窗口被最小化，Windows DWM 停止 GPU 视口绘制并剥离渲染表面导致 Angular 脏检查与 DOM 停摆 | 坚守 **第二桌面常驻铁律**：将 Chrome 放置于 Windows 第二虚拟桌面展开常驻，坚决禁止最小化窗口。 |
