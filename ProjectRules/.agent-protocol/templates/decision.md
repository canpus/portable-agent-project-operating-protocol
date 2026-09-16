<!-- DECISION_BEGIN -->
SCHEMA: PAPOP-DECISION-4
DECISION_ID: {D- 加 6 位数字}
TASK_ID: {TASK_ID}
DECISION_TYPE: {SCHEMA 的 DECISION_TYPE}
DECISION_SOURCE: {USER_MESSAGE / USER_INSTRUCTION / UNKNOWN}
SOURCE_REF: {可核验消息/指令引用，无法取得 UNKNOWN}
TARGET_REF: {TASK_ID / 精确 PLAN_REF / DELIVERY_REF / ACTION_ID / GATE_ID}
PLAN_REF: {精确修订或 NONE}
DELIVERY_REF: {交付候选或 NONE}
ACTION_ID: {逻辑动作或 NONE}
CORRECTION_OF: {旧 DECISION_ID 或 NONE}
SUBJECT: {一行决定主题}
TAGS: {tag-one, tag-two，或 NONE}
RECORDED_AT: {RFC3339 或 UNKNOWN}

## USER_EVIDENCE

{真实用户短原文或准确语义，明确是原文还是摘要；没有用户证据不能伪造批准。}

## SCOPE_AND_EXCLUSIONS

{确认需求或授权的完整范围、约束、验收条件及排除项；外部授权包括对象/动作/数据/成本；模式切换包括旧/新模式和适用任务。}

## TARGET_EVIDENCE

{精确计划路径/修订、具体交付路径与指纹、逻辑动作或关卡目标；TASK 级决定说明当前目标。不适用 NONE。}
<!-- DECISION_END -->
