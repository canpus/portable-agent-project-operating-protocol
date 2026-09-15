# PAPOP v3 记录 Schema

## 0. 目的与基本约束

本文件定义 `.agent-work/` 中记录的稳定格式，使 Agent 能用 `rg`、`grep` 或等效工具精确定位，而无需全文读取长期历史。

- 编码：UTF-8；文本使用 LF 或宿主既有换行风格。
- 字段名为大写 ASCII、固定拼写；机器检索字段必须单独占一行，格式为 `FIELD: value`。
- ID 只使用 ASCII 字母、数字和连字符；同一项目中唯一。编号必须查看现有记录后递增，不能凭记忆猜测。
- 多行说明写在 Markdown 标题下，不塞进机器字段。字段值未知写 `UNKNOWN`，不适用写 `NONE`，不得留空或使用模糊占位符。
- 所有时间采用可获得的 RFC3339 时区时间；无法可靠取得写 `UNKNOWN`，不得编造。
- `SUBJECT` 是便于人搜索的一行短语；`TAGS` 使用小写英文或稳定项目词，以逗号和一个空格分隔，例如 `TAGS: api, auth, regression`。
- 长期文件采用边界标记。不得在正文中复用相同 BEGIN/END 标记。

## 1. 目录结构

```text
.agent-work/
├── active.md
├── task_index.md
└── tasks/
    └── <TASK_ID>/
        ├── current_state.md
        ├── current_state.prev.md
        ├── plan.md
        ├── history.md
        └── snapshots/
            └── <EVENT_ID>.md
```

仅在 TRACKED 启用时创建。项目源码、输入、证据和交付物仍位于项目原位置；状态文件使用相对项目根的路径并注明基准。

## 2. ID 规则

| 对象 | 格式 | 示例 |
|---|---|---|
| Task | `T-YYYYMMDD-<slug>`；冲突时加 `-02` | `T-20260915-auth-fix` |
| Task-index event | `I-` 加 6 位数字，项目内单调递增 | `I-000001` |
| Plan | `P-` 加 4 位数字 | `P-0001` |
| Plan revision | Plan ID 加 `-R` 和 4 位数字 | `P-0001-R0002` |
| Step | `S-` 加 3 位数字，只在所属 Plan revision 内解释 | `S-003` |
| Event/checkpoint | `E-` 加 6 位数字，任务内单调递增 | `E-000014` |

`slug` 使用简短 ASCII 小写词和连字符。旧 ID 不回收、不重排。计划修订可继承原 Step ID；改变步骤含义时分配新 Step ID，并在修订映射中说明。

## 3. active.md — 当前任务快捷指针

完整读取，保持短小。切换活动任务时可覆盖；它不承担历史职责。

```text
SCHEMA: PAPOP-ACTIVE-3
TASK_ID: T-20260915-auth-fix
TASK_STATUS: ACTIVE
SUBJECT: 修复登录刷新流程
CURRENT_STATE: .agent-work/tasks/T-20260915-auth-fix/current_state.md
UPDATED_AT: 2026-09-15T10:30:00+08:00
```

`TASK_STATUS` 枚举：`ACTIVE / WAITING / BLOCKED / DONE / CANCELLED`。

## 4. task_index.md — 项目任务索引

只追加任务事件，不覆盖旧记录。搜索 `TASK_ID` 后读取命中块；同一任务可有多条，文件中最后出现的结构完整事件表示最新索引状态。`RECORDED_AT` 用于展示和审计，不用于推翻追加顺序。

```text
<!-- TASK_INDEX_EVENT_BEGIN -->
SCHEMA: PAPOP-TASK-INDEX-3
INDEX_EVENT_ID: I-000001
TASK_ID: T-20260915-auth-fix
EVENT_TYPE: TASK_CREATED
STATUS: ACTIVE
SUBJECT: 修复登录刷新流程
TAGS: auth, bugfix
CURRENT_STATE: .agent-work/tasks/T-20260915-auth-fix/current_state.md
RECORDED_AT: 2026-09-15T10:00:00+08:00
<!-- TASK_INDEX_EVENT_END -->
```

`EVENT_TYPE` 枚举：`TASK_CREATED / TASK_ACTIVATED / TASK_WAITING / TASK_BLOCKED / TASK_COMPLETED / TASK_CANCELLED`。

## 5. plan.md — Append-Only 正式计划修订

每个修订是独立块。旧修订不得回写；当前修订由 current_state 的 `PLAN_REF` 指定。

```text
<!-- PLAN_REVISION_BEGIN -->
SCHEMA: PAPOP-PLAN-3
TASK_ID: T-20260915-auth-fix
PLAN_ID: P-0001
PLAN_REF: P-0001-R0001
SUPERSEDES: NONE
STATUS: ACTIVE
SUBJECT: 修复登录刷新流程
TAGS: auth, implementation
CREATED_AT: 2026-09-15T10:05:00+08:00

## 目标与交付物
...

## 约束与授权
...

## 步骤与验收条件

### S-001 | 调查现状
- STATUS: PENDING
- DELIVERABLE: ...
- ACCEPTANCE: ...

### S-002 | 实现修复
- STATUS: PENDING
- DELIVERABLE: ...
- ACCEPTANCE: ...

## 修订映射
首次修订写 NONE；后续说明旧步骤的继承、替换、删除和已完成证据。
<!-- PLAN_REVISION_END -->
```

块头的 `STATUS` 表示该修订写入时的生命周期状态，允许值：`DRAFT / ACTIVE / AWAITING_APPROVAL / SUPERSEDING_PROPOSAL`。旧块不能因后来被替代而回写；替代关系由新块 `SUPERSEDES` 以及历史事件表达。

步骤的 STATUS 是计划写入时状态快照，实际当前进度以 current_state 为准。

## 6. current_state.md — 当前完整恢复状态

每次检查点全量重写，并保持足够短以便恢复时完整读取。稳定目标和约束没有变化时原样保留，不对上一版摘要再次摘要。

```text
SCHEMA: PAPOP-CURRENT-3
TASK_ID: T-20260915-auth-fix
STATUS: EXECUTING
SUBJECT: 修复登录刷新流程
TAGS: auth, bugfix
PLAN_REF: P-0001-R0001
ACTIVE_STEP: S-002
LAST_EVENT_ID: E-000004
LAST_EVENT_TYPE: STEP_COMPLETED
LAST_SNAPSHOT: .agent-work/tasks/T-20260915-auth-fix/snapshots/E-000004.md
RESUME_MODE: NORMAL
UPDATED_AT: 2026-09-15T10:30:00+08:00

## 目标与交付物
...

## 稳定约束与用户决定
...

## 授权与待确认动作
...

## 计划进度
| STEP_ID | STATUS | RESULT_OR_NEXT | EVIDENCE |
|---|---|---|---|
| S-001 | DONE | 已确认根因 | path/to/evidence |
| S-002 | IN_PROGRESS | 修改刷新逻辑 | path/to/file |

## 已完成成果与验证
...

## 下一步与验收条件
...

## 阻塞、未知与未验证项
...

## 已否定路线及证据
...

## 执行中或结果未知的外部动作
...

## 关键路径
所有路径注明相对于 PROJECT_ROOT 或任务目录；只列恢复需要的输入、修改、产物和证据。
```

顶层 `STATUS` 枚举：`PLANNING / EXECUTING / VERIFYING / WAITING_USER / BLOCKED / DONE / CANCELLED`。步骤 STATUS 枚举：`PENDING / IN_PROGRESS / DONE / BLOCKED / SKIPPED`。`RESUME_MODE` 枚举：`NORMAL / READY_FOR_COMPACTION`。

## 7. history.md — Append-Only 事件索引

每个里程碑追加一条固定结构事件。事件只写本次变化摘要和完整快照指针，不重复整份 current_state。

```text
<!-- HISTORY_EVENT_BEGIN -->
SCHEMA: PAPOP-HISTORY-3
EVENT_ID: E-000004
TASK_ID: T-20260915-auth-fix
PLAN_REF: P-0001-R0001
STEP_ID: S-001
EVENT_TYPE: STEP_COMPLETED
STATUS: SUCCESS
SUBJECT: 完成登录刷新根因调查
TAGS: auth, investigation
SNAPSHOT: .agent-work/tasks/T-20260915-auth-fix/snapshots/E-000004.md
RECORDED_AT: 2026-09-15T10:30:00+08:00

## CHANGE
完成了什么或发生了什么；只描述本事件增量。

## EVIDENCE
与本事件直接相关的项目路径、命令结果或外部收据。未验证写 UNVERIFIED。

## NEXT
下一步或等待事项。
<!-- HISTORY_EVENT_END -->
```

`EVENT_TYPE` 枚举：

`TASK_CREATED / PLAN_CREATED / PLAN_REVISED / USER_DECISION / STEP_COMPLETED / PROGRESS_SAVED / PRE_COMPACTION / RESUMED / EXTERNAL_INTENT / EXTERNAL_RESULT / BLOCKED / TASK_COMPLETED / TASK_CANCELLED / RECOVERY_REPAIR`。

`STATUS` 枚举：`SUCCESS / PARTIAL / WAITING / BLOCKED / FAILED / UNKNOWN`。

## 8. snapshots/<EVENT_ID>.md — 完整状态快照

内容必须与该 EVENT_ID 提交时的 current_state 完全一致。优先使用文件复制而非让模型重新生成。快照完成后不回写；如发现错误，通过新检查点修正，保留旧文件作为事实记录。

## 9. 精确检索协议

优先使用 `rg`；不可用时使用 `grep`、编辑器搜索或宿主等效能力。

```text
rg -n '^EVENT_ID: E-000004$' .agent-work/tasks/<TASK_ID>/history.md
rg -n '^PLAN_REF: P-0001-R0002$' .agent-work/tasks/<TASK_ID>/plan.md
rg -n '^STEP_ID: S-003$' .agent-work/tasks/<TASK_ID>/history.md
rg -n '^EVENT_TYPE: PLAN_REVISED$' .agent-work/tasks/<TASK_ID>/history.md
rg -n '^TASK_ID: T-20260915-auth-fix$' .agent-work/task_index.md
rg -n '^TAGS: .*auth' .agent-work/tasks/<TASK_ID>/history.md
```

搜索返回行号后，从命中点向上找到最近的对应 BEGIN，向下读到对应 END。多个命中时先看块头字段，不将不同块拼接成一条事实。正文关键词搜索仅用于发现候选；定案使用稳定 ID 和结构字段。

如宿主不能按行局部读取，可先用一个小型搜索/提取工具输出完整命中块；仍不要直接把整个长期文件载入模型上下文。

## 10. 写入前结构检查

写入或追加前确认：

- ID 未重复且格式正确；
- 必填字段全部存在且每个只出现一次；
- 枚举值来自本 Schema；
- BEGIN/END 成对，记录没有嵌套；
- `TASK_ID`、`PLAN_REF`、`STEP_ID` 和 `EVENT_ID` 与 current_state 一致；
- 引用路径实际存在或明确标记为尚未生成；
- 不含凭据、无必要个人信息或整段原始材料。
