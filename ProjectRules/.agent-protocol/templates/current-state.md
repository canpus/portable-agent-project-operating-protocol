SCHEMA: PAPOP-CURRENT-4
TASK_ID: {TASK_ID}
GOVERNANCE_MODE: {PLAN_APPROVAL / TASK_DELEGATION}
STATUS: {PLANNING / EXECUTING / VERIFYING / WAITING_USER / BLOCKED / DONE / CANCELLED}
WORKFLOW_PHASE: {SCHEMA 的 WORKFLOW_PHASE}
AUTHORIZATION_STATUS: {SCHEMA 的 AUTHORIZATION_STATUS}
AGENT_COMPLETION: {NOT_STARTED / IN_PROGRESS / COMPLETE}
ACCEPTANCE_STATUS: {NOT_REQUESTED / AWAITING / ACCEPTED / REJECTED / NOT_REQUIRED}
SUBJECT: {一行主题}
TAGS: {tag-one, tag-two，或 NONE}
PLAN_REF: {活动精确修订或 NONE}
PROPOSED_PLAN_REF: {待批精确修订或 NONE}
ACTIVE_STEP: {活动计划的 STEP_ID 或 NONE}
REQUIREMENTS_CONFIRMATION_REF: {DECISION_ID 或 NONE}
PLAN_APPROVAL_REF: {DECISION_ID 或 NONE}
TASK_AUTHORIZATION_REF: {DECISION_ID 或 NONE}
DELIVERY_REF: {例如 B-0001，或 NONE}
ACCEPTANCE_REF: {DECISION_ID 或 NONE}
LAST_DECISION_REF: {DECISION_ID 或 NONE}
LAST_EVENT_ID: {EVENT_ID；初始未提交才可 NONE}
LAST_EVENT_TYPE: {SCHEMA 的 EVENT_TYPE；初始未提交才可 NONE}
LAST_SNAPSHOT: {.agent-work/tasks/TASK_ID/snapshots/EVENT_ID.md；初始未提交才可 NONE}
RESUME_MODE: {NORMAL / READY_FOR_COMPACTION}
UPDATED_AT: {RFC3339 或 UNKNOWN}

## 目标与交付物

{当前完整目标、交付物及路径。}

## 稳定约束与用户决定

{稳定约束、实际已确认需求/委托范围、决定引用；没有变化时原样继承。}

## 授权与待确认动作

{当前批准/委托范围、批准排除项、待批准提案及另批动作，不把提案写成已批准。}

## 用户关卡

| GATE_ID | TARGET | GATE_STATUS | DECISION_REF |
|---|---|---|---|
| {G-001} | {精确计划/步骤/动作/边界} | {PENDING / RELEASED} | {释放/变更决定或 NONE} |

{无关卡删除示例行并写 NONE。}

## 计划进度

| PLAN_REF | STEP_ID | STEP_STATUS | RESULT_OR_NEXT | EVIDENCE |
|---|---|---|---|---|
| {活动计划} | {S-001} | {PENDING / IN_PROGRESS / DONE / BLOCKED / SKIPPED} | {结果或下一动作} | {路径或 NONE} |

{没有活动计划写 NONE；待批提案的拟执行步骤在下一步说明。}

## 已完成成果、验证与交付候选

{实际成果、验证/未验证项、DELIVERY_REF、候选路径及稳定指纹。}

## 人工验收与反馈

{当前候选的待验收/接受/拒绝及真实反馈来源；Agent 完成不等于用户接受。}

## 下一步与验收条件

{下一项允许动作、依赖和完成条件；待批时只列允许的调查/记录及需要的人类决定。}

## 阻塞、未知与未验证项

{具体恢复条件，无则 NONE。}

## 已否定路线及证据

{失败路线、原始错误/证据路径和避免机械重试原因，无则 NONE。}

## 执行中或结果未知的外部动作

{ACTION_ID、对象/动作/范围、授权决定、幂等标识、INTENT/SUCCESS/FAILED/UNKNOWN、查询方法；不写凭据。无则 NONE。}

## 关键路径

{恢复需要的输入、修改、交付及证据，注明相对 PROJECT_ROOT。}
