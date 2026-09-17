# Case 记录、触发与升格

## 发生计数

- 每次失败记录 `INCIDENT_SIGNATURE`、证据、Step/Event/Plan/Decision/Snapshot 和经证据确认的 `ROOT_CAUSE_KEY`。
- 只有同一 Task、同一已确认根因才累计；相同错误文字不能自动视为同根因。
- 第三次且尚无关联 Case 时输出 `CASE_RECOMMENDATION_REQUIRED`。用户可批准、拒绝或暂缓；只有 `CASE_RECORD_APPROVED` 才能创建。

## Case 内容

- `cases/index.md` 仅含 ID、短摘要、触发场景、详情指针和状态；每个步骤开始/恢复只读 index。
- `cases/C-NNNN.md` 记录根因、三次时间线、失败做法、诊断、预防清单、修复与回归证据。触发匹配才读取。
- Index 与详情均 append-only；再次重犯追加 Occurrence，不改写旧记录。

## 升格

- 用户判断 Case 具有强通用性时，用 `CASE_ELEVATION_APPROVED` 复制为 Workspace `WC-NNNN` 或 Global `GC-NNNN`。
- 升格 Case 保留来源 Task、原 Case、原事件/快照、审批 Decision、适用与不适用范围。原 Case 不移动、不删除，旧 History 引用保持有效。
- Workspace Case 写入 `<WORKSPACE_ROOT>/.agent-cases/`；Global Case 写入全局 `AGENTS.md` 同级的 `.agent-cases/`。两层都使用单一 `index.md` 和按 ID 命名的详情文件，仅在首次获批升格时创建。
