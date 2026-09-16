# AGENTS.md — PAPOP v4 项目执行与状态入口

## 0. 入口、路径与配置

- 本文件适用于其所在目录及子目录；`PROJECT_ROOT` 即本文件所在目录。
- `PROTOCOL_VERSION: 4.0.1`
- `GOVERNANCE_MODE: @@GOVERNANCE_MODE@@`
- `RECORD_MODE: @@RECORD_MODE@@`
- GOVERNANCE_MODE 只允许 `PLAN_APPROVAL / TASK_DELEGATION`，决定执行授权和关闭关卡；RECORD_MODE 只允许 `AUTO / TRACKED`，决定是否记录。两者不能互相替代。
- PLAN_APPROVAL 的实际任务必须 TRACKED，即使只修改一个文件；纯问答和不改变项目的讨论不建账、不进入审批流程。
- 本文件是唯一项目入口。详细规则在 `.agent-protocol/rules/`，契约在 `.agent-protocol/SCHEMA.md`，模板在 `.agent-protocol/templates/`。状态只写入 `<PROJECT_ROOT>/.agent-work/`，不搬动源码、输入、证据或交付物。
- 首次加载时读取本节、会话入口和当前模式对应的治理规则；不要预读整个规则库、Schema、历史或旧计划。
- 配置缺失、未替换、非法，或 PLAN_APPROVAL 配成 AUTO 时，不自行选择宽松模式。保持只读调查，指出具体配置问题。

## 1. 会话入口

1. 理解用户当前目标。先读取当前模式的治理规则：PLAN_APPROVAL → `.agent-protocol/rules/plan-approval.md`；TASK_DELEGATION → `.agent-protocol/rules/task-delegation.md`。只加载当前模式。
2. 独立新目标按记录模式判定处理；新会话不自动等于新任务，旧任务也不自动吸收无关目标。
3. 用户说“继续、恢复、压缩后继续”或给出状态路径时，按 recovery.md 恢复。明确任务 ID 或路径不需要双次确认；只有多个候选无法区分才询问。
4. 用户要求保存或准备压缩时，按 checkpoint.md 保存真实进度，核验后停止新工作；用户明确要求“保存后继续”时，仍需先通过当前治理关卡。
5. 状态记录的 GOVERNANCE_MODE 必须与项目配置一致。发现冲突不自行重置状态或降级审批；按 governance.md 核对用户决定。
6. 纯问答、规则安装检查和讨论不建立任务账本。不要因为查看规则、验证配置就进入计划审批。

## 2. 记录模式

### TRACKED

PLAN_APPROVAL 的所有实际任务均使用 TRACKED。TASK_DELEGATION 配成 TRACKED 时也从实际任务开始记录。

AUTO 下出现任一条件即升级 TRACKED：

- 准备建立两个或以上成果里程碑的正式计划；
- 已有后续工作依赖、需要保存的中间成果或复杂决定；
- 需要等待用户、后台任务、外部结果，或交接、跨会话、压缩后继续；
- 存在结果可能不确定、恢复后不能盲目重试的外部动作；
- 用户要求正式计划、状态、历史、授权记录落盘或指定执行关卡。

### FAST

只允许 TASK_DELEGATION + AUTO，且以下条件全部成立：无正式计划；预计连续工作可完成；无等待；无需要跨会话保留的中间决定；用户未要求记录、交接或执行关卡。

FAST 仍遵守全局规则、治理规则和当前动作规则。升级时立即保存已有真实事实，不补造过去事件。任务结束前不从 TRACKED 降回 FAST。

## 3. 共用生命周期与检查点

1. TRACKED 的新建、正式计划、交付、返工、关闭按 lifecycle.md；授权和人工决定按 governance.md 及当前模式规则。
2. 正式计划写入或修订后保存 PLAN_CREATED / PLAN_REVISED。写入计划不等于批准计划；PLAN_APPROVAL 的新提案不会自动替换已批准计划。
3. 每个计划步骤满足验收条件后保存 STEP_COMPLETED；部分完成保存 PROGRESS_SAVED，不标 DONE。
4. 用户决定、授权变化、交付待验收、等待、阻塞、外部动作前后、完成或取消均按 checkpoint.md 保存。
5. 检查点保存后能否继续由治理规则和未释放的用户关卡决定。PLAN_APPROVAL 可继续当前已批准计划内步骤；TASK_DELEGATION 可继续当前已委托范围。不得把检查点读回成功当成人类批准。
6. 准备压缩保存 PRE_COMPACTION，保持真实审批和验收状态，保存后等待；恢复不能越过原有等待关卡。
7. current_state 是完整但短小的恢复入口；plan、decisions、history 和 task_index 只追加。完整历史状态在不可回写 snapshots 中。

## 4. 按动作加载规则

对应完整规则已在上下文时不重复读取；压缩后缺失则重读当前需要的文件。

| 动作 | 必读文件（相对 PROJECT_ROOT） |
|---|---|
| 判断当前模式、执行前授权、用户关卡、切换模式、人工验收 | `.agent-protocol/rules/governance.md` 及当前模式规则 |
| 新建、正式计划、计划修订、交付、返工、关闭 | `.agent-protocol/rules/lifecycle.md` |
| 检查点、历史、准备压缩 | `.agent-protocol/rules/checkpoint.md` |
| 恢复、中断、记录或配置冲突 | `.agent-protocol/rules/recovery.md` |
| 文件写入、覆盖、移动、删除、Git 状态变更 | `.agent-protocol/rules/workspace.md` |
| 代码、脚本、配置实现与调试 | `.agent-protocol/rules/implementation.md` |
| 联网核验、易变化事实 | `.agent-protocol/rules/verification.md` |
| 外发、发送、发布、购买、生产、权限、全局环境、破坏性操作 | `.agent-protocol/rules/external-actions.md` |

首次创建记录、字段不确定、写入或修复时，按 SCHEMA 标题定位有关章节；不默认加载全文。模板不能替代治理判断。

## 5. Search First / Read Narrow

- 恢复时完整读取 active 和 current_state。
- plan、decisions、history 和 task_index 默认先搜索稳定字段，再读取对应 BEGIN/END 块。
- 检索键：TASK_ID、PLAN_REF、PROPOSED_PLAN_REF、DECISION_ID、DELIVERY_REF、ACTION_ID、STEP_ID、EVENT_ID、EVENT_TYPE、STATUS、SUBJECT、TAGS。
- 不拼接不同记录块。无命中先检查路径、拼写、大小写、转义和 Schema 版本，不立即认定记录不存在。
- 只有完整审计、损坏修复或文件很小且全读成本可忽略时全读长期记录。

## 6. 实际事实、并发和权限

- 状态不能扩大真实授权；用户最新指令、实际文件、运行和远端结果可能使旧状态过时。恢复时核对下一步依赖及授权范围。
- 同一任务账本只有一个写入者；委派不能扩大范围、另建该任务或并发写账本。没有明确需要时不启动子 Agent。
- 出现不明并发修改时暂停冲突写入，继续允许的只读调查；无法确定归属时说明具体冲突。
- 不复制完整聊天、源码、长日志或原始材料到状态；记录稳定结论、短授权依据、路径及必要指纹，不记录秘密。

## 7. 完成与沟通

- 执行前必须等待时，给出具体需求、PLAN_REF、交付候选或动作范围，明确当前关卡。不要提出无法审阅的笼统批准请求。
- 只有 current_state、snapshot、history 和决定引用核对一致才能说“已落盘”；未修复写入失败不得声称可安全压缩。
- 最终说明成果、实际路径、验证、未验证项和审批/验收状态；人工接受不得由模型代签。
- 不自行修改模式以绕开等待，不同时启用两套项目入口，不为账本移动资产或安装全局工具。

## 8. 项目特有约束

由维护者填写真实构建/测试入口、保护目录、目标平台和交付格式。不要复制完整规则库或临时任务状态。
