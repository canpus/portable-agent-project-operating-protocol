# 共用任务生命周期与正式计划

## 新建与续接

1. 先按项目入口及当前治理模式判断是否实际任务、是否 TRACKED。PLAN_APPROVAL 实际任务始终 TRACKED；纯讨论不建账。
2. 新建 TRACKED 时读取 SCHEMA 的目录、ID、active、task_index、current_state 章节。检查现有 TASK_ID，创建任务目录、snapshots、空 plan.md、decisions.md、history.md。
3. 初始 current_state 使用真实模式、目标和约束；计划、提案、决定、候选引用都为 NONE；LAST_EVENT_ID 初次写入前为 NONE。按 checkpoint.md 保存 TASK_CREATED，同时建立索引与 active 指针。
4. 当前模式所需的用户请求授权或确认，由治理规则记录决定及后续检查点。不得先填一个尚不存在的批准引用。
5. 不创建固定六目录，不搬动项目资产。明确任务 ID 或路径按 recovery.md 直接续接；只有无法区分候选才询问。

## 自包含计划修订

1. 首次写计划前定位 SCHEMA 的 plan.md。检查已有 PLAN_ID/revision，递增分配，不回收 ID。
2. 每个修订追加完整 PLAN_REVISION 块：目标/交付物、确认或委托依据、范围/排除项、核心约束、步骤、每步验收条件、风险及另行授权、用户关卡、修订映射。
3. 步骤是有意义的成果单位，不是每条工具调用。一个实际任务也可只有一个步骤；两个或以上正式里程碑必为 TRACKED。
4. PLAN_APPROVAL 在需求确认后写待批提案；TASK_DELEGATION 在已有授权范围内写 ACTIVE，用户先审要求覆盖的计划仍待批。
5. SUPERSEDES 说明拟替代关系，本身不证明新提案已生效。待批提案写 PROPOSED_PLAN_REF；PLAN_REF 始终指向当前已激活的修订，无有效当前计划写 NONE。
6. 不改变旧块状态。新修订逐项说明继承、已完成、替换、取消或新增；改变步骤含义时分配新 STEP_ID，保留已完成证据。
7. 计划追加并读回后保存 PLAN_CREATED/PLAN_REVISED；符合治理要求激活时保存 PLAN_ACTIVATED。不得因为计划已写入而跳过待批状态。

## 每步执行

- 开始前完整读取 current_state，精确定位 PLAN_REF 和必要决定块；核对模式、当前批准/委托、未释放关卡、依赖、步骤未完成及动作具体授权。
- 实际事实与状态冲突先修正。不能仅根据 plan 步骤写 PENDING 认定尚未执行；当前进度以核对后的 state 为入口。
- 达到验收条件才保存 STEP_COMPLETED；部分完成 PROGRESS_SAVED；等待 WAITING，阻塞 BLOCKED。未完成不可为进入下一步而标 DONE。
- 范围变化按当前治理模式处理。保存成功后是否继续由治理规则决定。

## 交付、返工、等待与关闭

1. Agent 侧成果和验证完成，递增分配 DELIVERY_REF，记录实际候选路径、版本/指纹、证据和未验证项。源码改动保留 canonical path，以稳定 diff/提交基线和证据绑定候选，不擅自提交。
2. 需要人工验收：保存 DELIVERY_READY，AGENT_COMPLETION: COMPLETE、ACCEPTANCE_STATUS: AWAITING、STATUS: WAITING_USER、WORKFLOW_PHASE: AWAITING_ACCEPTANCE。PLAN_APPROVAL 默认始终需要。
3. 不需要人工验收的 TASK_DELEGATION：保存 TASK_COMPLETED，ACCEPTANCE_STATUS: NOT_REQUIRED。不能写 ACCEPTED。
4. 接受/拒绝记录到 decisions 并保存 USER_DECISION；接受后才完成人工验收流程；拒绝记录候选及反馈，范围内返工沿用有效批准/委托，新候选使用新 DELIVERY_REF。
5. 等待或阻塞写明受影响动作、具体恢复条件、仍允许做的工作，保存检查点；不能把“尚待批准”写成工具故障。
6. 完成/取消时向 task_index 追加对应事件并更新 active；保留全部证据和原材料，不自动删除。
7. DONE 表示当前治理模式的关闭条件满足。恢复已关闭任务只报告现状，不自动重新执行；用户明确请求范围内返工可保存 TASK_REOPENED 再执行，人工验收模式仍保留原有审批要求。
