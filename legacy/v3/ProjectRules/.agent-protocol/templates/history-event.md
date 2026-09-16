<!-- HISTORY_EVENT_BEGIN -->
SCHEMA: PAPOP-HISTORY-3
EVENT_ID: {E- 加 6 位数字，例如 E-000001}
TASK_ID: {TASK_ID}
PLAN_REF: {例如 P-0001-R0001，或 NONE}
STEP_ID: {例如 S-001，或 NONE}
EVENT_TYPE: {SCHEMA 规定的 EVENT_TYPE}
STATUS: {SUCCESS / PARTIAL / WAITING / BLOCKED / FAILED / UNKNOWN}
SUBJECT: {一行事件主题}
TAGS: {tag-one, tag-two}
SNAPSHOT: .agent-work/tasks/{TASK_ID}/snapshots/{EVENT_ID}.md
RECORDED_AT: {RFC3339 或 UNKNOWN}

## CHANGE

{本事件产生的变化，不重复整个 current_state。}

## EVIDENCE

{直接证据路径或 UNVERIFIED。}

## NEXT

{下一步或等待事项。}
<!-- HISTORY_EVENT_END -->
