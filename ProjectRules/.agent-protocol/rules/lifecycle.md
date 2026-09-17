# Task、Session 与 Stage 生命周期

## Task（Project）

- 扫描 `tasks/` 后分配 `task<N>_YYYYMMDD_<任务名>`；目录名与 `TASK_ID` 永久相同。
- Task 就是项目根。新对话继续既有项目时，展示候选 Task、Goal、最近 Stage/事件并取得确认，不新建同项目 Task。
- 初始化通过 checkpoint 工具创建六个空账本、`cases/index.md`、事务与锁目录，并最小合并两层 `.gitignore`。
- 工作区模式只作为新 Task 默认值；初始化后以 Task Current State 中的模式为准。
- 既有 Task 切换模式时，先追加用户 `MODE_SWITCH_APPROVED`，其目标必须为 `GOVERNANCE_MODE:<旧模式>-><新模式>`；切换检查点把该 Decision 列入 `RELATED_DECISION_REFS`。没有该精确批准，checkpoint 拒绝模式变化。

## Session

- 一次新顶层对话、压缩后显式恢复或交接分配新的 `SESSION_ID: SES-NNNN`。
- Session 只表示工作上下文，不重置 Goal、Stage、批准或 Case 计数。
- 恢复时先运行 verify，再核对实际文件/diff，不能盲信账本。

## Stage

- `STAGE_ID: STG-NNNN` 表示一次可验收的交付周期。Goal 通常跨 Stage 稳定，Plan 和 Delivery 绑定一个 Stage。
- 严格模式只有当前 Delivery 验收后才能追加 `STAGE_CLOSED`，随后进入下一 Stage 的 Plan 撰写。
- 下一 Stage 改变最终 Goal 时，重新进入需求讨论、需求确认和 Goal 审批。

## Append-only 规则

- Goal、Plan、Decision、History、Snapshot 只追加；Current State 是唯一可覆写核心账本。
- Case index 和详细 Case 也只追加修订/Occurrence，不重写旧证据。
- Goal/Plan/Decision 先追加；Current/Snapshot/History 由 checkpoint 工具协调。任何可预先发现的错误都必须在替换 Current 前拒绝。
