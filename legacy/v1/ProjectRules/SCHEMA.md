# SCHEMA.md — 通用 Agent 项目生命周期数据契约

**适用范围**：与同目录 `AGENTS.md` / `OPERATING_RULES.md` / `TASK_STATE_MACHINE.md` 配套使用。  
**Schema 版本**：`PKS-2`  
**Sub-schemas**：`PLAN-2`, `CS-2`, `HSNAP-1`, `CASE-1`, `TIDX-1`, `FIDX-1`

**定位**：本文件只规定生命周期数据“怎么写”：字段、ID、记录块、证据、引用和模板。  
“什么时候写、什么时候等待用户、何时进入下一状态”由 `TASK_STATE_MACHINE.md` 定义。  
“该不该做、往哪走”由 `AGENTS.md` 定义；条件触发细节由 `OPERATING_RULES.md` 定义。  
项目目录和资产纪律由 `AGENTS.md` 定义。

> 本契约不依赖特定模型、Agent 宿主、IDE、CLI、编程语言或版本控制系统。

---

## 0. 核心数据原则

1. `plan.md`：Append-Only，保存需求/方案/审批的决策链。
2. `task_current_state.md`：可覆盖，保存唯一当前真相。
3. `task_history.md`：Append-Only，只保存 CurrentState 的完整历史快照。
4. `cases/`：可修订知识文件，但仅由用户显式触发。
5. 旧记录允许通过新增 Correction 纠正，但禁止回写。
6. Human Acceptance / Human Test 只能来自用户明确反馈。
7. Agent 推断不得伪装成用户批准或已确认事实。
8. 长期账本必须可通过 `SEARCH:` 索引先定位后局部读取。

---

## 1. 通用格式

### 1.1 字段
- 固定字段名：大写英文 + 下划线。
- 正文：使用项目默认语言；技术标识保持原样。
- 多值字段：Markdown 列表。
- 时间：RFC 3339，必须带时区，例如 `2026-08-19T17:00:00+08:00`。
- Task 内路径：相对 Task 根目录；项目 canonical path 使用相对 `PROJECT_ROOT` 的路径并明确 `PROJECT_PATH:`。
- 不适用：`NOT_APPLICABLE` + 理由。
- 真实为空：`none`。
- 无法确认：`UNKNOWN` + `FOLLOW_UP`。

### 1.2 证据分类

```text
USER_STATEMENT
USER_CONFIRMATION
USER_APPROVAL
USER_REJECTION
USER_ACCEPTANCE
USER_OBSERVATION
CODE_INSPECTION
CONFIG_INSPECTION
TEST_RESULT
HUMAN_TEST_RESULT
RUNTIME_LOG
BUILD_OUTPUT
RELEASE_ARTIFACT
VERSION_CONTROL_DIFF
PROJECT_DOCUMENT
UPSTREAM_DOCUMENTATION
EXTERNAL_SOURCE
MODEL_INFERENCE
```

事实内容尽量区分：

```text
CONFIRMED_FACTS:
- F1 [SOURCE] ...

INFERENCES:
- I1 [MODEL_INFERENCE] ...

UNVERIFIED:
- U1 ...
```

仅有模型推断时不得写成已确认事实。

---

## 2. 强制检索协议：SEARCH Index + Search First

### 2.1 Append-Only 文件必须有 `SEARCH:` 单行索引

`plan.md` 与 `task_history.md` 的每个记录块都必须以：

```text
================================================================================
SEARCH: ...
...
================================================================================
```

包裹。

`SEARCH:` 是粗检索入口，不替代正文，但必须包含足够稳定键，使任意 Agent 可以使用 grep、rg、find-in-file、宿主搜索或等效能力快速定位。

### 2.2 `plan.md` 的 SEARCH 最低字段

```text
SEARCH: RECORD=PLAN EVENT=<EVENT> ROUND=<ROUND_ID> PLAN=<PLAN_ID> REV=<REV_OR_NA> ID=<PLAN_EVENT_ID> SUBJECT=<SUBJECT> STATUS=<STATUS> TAGS=<...>
```

### 2.3 `task_history.md` 的 SEARCH 最低字段

```text
SEARCH: RECORD=HISTORY TYPE=STATE_SNAPSHOT ID=<ENTRY_ID> ROUND=<ROUND_ID> PLAN=<PLAN_REF> REASON=<REASON> SUBJECT=<SUBJECT> STATUS=<STATUS> STATE=<STATE_REVISION> TAGS=<...>
```

### 2.4 读取规则

- `task_current_state.md`：允许完整读取，且恢复时优先完整读取。
- `plan.md`：必须先按 ID / Subject / Status 搜索，再局部读取。
- `task_history.md`：必须先按 Entry / Round / Plan / Reason / Subject 搜索，再局部读取。
- `SCHEMA.md` 本身较长时优先按标题或字段搜索。
- 只有完整审计、索引修复或多轮搜索无法定位时才允许全读长期账本。

---

## 3. 统一 ID

默认格式：

| 对象 | 格式 | 示例 |
|---|---|---|
| Task 内逻辑轮次 | `RNNNN` | `R0003` |
| Plan | `P-RNNNN-NNN` | `P-R0003-001` |
| Plan Revision | `P-RNNNN-NNN@revN` | `P-R0003-001@rev2` |
| Plan Event | `PE-RNNNN-NNN-NNN` | `PE-R0003-001-004` |
| CurrentState Revision | `CS-NNNN` | `CS-0017` |
| History Snapshot | `H-RNNNN-NNN` | `H-R0003-004` |
| Case | `CASE-NNNN` | `CASE-0004` |

规则：
- 正式 ID 只由主 Agent / 主协调者分配。
- 计数器保存在 CurrentState。
- ID 一经分配不得复用。
- Subagent 不得独立分配最终 ID。

---

# 4. `plan.md` — PLAN-2

## 4.1 定位

`plan.md` 是 **Append-Only** 的需求、计划与审批账本。

它回答：
- 用户确认过什么需求；
- Agent 提交过什么 Plan；
- 哪个 Revision 被拒绝；
- 哪个 Revision 被批准；
- 后续 Correction 是什么。

它不作为“当前施工状态”的权威；当前施工状态属于 CurrentState。

## 4.2 Plan Event

核心事件：

```text
DISCOVERY
PROPOSAL
REVIEW
CORRECTION
ROUND_CLOSE
```

- `DISCOVERY`：可选；长需求讨论的阶段性固化，不构成授权。
- `PROPOSAL`：初版或修订版计划。
- `REVIEW`：用户批准或拒绝某个精确 Revision。
- `CORRECTION`：追加纠正旧记录中的事实错误。
- `ROUND_CLOSE`：记录本 Round 最终关闭状态，不替代 History。

## 4.3 Proposal 必填字段

```text
PLAN_EVENT_ID
SCHEMA_VERSION: PLAN-2
ROUND_ID
PLAN_ID
PLAN_REVISION
PLAN_EVENT: PROPOSAL
PLAN_STATUS_AT_WRITE: AWAITING_APPROVAL
RECORDED_AT
RECORDER_AGENT
BASED_ON_STATE

AREA
SUBJECT
TAGS
SUMMARY

USER_CONFIRMED_REQUIREMENTS
GOAL
IN_SCOPE
OUT_OF_SCOPE
CONSTRAINTS
DELIVERABLES
IMPLEMENTATION_STEPS
VALIDATION_PLAN
ACCEPTANCE_CRITERIA
RISKS
INVARIANTS
SEPARATE_APPROVAL_REQUIRED
```

按需：

```text
DISCUSSION_SOURCES
REQUIREMENT_TRACEABILITY
OPTIONS
RECOMMENDATION
PROJECT_FILES_EXPECTED
TASK_FILES_EXPECTED
DEPENDENCIES
OPEN_QUESTIONS
STOP_CONDITIONS
SUPERSEDES_REVISION
CHANGES_FROM_PREVIOUS
USER_FEEDBACK_ADDRESSED
```

### Proposal 模板

```text
================================================================================
SEARCH: RECORD=PLAN EVENT=PROPOSAL ROUND=R0003 PLAN=P-R0003-001 REV=2 ID=PE-R0003-001-003 SUBJECT=document.layout STATUS=AWAITING_APPROVAL TAGS=document,layout

PLAN_EVENT_ID: PE-R0003-001-003
SCHEMA_VERSION: PLAN-2
ROUND_ID: R0003
PLAN_ID: P-R0003-001
PLAN_REVISION: 2
PLAN_EVENT: PROPOSAL
PLAN_STATUS_AT_WRITE: AWAITING_APPROVAL
RECORDED_AT: 2026-08-19T17:00:00+08:00
RECORDER_AGENT: AGENT_NAME_OR_UNKNOWN
BASED_ON_STATE: CS-0016

AREA: document
SUBJECT: document.layout
TAGS:
- document
- layout

SUMMARY:
...

USER_CONFIRMED_REQUIREMENTS:
- ...

GOAL:
...

IN_SCOPE:
- ...

OUT_OF_SCOPE:
- ...

CONSTRAINTS:
- ...

DELIVERABLES:
- ...

PROJECT_FILES_EXPECTED:
- src/example.ext

TASK_FILES_EXPECTED:
- 02_src/helper_script.ext

IMPLEMENTATION_STEPS:
1. ...
2. ...

VALIDATION_PLAN:
- ...

ACCEPTANCE_CRITERIA:
- ...

RISKS:
- ...

INVARIANTS:
- ...

SEPARATE_APPROVAL_REQUIRED:
- ...
================================================================================
```

## 4.4 Review

必填：

```text
PLAN_EVENT_ID
SCHEMA_VERSION: PLAN-2
ROUND_ID
PLAN_ID
PLAN_EVENT: REVIEW
TARGET_REVISION
RECORDED_AT
RECORDER_AGENT
REVIEWED_BY: USER
REVIEW_RESULT: APPROVED / REJECTED
USER_FEEDBACK
```

批准时：

```text
APPROVED_PLAN_REF
APPROVED_SCOPE
APPROVAL_EXCLUSIONS
```

拒绝时：

```text
REJECTION_REASON
REQUIRED_CHANGES
NEXT_REVISION
```

规则：
- Review 只能绑定精确 Revision。
- 对 rev1 的批准不能自动扩展到 rev2。
- 用户新增需求时，必须形成新 Revision 并重新审批。
- 不得回头修改旧 Proposal 的状态字段。

### Review 模板

```text
================================================================================
SEARCH: RECORD=PLAN EVENT=REVIEW ROUND=R0003 PLAN=P-R0003-001 REV=2 ID=PE-R0003-001-004 SUBJECT=document.layout STATUS=APPROVED TAGS=document,layout

PLAN_EVENT_ID: PE-R0003-001-004
SCHEMA_VERSION: PLAN-2
ROUND_ID: R0003
PLAN_ID: P-R0003-001
PLAN_EVENT: REVIEW
TARGET_REVISION: 2
RECORDED_AT: 2026-08-19T17:05:00+08:00
RECORDER_AGENT: AGENT_NAME_OR_UNKNOWN
REVIEWED_BY: USER
REVIEW_RESULT: APPROVED

USER_FEEDBACK:
按 rev2 执行。

APPROVED_PLAN_REF:
P-R0003-001@rev2

APPROVED_SCOPE:
仅限 rev2 明确范围。

APPROVAL_EXCLUSIONS:
- 未经另行批准的高风险外部操作
================================================================================
```

## 4.5 Correction

旧 Plan 不修改。事实错误使用：

```text
PLAN_EVENT: CORRECTION
CORRECTION_OF
OLD_RECORD
NEW_EVIDENCE
CORRECTED_RECORD
WHY_CHANGED
```

## 4.6 Round Close

推荐字段：

```text
PLAN_EVENT_ID
SCHEMA_VERSION: PLAN-2
ROUND_ID
PLAN_ID
PLAN_EVENT: ROUND_CLOSE
RECORDED_AT
RECORDER_AGENT
APPROVED_PLAN_REF
APPROVAL_REF
CLOSE_REASON
COMPLETION_STATUS
FINAL_STATE_REF
HISTORY_REFS
PENDING_WORK
```

`ROUND_CLOSE` 是 Plan 生命周期索引，不复制 CurrentState 或 History 正文。

---

# 5. `task_current_state.md` — CS-2

## 5.1 定位

CurrentState 是**可覆盖的唯一当前状态快照**。

它回答：
- 当前 Project / Task 在哪里；
- 现在处于哪个 Round / Plan；
- 用户是否已批准；
- 正在做什么；
- 修改了哪些 canonical project files；
- 交付了什么 Task-local artifact；
- 用户是否在验收；
- 当前 Blocker / Issue；
- 下一步是什么；
- 从哪里安全恢复。

它不得承担不可变历史职责。

## 5.2 顶层结构

```text
# Current State

## METADATA
## PROJECT_AND_TASK_IDENTITY
## ACTIVE_ROUND_AND_PLAN
## WORKFLOW_EXECUTION_STATE
## CURRENT_REQUIREMENTS
## PROJECT_CHANGE_STATE
## CURRENT_DELIVERABLES
## BUILD_AND_VALIDATION_STATE
## USER_ACCEPTANCE_STATE
## KNOWN_ISSUES
## ACTIVE_CONSTRAINTS
## VERSION_CONTROL_STATE
## NEXT_ACTIONS
## COUNTERS_AND_INDEXES
## CONTEXT_HANDOFF
```

## 5.3 核心字段

```yaml
METADATA:
  SCHEMA_VERSION: PKS-2
  STATE_SCHEMA_VERSION: CS-2
  STATE_REVISION: CS-0017
  STATE_STATUS: CURRENT
  LAST_UPDATED:
  UPDATED_BY:
  LAST_VERIFIED:

PROJECT_AND_TASK_IDENTITY:
  PROJECT_ROOT:
  TASKS_ROOT:
  TASK_ROOT:
  TASK_CREATED_AT:
  TOP_LEVEL_SESSION_RULE: ONE_SESSION_ONE_TASK

ACTIVE_ROUND_AND_PLAN:
  ROUND_ID:
  PRECEDING_TASK_REF:  # 续接来源（新建任务为 none；续接时记录来源任务编号与时间，见 OPERATING_RULES §2）
  ACTIVE_PLAN_REF:
  PLAN_LIFECYCLE_STATUS: PLANNING / AWAITING_APPROVAL / REJECTED / APPROVED / CLOSED / none
  APPROVAL_REF:
  WORKFLOW_PHASE: REQUIREMENTS_CONFIRMATION / PLAN_DRAFTING / AWAITING_PLAN_APPROVAL / IMPLEMENTATION / AWAITING_ACCEPTANCE / REWORKING / REPLAN_REQUIRED / CASE_REVIEW / IDLE
  EXECUTION_STATUS: NOT_STARTED / IN_PROGRESS / PAUSED_FOR_REAPPROVAL / BLOCKED / COMPLETED / STOPPED
  CURRENT_STEP:
  LAST_COMPLETED_STEP:
  BLOCKERS:
  SAFE_RESUME_POINT:

CURRENT_REQUIREMENTS:
  SUBJECT:
  CONFIRMED_REQUIREMENTS:
  IN_SCOPE:
  OUT_OF_SCOPE:
  ACTIVE_CONSTRAINTS:

PROJECT_CHANGE_STATE:
  CANONICAL_FILES_INSPECTED:
  CANONICAL_FILES_CHANGED:
  NEW_PROJECT_FILES_CREATED:
  USER_EXISTING_CHANGES_PRESERVED:

CURRENT_DELIVERABLES:
  - ARTIFACT_ID:
    PATH:
    PATH_SCOPE: PROJECT / TASK
    TYPE:
    STATUS:
    HASH_OR_FINGERPRINT:
    NOTES:

BUILD_AND_VALIDATION_STATE:
  AUTOMATED_VALIDATION_STATUS:
  AUTOMATED_VALIDATION_REFS:
  HUMAN_TEST_STATUS: NOT_STARTED / AWAITING / PASSED / FAILED
  HUMAN_TEST_FEEDBACK:
  UNVERIFIED_ITEMS:

USER_ACCEPTANCE_STATE:
  ACCEPTANCE_STATUS: NOT_REQUESTED / AWAITING / ACCEPTED / REJECTED
  LAST_USER_FEEDBACK:
  ACCEPTED_ARTIFACT_REFS:

KNOWN_ISSUES:
  - ISSUE_ID:
    STATUS:
    DESCRIPTION:
    EVIDENCE_REF:

VERSION_CONTROL_STATE:
  SYSTEM: git / other / none
  BRANCH:
  HEAD_REVISION:
  WORKTREE_STATUS:
  USER_CHANGES_PRESENT:

NEXT_ACTIONS:
  - ...

COUNTERS_AND_INDEXES:
  ROUND_COUNTER:
  PLAN_COUNTER:
  PLAN_EVENT_COUNTER:
  STATE_REVISION_COUNTER:
  HISTORY_COUNTER:
  CASE_COUNTER:

CONTEXT_HANDOFF:
  REQUIRED_FIRST_READS:
  - 05_docs/task_current_state.md
  SAFE_RESUME_POINT:
  CONTEXT_COMPRESSION_READY: yes / no
```

## 5.4 CurrentState 更新原则

- 可以全量覆盖。
- 覆盖前必须基于当前真实文件、验证和用户反馈。
- `HUMAN_TEST_STATUS: PASSED` / `ACCEPTANCE_STATUS: ACCEPTED` 只能来自用户明确反馈。
- 进入用户验收前，必须先将交付候选、canonical changes 与验证结果写入 CurrentState。
- History 转写时先冻结当前文件内容；History Append 完成后才能继续覆盖 CurrentState。
- `PROJECT_ROOT` / `TASK_ROOT` 必须记录实际解析后的路径，不使用未替换占位符。

---

# 6. `task_history.md` — HSNAP-1

## 6.1 定位

`task_history.md` 是 **Append-Only CurrentState Snapshot Ledger**。

History 不由 Agent 另写一份“总结版事件”。每条历史记录由：

1. 一个很薄的 **History Envelope**；
2. 当时 `task_current_state.md` 的**完整原文 Snapshot Body**；

组成。

## 6.2 触发时机

具体触发由 `TASK_STATE_MACHINE.md` 决定。核心包括：

- 用户验收不合格；
- 用户验收合格；
- Scope Change 需要重新审批；
- 用户取消且存在需要保留的实际状态；
- 其他状态机明确要求固化当前状态的边界。

## 6.3 Envelope 必填字段

```text
ENTRY_ID
SCHEMA_VERSION: HSNAP-1
RECORDED_AT
RECORDER_AGENT
ROUND_ID
PLAN_REF
APPROVAL_REF
STATE_REVISION
REASON
AREA
SUBJECT
TAGS
STATUS_AT_WRITE
SNAPSHOT_HASH
SNAPSHOT_HASH_ALGORITHM
```

`REASON` 推荐枚举：

```text
USER_REJECTED_DELIVERY
USER_ACCEPTED_DELIVERY
SCOPE_CHANGE_REQUIRES_REAPPROVAL
USER_CANCELLED
BLOCKED_STOP
MILESTONE
CORRECTION
```

## 6.4 Snapshot Body

必须使用明确边界：

```text
----- BEGIN CURRENT_STATE SNAPSHOT -----

<task_current_state.md 完整原文，不摘要、不删节、不改写>

----- END CURRENT_STATE SNAPSHOT -----
```

规则：
- Snapshot Body 必须与转写时 CurrentState 一致。
- 推荐计算 SHA-256；无法计算时使用 `SNAPSHOT_HASH_ALGORITHM: NONE`，不得伪造。
- Snapshot 写入后禁止修改。
- 旧事实后来被纠正时，追加新的 History Snapshot / Correction，不回写旧 Snapshot。

## 6.5 History 模板

```text
================================================================================
SEARCH: RECORD=HISTORY TYPE=STATE_SNAPSHOT ID=H-R0003-002 ROUND=R0003 PLAN=P-R0003-001@rev2 REASON=USER_REJECTED_DELIVERY SUBJECT=document.layout STATUS=REJECTED STATE=CS-0017 TAGS=document,layout

ENTRY_ID: H-R0003-002
SCHEMA_VERSION: HSNAP-1
RECORDED_AT: 2026-08-19T17:30:00+08:00
RECORDER_AGENT: AGENT_NAME_OR_UNKNOWN
ROUND_ID: R0003
PLAN_REF: P-R0003-001@rev2
APPROVAL_REF: PE-R0003-001-004
STATE_REVISION: CS-0017
REASON: USER_REJECTED_DELIVERY

AREA: document
SUBJECT: document.layout
TAGS:
- document
- layout

STATUS_AT_WRITE: REJECTED
SNAPSHOT_HASH_ALGORITHM: SHA-256
SNAPSHOT_HASH: <hash>

----- BEGIN CURRENT_STATE SNAPSHOT -----

# Current State
...
<完整原文>

----- END CURRENT_STATE SNAPSHOT -----
================================================================================
```

---

# 7. `cases/` — CASE-1

## 7.1 触发约束

Case 文件**只允许由用户显式指令触发**。

`cases/` 目录默认存在但可以为空。

创建 Case 前必须检索已有：
- `SUBJECT`
- 症状标签
- 根因标签
- 适用环境

同一模式优先修订已有 Case，不堆重复案例。

## 7.2 Case 字段

```text
CASE_ID
SCHEMA_VERSION: CASE-1
TITLE
STATUS: OPEN / RESOLVED / WATCHLIST / SUPERSEDED
REVISION
CREATED_AT
CREATED_BY
UPDATED_AT
UPDATED_BY

AREA
SUBJECT
TAGS

RELATED_PLANS
RELATED_HISTORY

PITFALL
APPLIES_WHEN
TRIGGER_CONDITION
SYMPTOMS
CONSEQUENCES
ROOT_CAUSE
RESOLUTION
LESSONS
GUARDRAILS
DO_NOT_REPEAT
EXCEPTIONS

CONFIRMED_FACTS
INFERENCES
UNVERIFIED
```

不得为了填满字段而猜测 Root Cause。未知内容明确写 `UNKNOWN` / `UNVERIFIED`。

---

# 8. Round / Idle 约定

- Task 生命周期与 Top-Level Session 一致。
- Round 是 Task 内一次完整工作循环。
- 用户验收完成后，CurrentState 转为 `IDLE`，Task 不结束。
- 同一 Session 后续新需求分配新 Round，重新经过需求确认和 Plan Gate。
- 新 Top-Level Session 才创建新 Task。

---

# 9. 高风险外部操作扩展

若 Approved Plan 涉及版本控制发布、生产部署、不可逆删除、系统级配置、权限修改、外部服务写操作等高风险动作：

- 继续遵守宿主系统规则、安全策略与用户授权边界；
- 必须在 Plan 中列入 `SEPARATE_APPROVAL_REQUIRED`；
- 项目若另有发布确认协议，可作为 `PLAN-2` 扩展事件保存；
- 任何扩展都不得绕过本状态机的 Plan Approval、CurrentState 与 History 规则。

---

# 10. 一致性终检

每次状态边界写入后检查：

- [ ] Plan / History 是否只 Append；
- [ ] CurrentState 是否只包含当前真相；
- [ ] History Snapshot 是否为 CurrentState 完整原文；
- [ ] 用户批准是否绑定精确 Plan Revision；
- [ ] 用户验收是否来自明确反馈；
- [ ] CurrentState 中 ID 与计数器是否一致；
- [ ] `SEARCH:` 是否包含精确 ID、Round、Plan、Subject、Status/Reason；
- [ ] 长账本恢复是否遵守 Search First / Read Narrow；
- [ ] Case 是否确由用户显式触发；
- [ ] Subagent 是否未独立分配正式 ID；
- [ ] canonical project files 与 Task-local assets 是否正确区分。

---

# 11. `TASK_INDEX.md` — TIDX-1（项目任务全景索引）

## 11.1 定位

`<PROJECT_ROOT>/TASK_INDEX.md` 是**投影式**（可覆盖）的项目任务全景索引：项目内所有任务 current_state 的简略版，任何时刻反映各任务的当前状态。

- 不承担不可变历史职责（历史在 `task_history.md`）。
- 回答：“项目里有哪些任务、各做到哪、要找细节去哪个路径”。
- 任何新对话的第一步读取它（`AGENTS.md` §1）。

## 11.2 维护规则

- 每任务一个区块，区块相互独立；更新前读全文件，**只替换自己的区块**。
- 写入时机：任务创建时写初始区块；轮次结束时更新自己的区块；续接接管时更新 `LAST_ACTIVE_AT`。
- 维护权：归属于该任务的**最后活跃 Agent**；同一任务内禁止并行更改。
- 任务目录被删除/归档后，区块标记 `STALE` 而非删除。
- 触发细节见 `OPERATING_RULES.md` §3。

## 11.3 区块模板

```text
### task<N>_<Description>

TASK_ID: task<N>_<Description>
CREATED_AT: <RFC3339>
STATUS: ACTIVE / CLOSED / STALE
SUBJECT: <一句话主题>
ROUND_ID: <最近轮次，如 R0002>
WORKFLOW_PHASE: <最近阶段，如 IMPLEMENTATION / IDLE>
HANDOFF_NOTES: <交接要点 1-2 行：做了什么、结论、坑>
CURRENT_STATE_PATH: tasks/<YYYYMMDD>/task<N>_<Description>/05_docs/task_current_state.md
LAST_ACTIVE_AT: <RFC3339>
```

规则：`HANDOFF_NOTES` 只写结论与指针，不重述细节；细节永远回 `CURRENT_STATE_PATH` 取。

---

# 12. `FILE_INDEX.md` — FIDX-1（文件归属登记流水）

## 12.1 定位

`<PROJECT_ROOT>/FILE_INDEX.md` 是 **append-only** 的文件归属登记流水：记录散落文件的归属判定与用户裁决，与 TASK_INDEX 的投影职责分开。

- 回答：“这个文件是哪来的、归谁、状态如何”。
- 登记范围：项目根目录散落文件 + 各任务 `01_inputs/` 内容。

## 12.2 快速判定与结算

- 快速判定三规则（用户澄清 > 会话中提及 > 会话前已有=待定）见 `OPERATING_RULES.md` §5。
- 轮次关闭时执行归属结算（先结算、后写历史快照）见 `OPERATING_RULES.md` §5.3。

## 12.3 条目模板

```text
### FILE-<NNNN>  <相对路径或文件名>

RECORDED_AT: <RFC3339>
FILE_TIME: <文件时间，UNKNOWN 则标注>
SUMMARY: <内容概要，一句话>
ATTRIBUTION: task<N> / 公共 / 待定
EVIDENCE: <判定依据：USER_CLARIFICATION / USER_MENTION / PRE_SESSION / OTHER>
STATUS: PENDING_USER / CONFIRMED / CLEANED / ARCHIVED
USER_DECISION: <用户裁决原文或摘要；未裁决为 none>
```

规则：`ATTRIBUTION: 待定` 的条目保持到用户裁决后才改写状态（追加新记录说明裁决，不回写旧条目）。
