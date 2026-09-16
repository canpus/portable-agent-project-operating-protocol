# 任务生命周期与正式计划

## 触发

新建或续接 TRACKED 任务；创建或修订正式计划；任务完成、取消、等待或阻塞。

## 新建任务

1. 完整读取 `.agent-protocol/SCHEMA.md` 的“目录结构”“ID 规则”“active.md”“task_index.md”和“current_state.md”章节；使用对应模板。
2. 检查 `.agent-work/task_index.md` 中现有 `TASK_ID` 行，选择不冲突的任务 ID。无法可靠取得日期时使用稳定主题加唯一序号，不伪造日期。
3. 创建任务目录、`snapshots/`、空的 `plan.md` 与 `history.md`，再写初始 current_state。没有正式计划时 `PLAN_REF: NONE`、`ACTIVE_STEP: NONE`。
4. 在 task_index 追加 `TASK_CREATED` 块，并将 active.md 指向该 current_state。读回路径和 ID 后，保存 `TASK_CREATED` 检查点。
5. 不移动项目资产，不预建输入、源码、证据和输出目录。

## 续接任务

- 用户已提供任务 ID 或 current_state 路径时，直接按 recovery.md 恢复。
- 用户只说“继续”时，先看 active.md；其目标与当前请求一致即可恢复。
- active 缺失或明显不匹配时，用 task_index 的 `TASK_ID`、`SUBJECT`、`STATUS` 搜索候选。只有多个候选无法区分才询问用户。
- 不因新会话创建新任务，不复制旧任务，不重新分配已存在 ID。

## 正式计划

1. 准备建立两个或以上里程碑的计划时，任务必须是 TRACKED。首次写计划前读取 SCHEMA 的“plan.md”章节。
2. 每个计划修订作为完整 `PLAN_REVISION` 块追加到当前任务 `plan.md`，不得回写旧块。一个修订必须自包含目标、交付物、稳定约束、授权状态、步骤和每步验收条件。
3. 计划步骤是有意义的成果单位，不是每条工具调用。步骤应足以让压缩后的 Agent 判断是否完成、下一步做什么以及需要什么证据。
4. 用户已经明确要求执行任务时，普通、可逆、任务内步骤不等待额外审批。只有用户明确要求“先给计划，批准后再做”，或某个高影响动作尚无具体授权，才设置等待；其他调查和准备继续。
5. 创建修订前用精确搜索检查已有最大 `PLAN_ID` 和 revision。新计划递增 Plan ID；同一目标的修订递增 revision。
6. 新修订的 `SUPERSEDES` 指向被替代版本，并在“修订映射”逐项说明：沿用、已完成、替换、取消或新增。不得使已完成步骤及证据从 current_state 消失。
7. 计划块追加并读回完整性后，更新 current_state 指向新 `PLAN_REF`，保存 `PLAN_CREATED` 或 `PLAN_REVISED` 检查点，然后继续已授权步骤。

## 计划执行

- 开始某一步前，读取 current_state 和当前 PLAN_REF 的精确块，确认步骤未完成、依赖满足、授权范围未变化。
- 步骤验收条件满足后保存 `STEP_COMPLETED` 检查点。条件仅部分满足时保存 `PROGRESS_SAVED`，记录未完成项，不为了进入下一步而写 DONE。
- 目标不变且仍在授权范围内的实现细节可自行调整。交付物、核心约束或高影响动作发生实质变化时，先追加计划修订；只有缺少必要用户决定时暂停受影响步骤。

## 等待、完成和取消

- 等待用户或外部资源：current_state 使用 `WAITING_USER` 或 `BLOCKED`，写明恢复条件并保存检查点；能继续的独立工作先完成。
- 完成：核对所有必要步骤、交付路径和验证，保存 `TASK_COMPLETED`；在 task_index 追加对应事件，active.md 可继续指向该任务，但状态写 DONE。
- 取消：停止新工作，保留已经产生的材料和真实进度，保存 `TASK_CANCELLED` 并更新 task_index。不得自动删除任务记录或项目资产。
- 交付等待人工验收时可以完成 Agent 侧工作，但必须在状态与回复中写明 `待用户验收`，不得声称用户已经接受。
