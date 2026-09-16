<!-- PLAN_REVISION_BEGIN -->
SCHEMA: PAPOP-PLAN-3
TASK_ID: {TASK_ID}
PLAN_ID: {P- 加 4 位数字，例如 P-0001}
PLAN_REF: {PLAN_ID 加 -R 和 4 位数字，例如 P-0001-R0001}
SUPERSEDES: {旧 PLAN_REF 或 NONE}
STATUS: {DRAFT / ACTIVE / AWAITING_APPROVAL / SUPERSEDING_PROPOSAL}
SUBJECT: {一行计划主题}
TAGS: {tag-one, tag-two}
CREATED_AT: {RFC3339 或 UNKNOWN}

## 目标与交付物

{任务目标、实际交付物和目标路径。}

## 约束与授权

{用户要求、项目约束、已授权范围，以及必须等待确认的具体动作。}

## 步骤与验收条件

### S-001 | {步骤名称}

- STATUS: PENDING
- DELIVERABLE: {本步骤产生的有意义成果}
- ACCEPTANCE: {可观察、可验证的完成条件}

### S-002 | {步骤名称}

- STATUS: PENDING
- DELIVERABLE: {本步骤成果}
- ACCEPTANCE: {完成条件}

## 修订映射

{首次修订写 NONE；后续逐项说明旧步骤的继承、替换、取消、新增和已完成证据。}
<!-- PLAN_REVISION_END -->
