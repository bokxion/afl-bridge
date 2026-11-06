---
name: aistudio
description: 当用户提到 aistudio、呈报 aistudio、发给 aistudio、AFL、统帅咨询、请旨 Argon、呈报 Argon、咨询 Argon、领旨、双端协同直连时激活。提供 AFL (Argon-Flash Link) v6.1.0 全后台零接触穿透、多会话定向单播与算力分层拓扑机制，包含通用解耦草稿箱模式与法定前置契约约定(Mandatory Inbox Contract Agreement Protocol)、长文本与工程源码内存纯文本内联(In-memory Markdown Inlining)、50ms状态机精准防吞单次原子点火与250ms防抖、第二桌面常驻展开或深水离屏调度(-32000)、交织思考跨块DOM全量缝合(compareDocumentPosition)、微秒级原子防重、原生 Reactive Wakeup 阻塞唤醒、双模闭环输出与专属落盘第一反射，以及跨桌面油猴无损安装。
---

# AFL (Argon-Flash Link) 协同与 AI Studio 多会话定向直连规范 (v6.1.0 工业级权威大正本)

本技能专为 **AI Studio (Argon/Gemini 云端模型集群)** 与 **Antigravity (Flash 执行官)** 之间的高维人机协同直连架构而设计。依托 **原生 Reactive Wakeup 阻塞唤醒**、**多会话 1-to-1 定向单播矩阵**、**算力分层拓扑 (Tiered Model Topology)**、**通用解耦草稿箱模式与法定前置契约约定 (Generic Decoupled Inbox & Mandatory Contract Protocol)** 以及 **第六代油猴中继韧性准则 (AFL Userscript v6.1.0 Resilience Standard)**，彻底终结人工复制粘贴、手动拖拽与盲目掐表等待，实现全天候、全后台、高吞吐、无人值守的工业级双端一体化协同闭环。

---

## 一、 架构禁区与核心铁律 (Architectural Invariants & Redlines)

1. **绝对禁绝 `/browser` 与 Selenium 类自动化**：
   - 严禁使用任何浏览器自动化指令（如 `/browser`）直接访问或操作 AI Studio 网页。
   - 所有浏览器 DOM 交互与事件派发，均由运行在宿主 Chrome 内的原生油猴脚本 `argon_commander.user.js` 在沙箱内自主闭环。
2. **全面废黜 CDP UI 模拟注入**：
   - 彻底停用脆弱的 CDP UI 模拟注入机制，确立 **原生 Reactive Wakeup 阻塞长轮询子进程** 为唯一回传唤醒正朔。
3. **1-to-1 星宿并发与 Ticket 事务隔离**：
   - 每次咨询投递，网关派发全局唯一的事务令牌 `ticket_id`（Ticket），并构建私有的 `threading.Event()` 与专属落盘路径 `data/tasks/<ticket_id>_reply.md`。
   - 浏览器端油猴脚本严格执行单播持牌与带牌核销，各会话标签页互不干扰、并行不悖。
4. **拒绝硬编码掐表，状态驱动感知 (Zero-Blind-Wait State Machine)**：
   - 严禁使用盲目的 sleep 或硬超时作为生成结束判断依据；
   - 采用 **纯内存状态机 + 完结信标极速短路 + 静默倒计时（2200ms）兜底** 双轨感知，确保答复完整无损。
5. **严禁孤儿后台盲目转发 (Ban on Detached Blind Background Daemons)**：
   - 明令严禁私自启动脱离主意识的后台硬轮询盲转脚本（如 `watch_*`、`forward_*`）私自截胡发件。
   - 外部业务数据必须经由契约草稿箱暂存，由案前主智能体实施受控调度，杜绝脱缰脚本破坏状态机时序。
6. **显式策展与调度权守卫 (Explicit Curation & Scheduling Ownership)**：
   - 投递调度权必须牢牢掌握在主智能体手中。由智能体在案前显式读取草稿、进行上下文核验与提示词策展，通过 `send_to_argon.py --target-title <目标会话标题> --wait` 实施受控阻塞投递；收到响应后完成清洗并写回业务子系统的归档卷帙中。
7. **草稿箱前置契约约定铁律 (Mandatory Inbox Contract Agreement Protocol)**：
   - 任何前端服务程序、独立 UI 终端、移动端业务模块或微服务后台，凡需经由 Antigravity 调度转发至 AI Studio，**必须在系统接入或功能初始化之初，显式与 Antigravity 案前主智能体约定并配置标准化的草稿箱路径（例如工作区约定的 `data/<service_name>_inbox/` 专用目录）**，方允许启动消息转发与提问提交流程；
   - **严禁无契约转发与野蛮落盘**：严禁在未与 Antigravity 显式对齐草稿箱路径的情况下擅自生成临时文件或盲目分发；严禁前端直接跨层绕过 Antigravity 去强行触碰 AI Studio 网关。草稿箱路径的显式约定是建立“前端毫秒级释放、案前智能体显式策展、双向响应式闭环回传”的法定前置准入契约。
8. **窗口保活铁律（坚决禁止最小化）**：
   - Windows DWM 在窗口最小化时会立即停止 GPU 视口绘制并剥离渲染表面，导致宿主浏览器冻结内部事件循环，使 Angular 脏检查、Tokenizer 词元计数与 DOM 渲染彻底停摆；
   - 宿主 Chrome 必须永久常驻置于 **Windows 第二虚拟桌面展开运行**，或通过 `python src/background_window.py --offscreen` 将专用窗口平移至 **坐标深水区 (-32000, -32000)**，绝对禁止最小化窗口。

---

## 二、 AFL v6.1.0 油猴中继韧性准则 (Userscript v6.1.0 Resilience Standard)

### 1. 50ms 状态机精准防吞点火与单次确定性原子击发 (Single-Shot Physical Click & 250ms Anti-Debounce)
- **微观物理痛点根除**：旧架构在注入文本后使用盲目的掐表硬等待（如 `setTimeout 300ms else triggerRun`）或 15x150ms 盲发，常因大文本注入后 Angular Tokenizer 词元计算耗时 400ms~800ms，导致误判进入 else 触发第二次点火，引爆消息双发与正文中穿插思考条的故障；
- **v6.1.0 确定性单次击发机制**：
  - 彻底拔除盲目的 300ms 二次重发扳机与连续扫射叩击，收敛为每 50ms 高频侦测 Angular Tokenizer 解锁后微秒级单次物理原子点击（`dispatchPhysicalClick`）；
  - 严格配合 **250ms 防抖流控** 与 **网关微秒级单次取件原子锁**，在前端与网关形成双保险；
  - 一旦捕获到前端框架完成词元解析并剥离 `disabled` / `aria-disabled` 属性的瞬间，立即精准击发一次原子点击；若达到 300ms 仍未解锁，则通过 DOM 原生 API 强行解禁再执行受控单次点击，点击后立即锁定点火状态，从物理上彻底根除重发风暴。

### 2. 思考容器跨块 DOM 全量缝合 (Cross-Chunk Interleaved Thinking DOM Stitching)
- 针对前沿大模型交织思考（Interleaved Thinking）机制，单轮回复会被平台拆分为多个交错出现的容器（如 `ms-thought-chunk` 与 `ms-text-chunk` 轮流出现）；
- 答复提取器使用原生 DOM 树拓扑关系判别：
  ```javascript
  const targetModelContainers = lastUser
      ? modelContainers.filter(mc => (lastUser.compareDocumentPosition(mc) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0)
      : [modelContainers[modelContainers.length - 1]];
  ```
- 严格筛选位于本轮最新 User Prompt 之后的所有 Model 容器，深度剥离思考胶囊与报错节点，按物理先后顺序全量缝合正文，杜绝截断事故。

### 3. 内存纯文本内联胜过脆弱的伪造文件上传 (In-Memory Text Inlining)
- 彻底废除模拟伪造文件上传机制，全面推行 **内存纯文本内联（In-memory Markdown Inlining）** 规范；
- 对海量文本切片、前置上下文与工程源码文件（如 `.cs`, `.py`, `.vue` 等），统一在案前内存中整合成格式规范的 Markdown 纯文本（采用代码块标注文件名与语言），直接打入主输入框；
- 100% 规避平台文件上传通道的偶发卡死、白名单封禁与 DOM 重建摧毁输入框的风险，充分释放百万级上下文窗口的推演能力。

### 4. 网关微秒级原子防重与单调回合守卫 (Microsecond Atomic Lock)
- 网关（`bridge_server.py`）在轮询接口（`/api/bridge/poll_consultation`）中，引入单次执行原子互斥锁；
- 只要匹配的标签页命中任务，网关在 `with self.lock:` 保护下微秒级将 `ready_for_aistudio` 置为 `False`，彻底根除网络窗口期多标签页并发争抢的缺陷；
- 注入发件瞬间捕获当前 DOM 中的回复块基线计数，回传时强制要求 `currentModelCount >= baselineModelCount + 1`，从物理层面 100% 杜绝误抓历史陈旧回复。

### 5. 行尾绝对锚定正则与信标直通车 (`[AFL_EOF_ACK]`)
- 采用严格行尾锚定正则：
  ```javascript
  const EOF_TAIL_REGEX = new RegExp('\\[AFL_EOF_' + 'ACK\\]\\s*(?:-->)?\\s*`{0,3}\\s*$');
  ```
- 唯有信标出现在文本绝对末尾时触发零延迟极速直通车；中间引述安全忽略；回传前自动剥离信标确保正文纯净。

---

## 三、 通用解耦草稿箱模式与法定前置契约约定

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

1. **草稿箱前置契约约定铁律**：外部程序经由 Antigravity 转发至 AI Studio，必须在初始化之初显式约定标准化草稿箱路径（如 `data/<service_name>_inbox/`），严禁无契约野蛮落盘或直接越权触碰网关；
2. **轻量落盘与秒级释放**：外部端毫秒级写入草稿箱后立即释放，杜绝前台 UI 卡顿或网络超时；
3. **主智能体案前显式调度**：主智能体使用 `read_file` 查验草稿、进行提示词工程策展、发起阻塞投递，并在回传后完成清洗归档，严禁编写脱机硬轮询盲转脚本。

---

## 四、 多会话定向单播与算力分层拓扑

通过 `--target-title` 高精度单播路由，兼顾极致推演深度与大文本量创作吞吐：

- **高阶架构推演专席 (High-Reasoning Tier)**：
  - 目标标题：`"统帅"` 或架构专席名称；
  - 绑定模型：Gemini 4 Argon / Gemini Pro (Thinking Max)；
  - 专攻场景：物理根因穿透、状态机设计、复杂代码重构。
- **高速创作与伴读专席 (High-Throughput Tier)**：
  - 目标标题：`"伴读创作"` 或对应功能名称；
  - 绑定模型：Gemini 3.1 Pro / Flash 系列；
  - 专攻场景：海量文本切片审读、万字文学与场景生成、高频交互分析。

---

## 五、 标准作业程序 (SOP)

### 步骤 0：前置会话核验与便携握手巡检 (Guided Binding & Handshake)
1. **核验绑定**：检查当前工作区根目录是否存在 `.aistudio_config.json` 且包含非空 `target_title`；
2. **未绑定时温柔引导**：
   > “主君，当前工作区尚未绑定专属 AI Studio 会话。请问您希望将本项目与 AI Studio 中的哪一个会话窗口进行配对？（例如：`统帅` 架构专席、`高速伴读` 创作专席等）”
3. **写入配置并运行三方握手巡检**：
   ```powershell
   python <工程目录>/src/check_handshake.py --bind-title "<目标会话标题>"
   ```
   若已绑定，直接执行：
   ```powershell
   python <工程目录>/src/check_handshake.py
   ```
4. **全绿后启程发信**：网关运行、Chrome 在线且标签页匹配全绿后方可投递。

---

### 步骤 1：现场深度勘查与咨询胶囊打包
编写 Markdown 咨询胶囊，格式遵循宗师级结构：
```markdown
# 【AFL 战略咨询胶囊 · 事务请求】

## 一、 呈报对象与元数据
- 呈报对象：Argon 首席系统架构师与三军总指挥
- 呈报端：Antigravity Flash 3.8 High 工程特遣官
- 关联会话：<会话标题>
- 咨询议题：<议题名称>

## 二、 现场物理根因穿透取证 (Root-Cause Autopsy)
- 真实报错堆栈 / 现场切片；
- 状态机、内存或时序分析。

## 三、 已证伪之死路与边界禁区 (Eliminated Dead-Ends)
- 已排查失败的方案及物理原因。

## 四、 顶层架构请旨核心议题 (Decision Requests)
- 议题 1：...

<!-- [AFL_EOF_ACK] -->
```

---

### 步骤 2：全后台单播投递与原生 Reactive Wakeup 阻塞等待
```powershell
# 1. 常规单播投递（读取本地绑定配置）
python <工程目录>/src/send_to_argon.py --file <胶囊路径.md> --wait

# 2. 内存纯文本内联模式（超长切片与工程源码推荐，直接打入输入框）
python <工程目录>/src/send_to_argon.py --file <包含内联源码的胶囊.md> --wait

# 3. 临时指定专席单播分流
python <工程目录>/src/send_to_argon.py --file <胶囊路径.md> --target-title "<专席标题>" --wait
```
- **阻塞唤醒机理**：脚本在本地挂起长轮询，执行官结束当前步挂起；AI Studio 回传瞬间子进程以 `sys.exit(0)` 退出，触发 Antigravity 宿主内核原生 Reactive Wakeup 自动唤醒！

---

### 步骤 3：智能双模输出接令与【专属落盘文件第一反射】
- **短文直读（≤ 2500 字符）**：全文在 `send_to_argon.py` 终端 stdout 中输出，直接阅读推进；
- **长文展卷第一反射（> 2500 字符）**：终端输出前 500 字符摘要，并提示专属落盘路径 `<工程目录>/data/tasks/<ticket_id>_reply.md`；
  - **【第一反射铁律】**：苏醒后**首个工具调用必须且只能是使用 `read_file` 完整读取该专属 reply.md 文件**！严禁仅凭摘要盲目修改代码！

---

### 步骤 4：本地原子化施工与公子实机测试闭环
- 严格落地代码修改并运行语法检查；
- 施工完毕后温声向主君呈报修改摘要与技术细节，请主君进行实机测试验收。

---

## 六、 常见故障自愈指南

1. **8790 端口连接被拒绝**：`check_handshake.py` 会自动后台拉起网关，或手动运行 `start_bridge.bat`；
2. **三方巡检未找到标签页**：核对 Chrome 页面左上角标题与 `.aistudio_config.json` 是否一致；
3. **后台运行停止响应**：坚决禁止最小化 Chrome；将其移至第二虚拟桌面展开，或使用 `python <工程目录>/src/background_window.py --offscreen` 移入深水区。
