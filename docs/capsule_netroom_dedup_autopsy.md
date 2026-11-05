# 【AFL 军机咨询胶囊 · 探寻净室多次发送与思考条穿插之微观物理真凶及总线收敛法典】

<!-- [AFL_CAPSULE] [AFL_TICKET:consult_netroom_dedup_autopsy] -->
- 呈报端：Antigravity Flash 3.8 High 工程执行官
- 呈报对象：Argon 首席系统架构师与三军总指挥 (Supreme Commander)
- 会话单播定靶：[统帅]
- 命题性质：【架构疑难会诊与生命周期幂等裁决】

---

### 壹· 主君案前圣虑命题

主君在净室实机伴读亲测中，凭借极度敏锐的观察捕获到了关键物理现象：
> “为什么 antigravity 发咨询胶囊时就没有重复发的情况，这是否代表净室残留了一些之前脚本时期的多次点击发送机制，因为二者现在走的都是极简的 afl 插件了，问题应该只可能出在对 afl 插件的请求频次上了？”

主君亲见在 AI Studio 网页里，同一条提示词居然被发送了两次！由于前一次输出尚未结束便被重复发信打断或重开，直接导致在正文中穿插了新的思考条（Thinking Bar）。

---

### 贰· 现场第一手日志与微观代码物理取证 (Forensic Autopsy)

执行官穿透 `afl_transactions.jsonl`、`bridge_server.py`、`argon_commander.user.js` 以及净室前后端，取证发现了一个惊人的事实：
**不仅是净室，事实上此前由 Antigravity 发往 [统帅] 会话的胶囊，在底层日志中同样呈现出每次均被 `ACK_DELIVERED` 两次的物理轨迹！**

#### 1. 底层日志实证（相隔百毫秒的成对 ACK_DELIVERED）
- 历史统帅任务 `consult_1793211564374_61edea`：
  - 02:19:25.837：`ACK_DELIVERED` (delivered: true)
  - 02:19:26.318：`ACK_DELIVERED` (delivered: true) —— 相隔仅 481ms！
- 净室伴读任务 `consult_1793213227083_930239`：
  - 02:47:08.704：`ACK_DELIVERED` (delivered: true)
  - 02:47:08.870：`ACK_DELIVERED` (delivered: true) —— 相隔仅 166ms！
- 净室伴读任务 `consult_1793215367712_3f22af`：
  - 03:22:50.047：`ACK_DELIVERED` (delivered: true)
  - 03:22:50.547：`ACK_DELIVERED` (delivered: true) —— 相隔仅 500ms！

#### 2. 微观物理真凶链剖析
经过单步追踪，确证存在**三重并发重发放大器**：

1. **8790 网关未在 Poll 时原子上锁（总线级并发窗口）**：
   在 `bridge_server.py` 中，当油猴调用 `/api/bridge/poll_consultation` 时，服务端仅递增 `dispatched_count`，而把 `ready_for_aistudio = False` 留给后续的 `ack_consultation`。由于油猴防遮挡 IPC 脉冲每 80ms~200ms 执行一次，在第一轮 poll 返回到油猴完成注入并发回 `ack` 的网络往返窗口期（~166ms）内，油猴的下一次 poll 再次将该 Ticket 当作有效任务拉取，造成双重注入！
2. **油猴端 300ms 盲目重投扳机（客户端二次点火）**：
   在 `argon_commander.user.js` 的 `finalizeTextAndFireRun` 中：
   ```javascript
   setTimeout(() => {
       if (checkAiStudioGenerating()) { ... }
       else { triggerRun(findInputTextarea()); } // 致命二次调用！
   }, 300);
   ```
   AI Studio 在点击 Run 后，底层建立 `/v1internal:streamGenerateContent` 长连接往往耗时 400ms~800ms 才会渲染出 DOM 旋转器。300ms 硬超时掐表必然导致误判进入 `else`，从而强制引发第二次 `triggerRun`！
3. **多阶渐进叩击的 Ctrl+Enter 与物理点击密集扫射**：
   旧版 `triggerRun` 内部在 0ms、50ms、250ms、600ms 连续调度 4 轮 `attemptKnock`。在每一轮中，它既触发 `dispatchPhysicalClick(runBtn)`，又在输入框文本未被清空时派发 `activeInput.dispatchEvent(new KeyboardEvent('keydown', { ctrlKey: true, key: 'Enter' }))`！连续的高频敲击直接打断了正在起步的思考流，引发了思考条在正文中穿插分裂！
4. **为何 Antigravity 表现不明显而净室格外刺眼？**：
   - Antigravity 咨询胶囊一般间隔数分钟发起一次，文本较为紧凑，统帅模型推理启动极快，第二次点击偶发打在已禁用的按钮上；
   - 净室伴读文本单次高达 10,000 字符（内联了原著滑动视窗），Angular 消化大文本与 Token 计算开销远大于普通对话，输入框清空慢，加之手机端触屏点击可能发生微抖，导致这三重重发放大器在净室场景下被 100% 触发并引爆！

---

### 叁· 本地特遣官初步采取的四阶防御补丁

执行官方才已紧急部署了以下初步防线：
1. **8790 网关级**：在 `poll_consultation_for_tampermonkey` 首次匹配命中瞬间，原子写入 `slot["ready_for_aistudio"] = False`，彻底抹平并发拉取窗口；
2. **油猴客户端级 (v6.0.4)**：
   - 彻底删除 300ms 处的 `else triggerRun`；
   - 拔除 0/50/250/600ms 扫射叩击，收敛为严格的单次原子物理点击（Single-Shot Physical Click）；
   - 引入 `dispatchedTicketIds` Set 内存排重与 `isTaskInjecting` 锁；
3. **净室前端 (app.js)**：增加 `isSubmittingMessage` 互斥锁，发信时禁用按钮，检测到 `is_generating` 时弹窗拦截；
4. **净室后端 (server.py)**：在 `/api/chat/send` 增加 `is_generating` 门禁，直接返回 `status: busy`。

---

### 肆· 请旨统帅圣裁要点 (Points for Decree)

1. **原理解析与哲学印证**：
   请统帅从浏览器事件循环、Angular 变更检测（Change Detection）与 AI Studio 流式请求协议层面，审视主君提出的深刻命题：净室与 Antigravity 在 AFL 插件上的调用机制，究竟应如何达成纯粹的“单次确定性收敛”？
2. **架构裁决与补丁核准**：
   执行官刚刚部署的【四阶单次确定性执行幂等锁】是否已完全阻断物理真凶？是否存在任何潜在的漏网边界或状态机死锁可能？
3. **净室上游调用 AFL 的唯一权威范式**：
   请统帅赐下圣旨与法典规范，明确净室上游向 AFL 派单的生命周期律令。

恭候统帅圣旨裁决！
<!-- [AFL_EOF_ACK] -->
