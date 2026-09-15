# TASK_STATE_MACHINE.md — 通用 Agent Task 生命周期状态机（机制层）

**适用范围**：与同目录 `AGENTS.md` 配套使用。  
**状态机版本**：`TSM-2`  
**配套数据契约**：`SCHEMA.md`  
**配套触发纪律**：`OPERATING_RULES.md`（条件触发细节；入口见 `AGENTS.md` §5 触发索引表）  
**适用对象**：每个 Top-Level Session 对应的唯一 Task。

本文件只定义**机制**：状态、进入条件、退出条件、写入时机和用户门控。纪律性条款（该不该做、往哪走）在 `AGENTS.md`；条件触发的执行细节在 `OPERATING_RULES.md`；具体字段、ID 与记录模板统一由 `SCHEMA.md` 定义。

---

## 0. 核心不变量

### I1. Top-Level Session = Task
一个 Top-Level Session 只有一个 Task；Task 内可以有多个 Round。
**例外（续接）**：用户首句提及已有任务并双次确认继续时，该会话**不建立新任务**，直接续接旧任务（判定与协议见 `OPERATING_RULES.md` §2；本状态机的 S0 仅适用于"新建任务"路径）。

### I2. Plan 是施工授权边界
没有用户明确批准的精确 Plan Revision，不得进行实质施工。只读调查与不会改变业务/项目/外部状态的低风险验证可以在 Plan 批准前进行。

### I3. CurrentState 是唯一当前真相
`task_current_state.md` 可覆盖，且必须与当前实际状态一致。

### I4. History 是不可变快照账本
`task_history.md` 只追加不回写。每个 History Entry 的 Snapshot Body 必须完整转写当时的 `task_current_state.md`。

### I5. Case 只由用户显式触发
Case Review 是用户触发的旁路流程（纪律与触发约束见 `AGENTS.md` §3.5；本状态机仅提供旁路机制，见 §13）。

### I6. 用户批准不能由模型推定
沉默、换话题、继续提供信息、仅确认需求理解，都不等于批准 Plan。

### I7. Scope Change 必须重新审批
任何超出当前 Approved Plan 的新增目标、交付物、重大约束或路线变化，都必须返回规划流程。

### I8. Long Ledger = Search First
查阅 `plan.md` / `task_history.md` 时必须先根据 CurrentState 中的 ID/Subject 使用 grep、rg、宿主搜索或等效索引定位，再局部读取记录块。默认禁止全量读取。

### I9. Project Baseline 保持 canonical location
状态机不得把既有项目源码、配置或共享资产迁入 Task 目录。Task 目录只承载本轮新增的 Task-local 资产和生命周期记录。

---

## 1. 状态总览

```text
TASK_ONBOARDING
      ↓
REQUIREMENTS_CONFIRMATION
      ↓ 用户确认需求理解
PLAN_DRAFTING
      ↓ Proposal 已 append
AWAITING_PLAN_APPROVAL
   ↙                    ↘
拒绝                    批准
 ↓                       ↓
REQUIREMENTS_CONFIRMATION IMPLEMENTATION
                           ↓
                    DELIVERY_AND_STATE
                           ↓
                   AWAITING_ACCEPTANCE
                    ↙            ↘
             不满意/返工          满意
                 ↓                 ↓
          SNAPSHOT_TO_HISTORY  SNAPSHOT_TO_HISTORY
                 ↓                 ↓
       ┌─────────┴──────┐       ROUND_CLOSING
       │                │           ↓
  范围内返工       Scope Change      IDLE
       │                │            ↓
   REWORKING      REPLAN_REQUIRED   新需求
       │                │            ↓
       └→ DELIVERY      └→ REQUIREMENTS_CONFIRMATION
```

Case Review 是旁路流程：

```text
ANY_STATE --用户显式要求复盘/记录 Case--> CASE_REVIEW --> 返回原状态
```

---

## 2. S0 — TASK_ONBOARDING

### 进入条件
当前 Top-Level Session 首次进入实际项目任务，且**会话归属判定为"新建任务"**（归属判定见 `AGENTS.md` §1 与 `OPERATING_RULES.md` §2；判定为"续接"时不进入本状态）。

### 必须动作
0. 读取 `<PROJECT_ROOT>/TASK_INDEX.md`（若存在），确认项目内已有任务全景，避免编号冲突；按 `SCHEMA.md` TIDX-1 在任务创建时写入初始区块。
1. 按 `AGENTS.md` 确定 `PROJECT_ROOT`、`TASKS_ROOT` 与 Project Baseline 边界。
2. 创建当前唯一 Task 目录、六大子目录和 `05_docs/cases/`。
3. 初始化：
   - `plan.md`
   - `task_current_state.md`
   - `task_history.md`
4. 按 `SCHEMA.md` 初始化计数器和 CurrentState。
5. 初始状态：
   - `WORKFLOW_PHASE: REQUIREMENTS_CONFIRMATION`
   - `EXECUTION_STATUS: NOT_STARTED`
6. 不创建 Case。
7. 不搬迁 Project Baseline。

### 退出条件
目录、三本账和初始 CurrentState 均已实际落盘并读回确认。

### 下一状态
`REQUIREMENTS_CONFIRMATION`

---

## 3. S1 — REQUIREMENTS_CONFIRMATION

### 目的
在制定 Plan 前，确保 Agent 对用户真实需求、交付物、范围、硬约束与验收标准理解无误。

### Agent 必须做
1. 完整理解用户需求。
2. 必要时用只读工具检查用户已提供的文件、项目现状和可验证前提。
3. 向用户清晰复述：
   - 要交付什么；
   - 输入是什么；
   - 范围是什么；
   - 明确不做什么；
   - 关键约束；
   - 验收标准；
   - 仍存在的关键歧义。
4. 要求用户确认理解是否正确。

### 允许
在不改变业务资产、项目行为或外部状态的前提下，可以进行必要的读取、搜索、诊断和事实核验，以便形成可靠 Plan。

### 禁止
- 未经用户确认需求理解就直接写正式 Proposal；
- 把“我理解了”当作用户确认；
- 在此阶段进行实质施工；
- 为了调查而改动 canonical project files。

### 用户反馈
- **确认无误** → `PLAN_DRAFTING`
- **有偏差 / 补充 / 修改** → 继续本状态，重新确认
- **取消本轮需求** → `ROUND_CLOSING`

---

## 4. S2 — PLAN_DRAFTING

### 进入条件
用户已经明确确认 Agent 对需求的理解无误。

### 必须动作
1. 分配或更新 Round / Plan / Revision ID。
2. 按 `SCHEMA.md` 生成自包含 Proposal。
3. 将 Proposal **append** 到 `05_docs/plan.md`。
4. 写入状态 `AWAITING_APPROVAL`。
5. 不修改历史 Proposal。
6. 向用户提交该精确 Revision 供审批。

### CurrentState
更新：
- `WORKFLOW_PHASE: AWAITING_PLAN_APPROVAL`
- `PLAN_LIFECYCLE_STATUS: AWAITING_APPROVAL`
- `ACTIVE_PLAN_REF: <精确 Revision>`
- `EXECUTION_STATUS: NOT_STARTED`

### 下一状态
`AWAITING_PLAN_APPROVAL`

---

## 5. S3 — AWAITING_PLAN_APPROVAL

### A. APPROVED
只有用户明确表达批准当前精确 Proposal Revision 时成立，例如“批准”“按这个计划执行”“plan 没问题，开始吧”等语义等价的明确肯定。

动作：
1. 向 `plan.md` append `REVIEW: APPROVED`。
2. Review 绑定精确 `TARGET_REVISION`。
3. 更新 CurrentState：
   - `PLAN_LIFECYCLE_STATUS: APPROVED`
   - `APPROVAL_REF`
   - `WORKFLOW_PHASE: IMPLEMENTATION`
   - `EXECUTION_STATUS: IN_PROGRESS`
4. 进入 `IMPLEMENTATION`。

### B. REJECTED
用户明确不批准，或指出计划需要修改。

动作：
1. 向 `plan.md` append `REVIEW: REJECTED`。
2. 保留原 Proposal，不回写。
3. CurrentState 标记：
   - `PLAN_LIFECYCLE_STATUS: REJECTED`
   - `EXECUTION_STATUS: NOT_STARTED`
4. 回到 `REQUIREMENTS_CONFIRMATION`。
5. 再次确认更新后的用户意图。
6. 新 Proposal / Revision 必须追加到文件末尾。

### C. 用户补充新要求但没有明确批准
当前 Revision 仍视为**未获批准**。返回 `REQUIREMENTS_CONFIRMATION`，不得自行把补充内容合并后直接施工。

---

## 6. S4 — IMPLEMENTATION

### 进入条件
存在用户明确批准的精确 Plan Revision 和 Approval Ref。

### 基本纪律
1. 严格按 Approved Plan 施工。
2. 不得静默扩大范围。
3. 任何实质偏差必须区分：
   - **范围内实现调整**：不改变目标、交付物和关键约束，可继续；
   - **Material Scope Change**：暂停并进入 `REPLAN_REQUIRED`。
4. 修改 Project Baseline 时在其 canonical path 上做最小必要修改。
5. Task-local 过程产物按 `AGENTS.md` 路由。
6. 验证按 Approved Plan 与项目既有规则执行。
7. Human Acceptance 不得由 Agent 代签。

### CurrentState
施工过程中可覆盖更新 CurrentState，用于记录：
- 当前步骤；
- 已完成步骤；
- Blocker；
- 实际偏差；
- 修改的 canonical paths；
- Safe Resume Point。

### 施工完成
完成本轮可交付施工和必要 Agent 侧验证后：
1. 独立正式候选产物放入 `06_outputs/`；若交付是既有项目代码/配置修改，则保持 canonical path，不强制复制。
2. 覆盖 `task_current_state.md`，完整记录：
   - Approved Plan Ref；
   - 实际完成内容；
   - 修改/交付路径；
   - 验证结果；
   - 未验证项；
   - 已知问题；
   - 当前等待用户验收。
3. `WORKFLOW_PHASE: AWAITING_ACCEPTANCE`
4. 进入 `DELIVERY_AND_STATE`。

---

## 7. S5 — DELIVERY_AND_STATE

### 必须动作
1. 向用户交付候选结果。
2. 明确给出独立产物路径，或对代码/配置任务给出 canonical 修改路径。
3. 明确哪些验证已完成、哪些需要用户人工验收。
4. 确认 `task_current_state.md` 已实际落盘并读回。

### 下一状态
`AWAITING_ACCEPTANCE`

---

## 8. S6 — AWAITING_ACCEPTANCE

### A. 用户验收合格

动作顺序固定：

0. **文件归属结算**（`OPERATING_RULES.md` §5.3）：列出未定归属文件，用户裁决，结果写入 FILE_INDEX.md——在冻结 CurrentState 之前完成。
1. **冻结当前 CurrentState 内容。**
2. 按 `SCHEMA.md` 创建 History Entry Envelope，`REASON: USER_ACCEPTED_DELIVERY`。
3. 将冻结的 `task_current_state.md` **完整原文**写入 History Snapshot Body。
4. 将整条 History Entry append 到 `task_history.md`。
5. 不修改任何旧 History。
6. 更新 CurrentState 为：
   - `WORKFLOW_PHASE: IDLE`
   - `EXECUTION_STATUS: COMPLETED`
   - `CURRENT_STEP: none`
   - `BLOCKERS: none`
   - `NEXT_ACTIONS: 等待用户下一指令`
   - 保留最近的 Round / Approved Plan / Approval / Final Artifact 或 canonical change 引用。
7. 按 Schema 向 `plan.md` append Round Close（若该 Schema 版本要求/推荐）。
8. 进入 `IDLE`。

### B. 用户验收不合格，但反馈仍在 Approved Plan 范围内

动作：
1. 冻结当前 CurrentState。
2. 完整转写到 `task_history.md`：
   - `REASON: USER_REJECTED_DELIVERY`
   - Snapshot Body = 完整 CurrentState。
3. 覆盖 CurrentState：
   - `WORKFLOW_PHASE: REWORKING`
   - `EXECUTION_STATUS: IN_PROGRESS`
   - 记录用户反馈与待修复项。
4. 不需要新 Plan。
5. 进入 `REWORKING`。

### C. 用户反馈构成 Scope Change

例如：
- 新增原 Plan 没有的交付物；
- 改变核心目标；
- 新增重大约束；
- 改变关键路线；
- 要求执行此前明确 Out of Scope 的内容。

动作：
1. 冻结并完整转写 CurrentState 到 History：`REASON: SCOPE_CHANGE_REQUIRES_REAPPROVAL`。
2. 覆盖 CurrentState：
   - `WORKFLOW_PHASE: REPLAN_REQUIRED`
   - `EXECUTION_STATUS: PAUSED_FOR_REAPPROVAL`
3. 进入 `REPLAN_REQUIRED`。

### D. 用户意见不明确
不得猜测合格或不合格。向用户确认验收结论或需要修改的内容，保持当前状态。

---

## 9. S7 — REWORKING

### 进入条件
用户验收不合格，但要求仍属于当前 Approved Plan。

### 动作
1. 严格依据用户验收反馈修正。
2. 不重新建立 Plan。
3. 保持既有项目文件在 canonical path。
4. 如修复产生新构建/版本，按 Schema 更新引用。
5. 完成后重新执行必要验证。
6. 覆盖 CurrentState 为最新真实状态。
7. 再次交付候选结果。

### 下一状态
`DELIVERY_AND_STATE` → `AWAITING_ACCEPTANCE`

该循环可以重复任意次数。每次用户明确不接受当前交付，都必须先将当时 CurrentState 完整快照 append 到 History，再进入下一次返工。

---

## 10. S8 — REPLAN_REQUIRED

### 进入条件
施工或验收期间出现 Material Scope Change。

### 动作
1. 停止超出 Approved Plan 的施工。
2. CurrentState 记录暂停原因和 Safe Resume Point。
3. 回到需求确认流程。
4. 用户确认新需求后，Append 新 Proposal Revision。
5. 必须再次获得用户批准。

### 下一状态
`REQUIREMENTS_CONFIRMATION`

---

## 11. S9 — ROUND_CLOSING

### 触发
- 用户验收合格；
- 用户明确取消当前 Round；
- 无法继续且用户决定停止；
- 当前 Round 被新的获批 Revision/方向正式替代。

### 关闭原则
- 关闭前按 `OPERATING_RULES.md` §5.3 完成文件归属结算（先结算，后快照）。
- 按 `OPERATING_RULES.md` §3 更新 `TASK_INDEX.md` 中本任务区块（状态、阶段、交接要点、LAST_ACTIVE_AT）。
- 有实际施工/交付状态时，关闭前必须确保最后一个应保存的 CurrentState 已进入 History。
- History 只接受 CurrentState 完整快照，不另写替代性“总结历史”。
- `plan.md` 如需 Round Close Event，必须 append。
- CurrentState 最终回到 `IDLE`，等待同一 Top-Level Session 内下一 Round。

---

## 12. S10 — IDLE

### 含义
Task 仍存在，但当前没有进行中的工作项。

建议 CurrentState：
- `WORKFLOW_PHASE: IDLE`
- `EXECUTION_STATUS: COMPLETED` 或 `NOT_STARTED`
- `CURRENT_STEP: none`
- `NEXT_ACTIONS: 等待用户下一指令`
- 保留最近完成 Round 的必要索引。

### 新需求
同一 Top-Level Session 中用户提出新的独立工作要求：

1. 不新建 Task。
2. 分配新 Round。
3. 进入 `REQUIREMENTS_CONFIRMATION`。
4. 重新经过 Plan Gate。

---

## 13. CASE_REVIEW — 用户显式触发的复盘旁路

### 触发条件
只有用户显式要求复盘、记录 Case 或沉淀经验（触发约束见 `AGENTS.md` §3.5）。

### 动作
1. 记录进入 Case Review 前的原状态。
2. 先完整读取 CurrentState。
3. 需要旧信息时：
   - `plan.md` → Search First / Read Narrow；
   - `task_history.md` → Search First / Read Narrow；
   - Evidence → 按引用读取。
4. 按 `SCHEMA.md` 检索已有 Case，避免重复。
5. 创建或修订 Case。
6. Case 内容区分事实、推断和未验证部分。
7. 完成后返回原状态。

### 禁止
- 自动触发 Case；
- 因为 Bug 出现就默认写 Case；
- 为填充知识库而制造 Case。

---

## 14. 上下文恢复协议

当发生上下文压缩、模型切换、中断恢复、Agent 更换或子 Agent 接手时：

### 必须顺序
1. 获取/确认 `PROJECT_ROOT` 和当前 Task 根路径。
2. 读取 `AGENTS.md` 中与当前动作相关的规则；若宿主已明确注入本文件，可不重复整读。
3. 搜索并局部读取 `TASK_STATE_MACHINE.md` 的当前状态章节。
4. **完整读取 `05_docs/task_current_state.md`。**
5. 从 CurrentState 获取：
   - `ROUND_ID`
   - `ACTIVE_PLAN_REF`
   - `APPROVAL_REF`
   - `WORKFLOW_PHASE`
   - `EXECUTION_STATUS`
   - `SAFE_RESUME_POINT`
   - 当前 Subject / Artifact Ref / History Ref
6. 对 `plan.md`：
   - 先搜索精确 Plan / Approval ID；
   - 再局部读取对应记录块。
7. 对 `task_history.md`：
   - 仅在确需历史上下文时搜索；
   - 按 Round / Plan / Subject / Reason / Entry ID 定位；
   - 局部读取必要 Snapshot。
8. 不得默认全量读取长期账本。
9. 恢复后从 `SAFE_RESUME_POINT` 继续，禁止重复生成已存在的 Proposal / History Entry / 正式 ID。

> 本节适用于**任务内**恢复（同一任务的对话/压缩/子代理场景）。**跨任务场景**（新会话续接旧任务）不适用本节——归属判定与续接协议见 `OPERATING_RULES.md` §2，索引读取见 `AGENTS.md` §1。

---

## 15. 异常与中断

### 工具失败
读取真实错误，改变方法或输入后再尝试；不得在条件不变时机械重试。工具失败不改变 Plan 授权边界。

### 中途崩溃
`task_current_state.md` 的当前状态和 Safe Resume Point 是恢复权威。

### Append 结果不确定
如果无法确认 Append 是否成功：
1. 搜索目标 ID；
2. 确认记录是否已存在；
3. 只有确认不存在才重新追加；
4. 禁止盲目重试导致重复记录。

### 用户要求立即停止
停止施工，更新 CurrentState；如已有需保留的实际状态，按 Schema 转写 History，然后进入 Idle 或等待用户后续指令。
