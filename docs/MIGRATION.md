# 迁移到 v5.0.1

v5 改变了身份层级、模式名称、状态 Schema 和用户工具，旧账本不能原地改写成 v5。

- 新建 `tasks/task<N>_YYYYMMDD_<项目名>/`，Task 即 Project。
- 将旧项目材料复制到 Task，保留原件；不要复制旧 `.git` 内部数据。
- 从证据整理新的 Requirements、Goal、Stage Plan 与 Decision。无法证明的旧批准保持未知。
- 旧多快照文件不能手工合并；由 v5 checkpoint 从第一个 Current 开始生成新的单一 `snapshots.md`。
- 旧 Case 只有在根因、触发场景和用户批准可核验时才迁移。
- v4 草案的 `PLAN_APPROVAL` 对应 v5 `STRICT_APPROVAL`，`TASK_DELEGATION` 对应 `AUTONOMOUS`，但必须重新初始化 Task 模式。

`legacy/` 保留历史版本供审计。迁移完成并验证前不删除旧材料。
