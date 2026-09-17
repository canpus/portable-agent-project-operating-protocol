# 严格审批模式

`GOVERNANCE_MODE=STRICT_APPROVAL`。主循环：

```text
需求讨论与澄清
→ [用户确认需求]
→ 写入 Goal 提案
→ [用户审批 Goal]
→ 撰写本阶段 Plan
→ [用户审批 Plan]
→ 施工、验证与提交 Delivery
→ [用户验收 Delivery]
→ STAGE_CLOSED
→ 下一 Stage Plan
```

## 四个审查点

1. `REQUIREMENTS_CONFIRMED` 精确绑定 `REQUIREMENTS_REF`。请求确认前，Current State 必须包含完整需求草案并已生成 Snapshot；拒绝后回到澄清。
2. 需求确认后才能追加 Goal 提案。`GOAL_APPROVED` 精确绑定 `GOAL_REF`；拒绝后追加新 Goal Revision，不覆盖旧版。
3. Goal 批准后才能追加当前 Stage Plan。`PLAN_APPROVED` 精确绑定 `PLAN_REF`；拒绝或实质变更形成新 Revision 并重新审批。
4. 执行与机器验证完成后形成 `DELIVERY_REF`。`DELIVERY_ACCEPTED` 必须绑定当前 Delivery；拒绝后进入返工。返工改变已批 Plan 实质范围时重新审批 Plan。

已批准 Plan 内的普通施工步骤不逐步请求审批；用户指定关卡、具体外部动作和高影响操作仍按各自规则等待。未通过当前审查点不能进入下一 Phase，旧版本批准不能用于新 Requirements、Goal、Plan 或 Delivery。
