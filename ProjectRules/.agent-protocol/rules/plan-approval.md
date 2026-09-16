# 计划审批模式 — PLAN_APPROVAL

## 定位

人类确认需求、批准精确计划修订，Agent 在该计划边界内执行，人类验收后关闭。所有实际任务使用 TRACKED；纯咨询不进入此流程。

这是计划与阶段审批，不是每条工具调用或每个计划步骤都重新审批。用户要求更细关卡时按 governance.md 记录并遵守。

## 状态与关卡

```text
REQUIREMENTS_CONFIRMATION
  --用户明确确认需求--> PLAN_DRAFTING
  --正式提案落盘--> AWAITING_PLAN_APPROVAL
  --用户批准精确修订--> IMPLEMENTATION
  --施工及 Agent 验证完成--> AWAITING_ACCEPTANCE
  --用户接受具体交付--> CLOSED / DONE

AWAITING_PLAN_APPROVAL --拒绝/修改--> REQUIREMENTS_CONFIRMATION
IMPLEMENTATION --实质范围变化--> REPLAN_REQUIRED
AWAITING_ACCEPTANCE --范围内返工--> IMPLEMENTATION
AWAITING_ACCEPTANCE --实质范围变化--> REPLAN_REQUIRED
REPLAN_REQUIRED --> REQUIREMENTS_CONFIRMATION
```

## 需求确认

1. 先做允许的只读调查，向用户提交可审阅的目标、输入、范围、核心约束、交付物、验收条件和关键未知。
2. 等待用户明确确认理解。用户原始任务请求不是对 Agent 需求复述的自动确认。已有可核验的明确确认可以复用，不重复询问。
3. 记录 REQUIREMENTS_CONFIRMED 决定及其完整确认内容。未确认前不提交正式计划提案、不实质施工；必要调查和协议记录可以继续。

## 计划审批

1. 需求确认后，按 lifecycle.md 追加自包含计划修订。至少一个有意义的成果步骤；不因任务小跳过关卡。
2. 新提案 STATUS_AT_WRITE: AWAITING_APPROVAL，current_state 的 PROPOSED_PLAN_REF 指向它；没有获批计划时 PLAN_REF: NONE、PLAN_APPROVAL_REF: NONE、AUTHORIZATION_STATUS: PENDING_PLAN。
3. 交给用户审阅精确修订并等待。用户明确“批准这个计划”且上下文唯一时可绑定该修订，不强制用户手输 ID。
4. 批准：追加 PLAN_APPROVED 决定，绑定修订、批准范围和排除项；读回后激活 PLAN_REF、PLAN_APPROVAL_REF，清空 PROPOSED_PLAN_REF，AUTHORIZATION_STATUS: PLAN_AUTHORIZED，保存 PLAN_ACTIVATED 后执行。
5. 拒绝：追加 PLAN_REJECTED，保留旧提案，记录反馈，返回需求确认；新提案必须使用新 revision。
6. 沉默、补充材料、确认理解、“接着看看”不算计划批准。审批结果不明确时保持等待。

## 执行与重新审批

- 每一步开始前核对 PLAN_REF 对应的 PLAN_APPROVED 决定及范围、依赖和用户关卡。
- 当前已批准范围内的实现调整、调试、验证可自主进行。保存 STEP_COMPLETED 后可继续下一已批准步骤。
- 新目标、新交付物、核心约束或关键路线实质变化：停止实质施工，AUTHORIZATION_STATUS: SUSPENDED，WORKFLOW_PHASE: REPLAN_REQUIRED，保存检查点；先确认新需求，再追加修订并等待新批准。
- 旧批准引用和已完成证据保留，待批提案不会自行取代旧计划。重新审批前只进行允许的调查与协议记录。
- 高影响动作依然检查具体另行授权；即使已批准计划也不得绕过其审批排除项。

## 交付与人工验收

1. Agent 侧工作及必要验证完成后，记录具体 DELIVERY_REF、路径/指纹和验证，AGENT_COMPLETION: COMPLETE，ACCEPTANCE_STATUS: AWAITING。
2. 保存 DELIVERY_READY，STATUS: WAITING_USER、WORKFLOW_PHASE: AWAITING_ACCEPTANCE。交付候选并等待；不能提前写 TASK_COMPLETED 或 DONE。
3. 用户明确接受该候选：追加 DELIVERY_ACCEPTED，保存决定与 TASK_COMPLETED，状态 DONE / CLOSED。
4. 用户拒绝且返工仍在当前批准范围：追加 DELIVERY_REJECTED，保存反馈；使用当前计划批准进入返工，无需新计划。修复后形成新 DELIVERY_REF，再次等待验收。
5. 反馈构成实质范围变化则进入重新审批；反馈不明确不能猜验收结论。
6. 用户明确取消时保留进度，保存 TASK_CANCELLED，不把取消写成验收合格。新独立目标另建任务，不自动沿用旧批准。
