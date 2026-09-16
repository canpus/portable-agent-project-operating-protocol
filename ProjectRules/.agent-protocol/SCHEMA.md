# PAPOP v4 记录 Schema

## 0. 数据原则

- 本契约只定义数据；是否执行、是否等待由项目入口及当前模式治理规则决定。
- UTF-8，固定大写 ASCII 字段单独占一行：`FIELD: value`。未知 UNKNOWN、不适用 NONE；不留空，不编造时间/ID/批准。
- 时间使用可获得的 RFC3339 时区时间，不能取得写 UNKNOWN。路径注明相对 PROJECT_ROOT；不存秘密或完整原始材料。
- plan、decisions、history、task_index 只追加，旧事实通过新记录纠正；current_state 和 active 是可更新的恢复入口。
- 每个长期块 BEGIN/END 成对且不可嵌套；正文不复用边界标记。机器字段在块头只出现一次，正文采用自然语言或表格，避免制造同名检索行。

## 1. 目录结构

```text
.agent-work/
├── active.md
├── task_index.md
└── tasks/<TASK_ID>/
    ├── current_state.md
    ├── current_state.prev.md
    ├── plan.md
    ├── decisions.md
    ├── history.md
    └── snapshots/<EVENT_ID>.md
```

next 是未提交写入的临时文件，不是恢复权威。只在 TRACKED 创建；PLAN_APPROVAL 的实际任务始终 TRACKED。

## 2. ID 与范围

| 对象 | 格式 | 唯一范围 |
|---|---|---|
| Task | T-YYYYMMDD-slug，冲突加 -02；日期未知可用 T-slug-序号 | 项目 |
| Index event | I- 加 6 位数字 | 项目 |
| Plan | P- 加 4 位数字 | Task |
| Revision | PLAN_ID 加 -R 和 4 位数字 | Task |
| Step | S- 加 3 位数字 | 所属 Plan revision |
| Decision | D- 加 6 位数字 | Task |
| Event/checkpoint | E- 加 6 位数字 | Task |
| Delivery candidate | B- 加 4 位数字 | Task |
| External logical action | X- 加 4 位数字 | Task |
| User gate | G- 加 3 位数字 | Task |

跨任务引用带 TASK_ID。旧 ID 不回收；查现有记录递增，不凭模型记忆猜。继承未变步骤可沿用 ID，改变步骤含义分配新 ID并说明映射。一次外部逻辑动作复用 ACTION_ID 和可用幂等标识；新对象/数据/成本不是同一逻辑动作。

## 3. 枚举

以下表是模板和维护者检查工具的枚举来源。

| 字段/对象 | 允许值 |
|---|---|
| GOVERNANCE_MODE | PLAN_APPROVAL / TASK_DELEGATION |
| RECORD_MODE | AUTO / TRACKED |
| TASK_STATUS（active/index） | ACTIVE / WAITING / BLOCKED / DONE / CANCELLED |
| STATUS（current_state） | PLANNING / EXECUTING / VERIFYING / WAITING_USER / BLOCKED / DONE / CANCELLED |
| WORKFLOW_PHASE | REQUIREMENTS_CONFIRMATION / PLAN_DRAFTING / AWAITING_PLAN_APPROVAL / IMPLEMENTATION / VERIFYING / AWAITING_ACCEPTANCE / REPLAN_REQUIRED / CLOSED |
| AUTHORIZATION_STATUS | PENDING_REQUIREMENTS / PENDING_PLAN / PLAN_AUTHORIZED / TASK_AUTHORIZED / PENDING_ACTION / SUSPENDED |
| AGENT_COMPLETION | NOT_STARTED / IN_PROGRESS / COMPLETE |
| ACCEPTANCE_STATUS | NOT_REQUESTED / AWAITING / ACCEPTED / REJECTED / NOT_REQUIRED |
| RESUME_MODE | NORMAL / READY_FOR_COMPACTION |
| STATUS_AT_WRITE（plan） | AWAITING_APPROVAL / ACTIVE |
| STEP_STATUS | PENDING / IN_PROGRESS / DONE / BLOCKED / SKIPPED |
| GATE_STATUS | PENDING / RELEASED |
| DECISION_TYPE | REQUIREMENTS_CONFIRMED / TASK_AUTHORIZED / PLAN_APPROVED / PLAN_REJECTED / DELIVERY_ACCEPTED / DELIVERY_REJECTED / ACTION_AUTHORIZED / USER_GATE_RELEASED / USER_GATE_CHANGED / GOVERNANCE_CHANGED / CORRECTION |
| DECISION_SOURCE | USER_MESSAGE / USER_INSTRUCTION / UNKNOWN |
| EVENT_TYPE（history） | TASK_CREATED / PLAN_CREATED / PLAN_REVISED / PLAN_ACTIVATED / USER_DECISION / STEP_COMPLETED / PROGRESS_SAVED / DELIVERY_READY / PRE_COMPACTION / RESUMED / EXTERNAL_INTENT / EXTERNAL_RESULT / WAITING / BLOCKED / TASK_COMPLETED / TASK_REOPENED / TASK_CANCELLED / RECOVERY_REPAIR |
| EVENT_STATUS（history） | SUCCESS / PARTIAL / WAITING / BLOCKED / FAILED / UNKNOWN |
| INDEX_EVENT_TYPE | TASK_CREATED / TASK_ACTIVATED / TASK_WAITING / TASK_BLOCKED / TASK_COMPLETED / TASK_CANCELLED |

## 4. active.md

Schema：PAPOP-ACTIVE-4。模板 active.md 定义全部必填字段：SCHEMA、TASK_ID、TASK_STATUS、GOVERNANCE_MODE、SUBJECT、CURRENT_STATE、UPDATED_AT。

完整读取，保持短小，切换活动任务可覆盖。不是授权或任务事实的权威。

## 5. task_index.md

Schema：PAPOP-TASK-INDEX-4。边界 TASK_INDEX_EVENT_BEGIN/END。模板 task-index-event.md 定义必填字段。

同一任务最后一个结构完整、追加顺序最新的事件表示最新索引状态。时间不推翻追加顺序。任务创建、激活/重开、等待、阻塞、完成、取消时追加，普通步骤不追加项目索引。

只允许一个项目索引写入者；多任务并行须由协调者串行分配 I 编号和追加，不能仅凭“只追加”假定无竞态。

## 6. plan.md

Schema：PAPOP-PLAN-4。边界 PLAN_REVISION_BEGIN/END。模板 plan-revision.md 的块头及正文小节全部必填。

- PLAN_REF 是块的精确修订。STATUS_AT_WRITE 保留写入时状态，不因批准或替代回写。
- REQUIREMENTS_CONFIRMATION_REF 引用该提案基于的 REQUIREMENTS_CONFIRMED 决定；PLAN_APPROVAL 必需，委托模式无该确认可写 NONE。
- TASK_AUTHORIZATION_REF 引用 TASK_AUTHORIZED 决定；TASK_DELEGATION 的正式计划必需，审批模式可写 NONE。
- SUPERSEDES 仅记录拟替代关系，不构成激活或授权。
- 已批准修订由 current_state 的 PLAN_REF 和 PLAN_APPROVAL_REF 联合确认。待批新修订只写 PROPOSED_PLAN_REF；旧活动计划引用不丢失。
- 正文须包含目标/交付、范围与排除、核心约束、授权依据与另批动作、用户关卡、步骤/验收、修订映射。每个修订自包含，不要求靠全读旧计划理解。
- 步骤进度表是提案写入时快照；实际进度在核对后的 current_state。不回写旧计划来维护进度。

## 7. decisions.md

Schema：PAPOP-DECISION-4。边界 DECISION_BEGIN/END。模板 decision.md 的字段和正文小节必填。

- DECISION_ID 是稳定审批/授权引用；TARGET_REF 指向精确计划、交付候选、外部动作、用户关卡或 Task。
- PLAN_APPROVED/REJECTED 的 PLAN_REF 和 TARGET_REF 必须一致；批准 rev1 不批准 rev2。
- DELIVERY_ACCEPTED/REJECTED 的 DELIVERY_REF 和 TARGET_REF 一致，正文含实际候选路径、稳定指纹与用户反馈。接受一个候选不接受之后的修改版本。
- ACTION_AUTHORIZED 的 ACTION_ID 和 TARGET_REF 一致，正文记录具体对象、动作、数据、成本、范围及排除项。
- REQUIREMENTS_CONFIRMED 以 TASK_ID 为目标，正文自包含用户实际确认的需求。TASK_AUTHORIZED 以 TASK_ID 为目标，记录委托来源与范围。
- USER_GATE_RELEASED/CHANGED 以 GATE_ID 为目标；模式切换以 TASK_ID 为目标并保存旧/新模式和范围。
- USER_EVIDENCE 保存短原文或准确语义；SOURCE_REF 无稳定消息 ID 时 UNKNOWN。用户来源 UNKNOWN 的决定只能作为待核查线索，不能授予批准。
- 无关 PLAN_REF/DELIVERY_REF/ACTION_ID 写 NONE；CORRECTION_OF 只在纠正旧决定时填旧 DECISION_ID，否则 NONE。错误批准记录的存在不能创造授权，修复时重新核实来源。

## 8. current_state.md

Schema：PAPOP-CURRENT-4。模板 current-state.md 的全部顶层字段及正文小节必填；每次检查点全量写入，稳定目标/约束原样继承，避免反复摘要。

- PLAN_REF：当前激活计划；PROPOSED_PLAN_REF：当前待批提案；没有则 NONE。
- REQUIREMENTS_CONFIRMATION_REF、PLAN_APPROVAL_REF、TASK_AUTHORIZATION_REF、ACCEPTANCE_REF、LAST_DECISION_REF：实际存在的决定 ID，无则 NONE。
- PLAN_APPROVAL 进入实质施工必须 PLAN_AUTHORIZED、精确活动计划及批准引用、需求确认引用均有效。SUSPENDED/PENDING_* 不可执行实质施工。
- TASK_DELEGATION 的 TRACKED 实质执行必须有有效任务委托引用，且没有覆盖当前动作的待批提案、待授权动作或用户关卡。
- ACTIVE_STEP 属于活动 PLAN_REF。待批提案的下一拟执行步骤放正文，不把它写成活动步骤。
- AGENT_COMPLETION: COMPLETE 与 ACCEPTANCE_STATUS: AWAITING 可同时成立；PLAN_APPROVAL 此时 STATUS: WAITING_USER、WORKFLOW_PHASE: AWAITING_ACCEPTANCE，不能 DONE。
- PLAN_APPROVAL 的 DONE 必须 AGENT_COMPLETION: COMPLETE、ACCEPTANCE_STATUS: ACCEPTED、有效 ACCEPTANCE_REF，绑定当前 DELIVERY_REF。
- TASK_DELEGATION 的 DONE 允许 NOT_REQUIRED；如人工验收关卡存在，必须 ACCEPTED 和有效接受引用。
- CANCELLED 不证明人工接受。未完成步骤不标 DONE，执行中或未知外部动作必须保留查询方法。
- 用户关卡表保存 GATE_ID、TARGET、STATUS、DECISION_REF；无关卡写 NONE。有效释放引用只覆盖其目标；状态变化需真实用户决定。
- LAST_EVENT_ID、LAST_EVENT_TYPE、LAST_SNAPSHOT 对应同一有效检查点；初始未提交状态才允许 NONE。

## 9. history.md

Schema：PAPOP-HISTORY-4。边界 HISTORY_EVENT_BEGIN/END。模板 history-event.md 的字段与 CHANGE/EVIDENCE/NEXT 必填。

- 同一任务 EVENT_ID 唯一；PLAN_REF 为事件时活动计划，PROPOSED_PLAN_REF 为待批计划。
- STEP_ID 无计划步骤时 NONE；DECISION_REF 无本事件相关决定时 NONE；ACTION_ID、DELIVERY_REF 无关时 NONE。
- EVENT_STATUS 表示事件结果，不与任务 STATUS、人工验收混用。STEP_COMPLETED 必须在步骤验收条件已满足后使用。
- EXTERNAL_INTENT/RESULT 使用同一 ACTION_ID；结果只能 SUCCESS / FAILED / UNKNOWN。INTENT 不是成功证据，也不是授权。
- SNAPSHOT 指向提交时的完整 current_state 副本，事件只记录本次增量和证据，不重复全文。

## 10. snapshots

snapshots/<EVENT_ID>.md 必须与提交时 current_state 字节完全一致。复制文件，不让模型重述；完成后不回写。发现错误以新检查点修正，保留旧事实。

## 11. 检索与写入验收

```text
rg -n '^PLAN_REF: P-0001-R0002$' .agent-work/tasks/<TASK_ID>/plan.md
rg -n '^DECISION_ID: D-000003$' .agent-work/tasks/<TASK_ID>/decisions.md
rg -n '^TARGET_REF: P-0001-R0002$' .agent-work/tasks/<TASK_ID>/decisions.md
rg -n '^EVENT_ID: E-000014$' .agent-work/tasks/<TASK_ID>/history.md
rg -n '^ACTION_ID: X-0001$' .agent-work/tasks/<TASK_ID>/history.md
rg -n '^TASK_ID: <TASK_ID>$' .agent-work/task_index.md
```

搜索后只读取完整对应块。记录追加前确认 ID 未重复、字段唯一/齐全、枚举合法、引用属于同一任务且存在、真实用户来源和范围相符。读回核对决定、current_state、snapshot、history 和必要索引；不把结构完整误当业务事实正确。
