# 任务委托模式 — TASK_DELEGATION

## 定位

用户委托目标，Agent 在授权范围内持续推进。缺少关键决定、具体高影响动作授权，或到达用户明确指定的关卡时等待。

默认 RECORD_MODE: AUTO；简单任务 FAST，需要计划、等待、恢复或用户关卡时 TRACKED。是否建账不改变权限。

## 任务授权与计划

1. 明确行动请求可授权普通、可逆、任务内必要步骤。纯分析请求不能授权项目施工；新对象、新敏感数据范围、新成本和不可逆影响不能从模糊请求推定。
2. TRACKED 时记录 TASK_AUTHORIZED 决定，包含目标、范围、约束、用户请求来源及排除项，current_state 的 TASK_AUTHORIZATION_REF 指向它。
3. 目标清楚时不强制复述确认；复杂任务建立成果步骤和验收条件。正式计划 STATUS_AT_WRITE: ACTIVE，基于任务授权激活 PLAN_REF；PLAN_APPROVAL_REF: NONE、AUTHORIZATION_STATUS: TASK_AUTHORIZED。
4. 用户要求先审计划时保存待批 PROPOSED_PLAN_REF 和具体关卡，不能激活该提案执行；按 governance.md 记录其精确 PLAN_APPROVED 决定。这里的人工批准不把整个任务默认切成 PLAN_APPROVAL。
5. FAST 不要求正式计划和账本；出现记录触发立即升级，记已有真实事实及当前有效授权，不补造曾经的事件。

## 执行与修订

- 已授权范围内实现、调试、验证和普通里程碑持续执行，不逐步询问是否继续。
- 每个正式计划步骤完成后保存 STEP_COMPLETED；保存成功仍需核对授权与用户关卡。
- 目标不变且在授权范围内的实现细节自行调整。交付物、核心约束或高影响动作发生实质变化时先追加修订并核对授权；用户已明确授权变化且没有人工关卡覆盖时可激活执行。
- 缺少关键用户决定或具体动作授权时暂停受影响工作，保存 WAITING_USER/BLOCKED 和恢复条件；当前范围内其他允许的工作继续。
- 用户指定的待批计划或执行关卡不能因“可逆”“已保存”被跳过；修改其批准范围需要重新获得对应决定。

## 外部动作与完成

1. 外发、发布、购买、生产、权限和破坏性动作按 external-actions.md 检查具体授权；重要但已获具体授权的动作无需重复询问。
2. 所有必要成果和 Agent 验证完成，可保存 TASK_COMPLETED，STATUS: DONE、WORKFLOW_PHASE: CLOSED、AGENT_COMPLETION: COMPLETE。
3. 用户未要求人工验收时 ACCEPTANCE_STATUS: NOT_REQUIRED。这表示协议允许 Agent 侧关闭，不表示人类已接受交付。
4. 用户明确要求验收后关闭时，保存 DELIVERY_READY，保持 WAITING_USER / AWAITING_ACCEPTANCE，直到接受具体候选；拒绝则记录反馈并在有效授权内返工。
5. 关闭后用户指出当前目标内缺陷，可在同一任务保存 TASK_REOPENED 后修复，重新核对范围和关卡；独立新目标另建任务。
6. 取消保留真实状态和材料，不自动清理。准备压缩时保存并暂停，不能把当前授权理解成允许跨越用户的停止要求。
