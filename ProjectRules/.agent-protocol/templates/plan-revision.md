<!-- PLAN_REVISION_BEGIN -->
SCHEMA: PAPOP-PLAN-4
TASK_ID: {TASK_ID}
PLAN_ID: {P- 加 4 位数字}
PLAN_REF: {例如 P-0001-R0001}
SUPERSEDES: {旧 PLAN_REF 或 NONE}
STATUS_AT_WRITE: {AWAITING_APPROVAL / ACTIVE}
REQUIREMENTS_CONFIRMATION_REF: {DECISION_ID 或 NONE}
TASK_AUTHORIZATION_REF: {DECISION_ID 或 NONE}
SUBJECT: {一行主题}
TAGS: {tag-one, tag-two，或 NONE}
CREATED_AT: {RFC3339 或 UNKNOWN}

## 目标与交付物

{完整目标、交付物、实际路径。}

## 范围、核心约束与排除项

{人类确认或委托的范围、核心路线、硬约束及不包含内容。}

## 授权依据、用户关卡与另批动作

{需求确认/任务委托决定、已有具体授权、待批关卡、需要另行授权的对象/动作/数据/成本；没有关卡写 NONE。提案本身不构成批准。}

## 步骤与验收条件

### S-001 | {步骤名称}

| STEP_STATUS | DELIVERABLE | ACCEPTANCE |
|---|---|---|
| PENDING | {有意义的成果} | {可观察、可验证的完成条件} |

{按需要增加步骤。计划审批模式一个步骤也必须先批准。}

## 修订映射

{首次 NONE；后续逐项继承、已完成及证据、替换、取消、新增。}
<!-- PLAN_REVISION_END -->
