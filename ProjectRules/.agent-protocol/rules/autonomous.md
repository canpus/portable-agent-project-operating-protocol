# 自主推进模式

`GOVERNANCE_MODE=AUTONOMOUS`。

- 用户清楚提出创建、修复、更新或交付任务时，追加 `TASK_AUTHORIZED`，并在授权范围内持续推进。
- Agent 可自行整理 Goal、划分 Stage、维护 Plan、施工和运行验证，不强制经过严格模式的四个人工审查点。
- 缺关键决定、需要具体外部授权、存在不可逆后果、遇到用户设置的关卡或最终 Goal 将发生实质变化时，提交等待检查点后询问。
- 用户明确要求审查某一 Goal、Plan、动作或 Delivery 时，该要求成为精确关卡，不能用总体任务授权绕过。
- Agent 完成与用户验收分开。未要求验收时使用 `ACCEPTANCE_STATUS=NOT_REQUIRED`；不得写成 `ACCEPTED`。
