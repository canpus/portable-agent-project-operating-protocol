# PAPOP v5 是怎样工作的

[返回 README](../README.md) · [为什么要用状态机](WHY.md) · [安装指南](INSTALL.md)

本文解释状态机怎样推动一个项目、Agent 在什么状态下工作、每个文件负责什么，以及用户在各个审查点应该做什么。

## 先记住五个词

| 名称 | 大白话解释 |
|---|---|
| Workspace | 你交给 Harness 的工作区。根目录有工作区 `AGENTS.md`、`.agent-protocol/` 和 `tasks/` |
| Task | 一个完整项目。目录名类似 `task1_20260917_重写产品文档` |
| Session | 一次顶层对话。压缩后恢复、更换模型或交接也会开始新的 Session，但不会新建项目 |
| Stage | 一次可以单独计划、施工、交付和验收的周期。一个长期 Task 可以有很多 Stage |
| Checkpoint | 已由脚本写入并重新验证、以后可以用于恢复的状态点 |

层级固定为：

```text
全局规则
└── 工作区规则与默认治理模式
    └── Task（Project）
        ├── Session 1
        ├── Session 2
        └── Stage 1、Stage 2……
```

全局规则约束 Agent 在所有项目中的基本行为。工作区规则决定新 Task 默认采用 Strict Approval 还是 Autonomous。Task 创建后会把模式写进自己的 Current State；以后替换工作区 `AGENTS.md` 不会静默改变旧 Task。

## 用户看到的完整主流程

[打开原尺寸 PNG](diagrams/v5-user-workflow.png) · [查看 Mermaid 源码](diagrams/v5-user-workflow.mmd)

![PAPOP v5 用户视角项目流转图](diagrams/v5-user-workflow.png)

新对话开始时，Agent 先判断这是新项目还是继续已有 Task。继续已有项目时，新建的是 Session，不是 Task。

恢复过程先运行只读 `verify`，再读取 `goal.md`、`current_state.md`、三层 Case 索引和最近 History，并核对实际文件、diff、测试及外部状态。Agent 随后向用户复述：

- 最终 Goal；
- 当前 Stage 和 Phase；
- 已经取得的批准或授权；
- 尚未完成的工作；
- 下一步准备做什么。

用户确认这份复述正确后，Agent 才按 Task 中已经冻结的治理模式继续。

## 两种治理模式

### Strict Approval：严格审批

严格模式有四个强制人类审查点：

```text
需求讨论与澄清
→ [用户确认 Requirements]
→ Agent 写 Goal
→ [用户审批 Goal]
→ Agent 写当前 Stage Plan
→ [用户审批 Plan]
→ Agent 施工并进行机器验证
→ [用户验收 Delivery]
→ Stage 结束
→ 下一 Stage Plan
```

审查不通过时返回相应阶段：

- Requirements 不正确：继续讨论；
- Goal 表述不正确：追加新 Goal Revision；
- Plan 不可接受：追加新 Plan Revision；
- Delivery 不合格：进入返工；如果返工会实质改变已批准 Plan，先回到 Plan 审批。

批准绑定精确引用。Plan R1 获得批准，不代表 Plan R2 也自动获批；Delivery R1 被接受，也不能关闭返工后形成的 Delivery R2。

### Autonomous：自主推进

自主模式在用户明确授权整个 Task 后连续工作。Agent 可以自行整理 Goal、划分 Stage、维护 Plan、施工和运行验证。

下面这些情况仍然必须暂停：

- 缺少会实质改变结果的关键决定；
- 需要对某个外部动作作具体授权；
- 操作具有不可逆后果；
- 用户显式设置了审查或验收关卡；
- Agent 准备实质改变最终 Goal；
- Harness 自己要求真实权限审批。

如果用户没有要求验收，Stage 可以写 `ACCEPTANCE_STATUS=NOT_REQUIRED`，但不能伪造为 `ACCEPTED`。

## 你在每个节点应该做什么

| 节点 | 你需要检查什么 | 建议怎样回答 |
|---|---|---|
| 选择或创建 Task | 这是新项目，还是旧项目的继续 | “继续 `task2_...`”或“新建 Task，使用严格审批模式” |
| 恢复确认 | Goal、当前阶段、批准、未完成项和下一步是否真实 | 指出具体错误；全部正确时明确确认 |
| Requirements 确认 | 范围内、范围外、限制、交付物、验收标准是否完整 | “确认 REQ-0001”或列出要补充/删除的内容 |
| Goal 审批 | `goal.md` 中的最终结果是否正是你要的，边界是否清楚 | “批准 G-0001-R0001”或要求追加修订 |
| Plan 审批 | 每一步做什么、改哪些范围、怎样机器验证、有哪些外部动作和用户关卡 | 阅读实际 `plan.md` 后批准精确 `PLAN_REF`，或说明不批准的原因 |
| 施工中的授权请求 | 对象、动作、数据、费用、影响和可逆性是否清楚 | 只批准你理解的具体对象和范围 |
| Delivery 验收 | 实际文件、界面、报告或其他产物是否符合 Goal；测试/diff 是否真实存在 | “接受 DLV-...”或列出返工项；不要只根据 Agent 的总结验收 |
| Goal 变化 | 这是不是在改变项目最终目的，而非普通实现细节 | 同意后追加新 Goal Revision；不同意则继续原 Goal |
| Case 建议 | 是否真的是同一根因反复发生，记录是否能防止再次发生 | 同意或拒绝创建；需要时再决定是否升格 |
| 压缩前 | 当前状态是否已经通过 checkpoint 保存 | 看到 `CHECKPOINT_COMMITTED` 后再手动压缩 |
| 压缩或换模型后 | Agent 是否重新读了 Goal，并正确复述项目 | 复述正确才允许继续 |

## Agent 自己的状态和文件记录点

[打开原尺寸 PNG](diagrams/v5-agent-state-ledger-flow.png) · [查看 Mermaid 源码](diagrams/v5-agent-state-ledger-flow.mmd)

![PAPOP v5 Agent 状态与账本记录图](diagrams/v5-agent-state-ledger-flow.png)

`current_state.md` 不是只保存一个“状态名称”。下面五组字段共同决定 Agent 现在可以做什么：

| 字段 | 回答的问题 |
|---|---|
| `PHASE` | 工作流现在走到哪一步 |
| `EXECUTION_STATUS` | 当前正在执行、等待、阻塞、完成还是取消 |
| `AUTHORIZATION_STATUS` | 正在等哪一种批准，或者已经获得什么授权 |
| `AGENT_COMPLETION` | Agent 自己的施工是否完成 |
| `ACCEPTANCE_STATUS` | 用户是否已经验收当前 Delivery |

例如，在 `AWAITING_DELIVERY_ACCEPTANCE` 阶段，`AGENT_COMPLETION` 可以是 `COMPLETE`，同时 `ACCEPTANCE_STATUS` 仍然是 `AWAITING`。这表示 Agent 已经交付，但项目尚未得到用户验收。

### 严格模式的主要 Phase

```text
REQUIREMENTS_DISCUSSION
→ AWAITING_REQUIREMENTS_CONFIRMATION
→ GOAL_DRAFTING
→ AWAITING_GOAL_APPROVAL
→ PLAN_DRAFTING
→ AWAITING_PLAN_APPROVAL
→ IMPLEMENTATION
→ VERIFYING
→ AWAITING_DELIVERY_ACCEPTANCE
→ STAGE_CLOSED
```

拒绝和验证失败会进入对应的讨论、撰写或 `REWORKING`。无法继续时进入 `BLOCKED`；用户取消时进入 `CANCELLED`。

自主模式使用相同的 Phase 字段，但可以在 Task 授权后跳过严格模式的四个固定人工等待点。用户额外设置的关卡仍然有效。

## 六个核心账本

所有核心账本都在当前 Task 的 `.agent-state/` 中。

### `goal.md`：项目最终要达成什么

Goal 在最初的需求澄清后形成，通常跨多个 Stage 保持稳定。它包含最终结果、范围内外、交付物、验收标准和稳定约束。

Goal 可以修改，但不能静默覆盖。Agent 必须先明确告诉用户这会改变项目最终目标；用户同意后，追加新的 Goal Revision，并保留旧版本。

每次上下文压缩后恢复、更换模型、新 Session 或任务交接，Agent 都必须重新读取 `goal.md`，并向用户复述最终 Goal。

### `plan.md`：当前阶段准备怎样做

Plan 绑定一个 Stage 和一个 Goal Revision，包含：

- 当前阶段要交付什么；
- 施工步骤；
- 每一步怎样由脚本、测试或 diff 验证；
- 允许修改的范围；
- 用户设置的关卡；
- 需要单独授权的外部动作。

Plan 只追加。返工导致方案发生实质变化时，写新 Revision，不修改已经审批过的旧记录。

### `decisions.md`：用户真正决定了什么

Decision 只记录用户明确说出的批准、拒绝、授权、模式切换、Case 创建、Goal 改变或任务取消。

沉默、含糊回复和 Agent 自己的推断不能写成用户 Decision。每个 Decision 都绑定精确目标，例如一个具体的 `GOAL_REF`、`PLAN_REF` 或 `DELIVERY_REF`。

### `current_state.md`：现在在哪里

这是唯一允许覆写的核心账本。它保持完整但尽量短，保存当前 Session、Stage、Phase、活动 Goal/Plan、执行状态、证据、阻塞、下一动作和最近事件。

Agent 不直接写这个文件，而是生成一个待提交的 next-state，由 checkpoint 脚本校验并原子替换。

### `snapshots.md`：每次检查点的完整状态

一个 Task 只有一个持续增长的 `snapshots.md`。每次 checkpoint 都把提交后的 `current_state.md` 完整原文追加到末尾。

Snapshot 不是摘要，也不拆成很多小文件。脚本计算每个 Snapshot 块的开始行、结束行、字节数和哈希。

### `history.md`：查历史时先看这里

History 不重复保存整个项目历史正文。它是一份可搜索索引，记录：

- 关键词、主题和摘要；
- 当时的 Session、Stage、Phase 和事件状态；
- Requirements、Goal、Plan、Decision、Case 和 Input 引用；
- Snapshot 在 `snapshots.md` 中的精确起止行；
- State 与 Snapshot 哈希；
- 当时做了什么、证据在哪里、下一步是什么。

## History 怎样把过去重新拼起来

查询历史时不要先读取整个 `snapshots.md`。顺序是：

1. 在 `history.md` 中搜索主题、关键词、事件编号或状态；
2. 只读取命中的 History 块；
3. 查看其中的 `PLAN_REFS`、`DECISION_REFS`、`CASE_REFS` 和 `INPUT_REFS`；
4. 只读取对应账本中的具体记录块；
5. 需要当时完整状态时，再按 `SNAPSHOT_START_LINE` 到 `SNAPSHOT_END_LINE` 读取 `snapshots.md` 的精确范围；
6. 用哈希和实际文件核对，不盲信旧记录。

由此可以回答：当时为什么做这件事、准备怎样做、用户批准了哪个版本、发生了什么、如何验证，以及为什么后来返工。

## Checkpoint 怎样防止漏写状态

每个正式状态边界都通过平台对应的 checkpoint 工具提交：

1. 原子取得当前 Task 的锁；
2. 在覆写任何账本前验证路径、字段、枚举、编号、模式关卡、引用和下一状态；
3. 预先计算 Snapshot 和 History 所需内容；
4. 原子替换 `current_state.md`；
5. 把完整 Current 原文追加到单一 `snapshots.md`；
6. 根据实际追加结果计算 Snapshot 起止行和哈希；
7. 向 `history.md` 追加索引；
8. 重新读取三个文件并验证一致性；
9. 删除成功事务并释放锁。

如果进程在第 4 步或第 5 步后中断，用同一个 next-state 重跑提交。脚本根据已经完成到哪一步继续补齐，不重复追加相同事件。相同 ID 但内容不同会失败。

只有 `CHECKPOINT_COMMITTED` 表示提交成功。`verify` 是只读操作，成功时输出 `TASK_STATE_VALID`。

## 什么时候必须保存 Checkpoint

- 即将请求 Requirements、Goal、Plan 或 Delivery 审查前；
- 用户作出批准、拒绝或其他关键 Decision 后；
- 切换 Phase、Stage 或 Session 时；
- 保存有价值的施工进度或机器验证结果时；
- 进入返工、阻塞、暂停或结束时；
- 上下文压缩、模型更换或任务交接前；
- 开始下一 Stage 的 Plan 前。

准备压缩时，Phase 通常保持不变。Agent 只是保存一个可恢复检查点，然后停止启动新步骤、委派和外部动作。

## 上下文压缩与模型更换

Agent 无法可靠看到所有 Harness 的真实 Token 占用，因此是否压缩由用户或宿主管理。

推荐做法：

1. 如果 Harness 有上下文占用显示，在大约一半时考虑压缩；
2. 每个 Stage 结束并确认落盘后，也是合适的压缩点；
3. 告诉 Agent 先保存压缩前检查点并暂停；
4. 等待脚本明确返回 `CHECKPOINT_COMMITTED`；
5. 再使用 Harness 的手动压缩功能；
6. 压缩完成或更换模型后，要求 Agent 按恢复流程继续，不重新开始项目；
7. 核对 Agent 对 Goal 和当前状态的复述。

可以直接对 Agent 说：

> 我准备压缩上下文。请先保存并验证当前 Task 的检查点，保留 Goal、当前 Plan、用户 Decision、已有授权、实际进度、机器证据、失败路线、未完成项和下一步。得到 `CHECKPOINT_COMMITTED` 后暂停，不要开始新工作。

恢复时可以说：

> 这是压缩后恢复或模型更换。请先运行只读 verify，重新读取 `goal.md`、`current_state.md`、Case 索引和最近 History，核对实际文件与 diff，然后向我复述最终 Goal、当前阶段、已有批准、未完成项和下一步。等我确认后再继续。

## 文件接收为什么不属于状态机

用户可能在任何阶段通过路径、附件或 `@` 引用新文件。文件出现不代表需求、Goal 或 Plan 发生变化，因此 intake 是独立流程，不改变当前 Phase。

| 文件位置 | 处理方式 |
|---|---|
| 已在当前 Task 内 | 原地使用，不重复复制 |
| 在 Workspace 内、当前 Task 外 | 复制并验证到 `UserInput/I-NNNN/`；列出已复制内容；询问用户是否删除源文件 |
| 在 Workspace 外 | 复制并验证到 `UserInput/I-NNNN/`；只告知已经复制，不询问删除源文件 |
| 当前没有活动 Task | 不因为一个文件自动新建项目；先让用户选择或创建 Task |

intake 只处理用户明确提到的路径。它拒绝自动复制 `.git`、状态目录、协议目录、符号链接、junction 和递归 `tasks`。

## Case 怎样形成

每次步骤开始、压缩恢复或模型更换后，Agent 只读取 Global、Workspace 和当前 Task 的 Case 索引。索引包含简短摘要、根因和触发场景；只有当前场景匹配时才读取详细 Case。

出现错误后：

1. Agent 和脚本记录错误签名、已确认根因及证据；
2. checkpoint 按当前 Task History 统计同一 `ROOT_CAUSE_KEY` 的出现次数；
3. 第一次和第二次只继续累计；
4. 第三次且没有现有 Case 时，脚本输出 `CASE_RECOMMENDATION_REQUIRED`；
5. Agent 显式提醒用户，并建议落盘；
6. 用户同意后，向 `decisions.md` 追加 `CASE_RECORD_APPROVED`，再写 Case 索引和详情；
7. History 保存 Case ID，把它与当时的 Plan、Decision 和 Snapshot 连接起来。

用户认为某个 Task Case 很通用时，可以批准升格为 Workspace Case 或 Global Case。原 Case 不移动、不删除，升格记录保留来源和适用边界。

## 三个平台工具入口

发布包同时包含所有脚本。Agent 根据当前操作系统选择入口：

- Windows：`.agent-protocol/tools/checkpoint.cmd` 和 `intake.cmd`；路径包含 `%`、`!`、`&`、`^` 等 CMD 元字符时，改用 PowerShell 直接调用对应 `.ps1`；
- Linux：`sh .agent-protocol/tools/checkpoint.sh` 和 `sh .agent-protocol/tools/intake.sh`；
- macOS：与 Linux 相同。

终端用户不需要 Python、Node 或其他额外运行时。CMD 只负责调用 PowerShell，不处理账本文本。所有账本统一使用 UTF-8、无 BOM、LF 和一个末尾换行，避免 PowerShell、CMD 与 POSIX Shell 对文本处理方式不同而破坏哈希或行号。

## 恢复时相信什么

证据优先级不是“账本永远正确”。正常恢复需要同时查看：

1. 用户最新明确指令；
2. checkpoint 的只读验证结果；
3. 实际文件与版本控制 diff；
4. 测试、构建和产物；
5. 外部动作的真实状态；
6. Current State 与历史账本。

账本和实际工作区冲突时，保留原历史，追加纠正记录。不能修改旧 Decision、伪造过去已经正确，或盲目重做一个结果未知的外部动作。
