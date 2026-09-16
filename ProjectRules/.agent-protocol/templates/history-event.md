<!-- HISTORY_EVENT_BEGIN -->
SCHEMA: PAPOP-HISTORY-4
EVENT_ID: {E- 加 6 位数字}
TASK_ID: {TASK_ID}
PLAN_REF: {活动修订或 NONE}
PROPOSED_PLAN_REF: {待批修订或 NONE}
STEP_ID: {STEP_ID 或 NONE}
DECISION_REF: {本事件相关 DECISION_ID 或 NONE}
DELIVERY_REF: {本事件相关候选或 NONE}
ACTION_ID: {本事件相关逻辑动作或 NONE}
EVENT_TYPE: {SCHEMA 的 EVENT_TYPE}
EVENT_STATUS: {SUCCESS / PARTIAL / WAITING / BLOCKED / FAILED / UNKNOWN}
SUBJECT: {一行主题}
TAGS: {tag-one, tag-two，或 NONE}
SNAPSHOT: .agent-work/tasks/{TASK_ID}/snapshots/{EVENT_ID}.md
RECORDED_AT: {RFC3339 或 UNKNOWN}

## CHANGE

{本事件增量，不重复整份状态；明确批准/委托/待验收的真实变化。}

## EVIDENCE

{本事件相关项目路径、真实验证或用户决定引用；未验证写 UNVERIFIED。}

## NEXT

{下一允许动作或等待的具体决定。}
<!-- HISTORY_EVENT_END -->
