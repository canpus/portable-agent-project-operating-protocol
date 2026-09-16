SCHEMA: PAPOP-CURRENT-3
TASK_ID: {TASK_ID}
STATUS: {PLANNING / EXECUTING / VERIFYING / WAITING_USER / BLOCKED / DONE / CANCELLED}
SUBJECT: {一行任务主题}
TAGS: {tag-one, tag-two}
PLAN_REF: {例如 P-0001-R0001，或 NONE}
ACTIVE_STEP: {例如 S-001，或 NONE}
LAST_EVENT_ID: {例如 E-000001}
LAST_EVENT_TYPE: {SCHEMA 规定的 EVENT_TYPE}
LAST_SNAPSHOT: .agent-work/tasks/{TASK_ID}/snapshots/{EVENT_ID}.md
RESUME_MODE: {NORMAL / READY_FOR_COMPACTION}
UPDATED_AT: {RFC3339 或 UNKNOWN}

## 目标与交付物

{当前完整目标、交付物和目标路径。}

## 稳定约束与用户决定

{跨压缩必须保留的要求和用户决定；没有变化时原样保留。}

## 授权与待确认动作

{已授权的具体动作和依据；仍需确认的动作；不记录凭据。}

## 计划进度

| STEP_ID | STATUS | RESULT_OR_NEXT | EVIDENCE |
|---|---|---|---|
| S-001 | {PENDING / IN_PROGRESS / DONE / BLOCKED / SKIPPED} | {结果或下一动作} | {路径、命令结果引用或 NONE} |

## 已完成成果与验证

{已产生的文件、结论和实际验证。未验证项不能写成通过。}

## 下一步与验收条件

{恢复后第一项具体动作、依赖、预期结果和完成条件。}

## 阻塞、未知与未验证项

{没有则 NONE。}

## 已否定路线及证据

{失败方法、原始错误或证据路径、不能重复的原因；没有则 NONE。}

## 执行中或结果未知的外部动作

{对象、动作、任务/幂等标识、INTENT/SUCCESS/FAILED/UNKNOWN、查询方式；没有则 NONE。}

## 关键路径

{列出恢复所需输入、修改文件、交付物和证据；每条注明相对于 PROJECT_ROOT 或任务目录。}
