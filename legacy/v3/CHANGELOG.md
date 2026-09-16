# Changelog

本文件记录 Portable Agent Project Operating Protocol 的重要变化。

版本格式参考 [Semantic Versioning](https://semver.org/)。v3 的项目规则结构和任务记录格式与旧版不兼容，因此使用新的主版本号。

## 3.0.0 - 2026-09-15

### 重构目的

旧版优先追求完整审计和强流程控制：每个任务默认建立固定目录与多份账本，需求确认、计划批准和验收均设置门槛。它适合需要严格留痕的长期项目，但在一次性或短任务中，规则读取、确认和记账成本可能超过收益。

早期 v2 草案进一步压缩了入口，却使部分约束过于概括：执行型模型需要自行推断条款含义、入口关系和失败处理，GlobalRules 单独使用时指导能力不足。

v3 的目标是取得更稳定的平衡：

- GlobalRules 单独使用也能完整约束 Agent；
- ProjectRules 有唯一、清晰的入口和可观察触发条件；
- 简单任务不承担长期项目的记录成本；
- 多步骤任务在固定里程碑保存可恢复状态；
- 长期计划和历史可用 `rg` / `grep` 精确定位；
- 上下文压缩由用户决定，恢复只加载继续工作所需内容。

### 新增

- 两种独立分发包：
  - `GlobalRules Only`；
  - `GlobalRules + ProjectRules`。
- `RECORD_MODE: AUTO / TRACKED`：AUTO 根据当前任务的恢复需要升级，TRACKED 从任务开始记录。
- FAST 的五项同时满足条件，以及 TRACKED 的明确触发条件。
- `.agent-protocol/` 规则目录和项目入口路由表。
- 正式计划修订、计划步骤完成、准备压缩、外部动作等里程碑事件。
- `PRE_COMPACTION` 保存流程：用户提醒后落盘、核验并暂停新工作。
- 多文件检查点写入中断后的修复流程。
- 外部动作 INTENT / RESULT 记录，避免不确定结果下重复发送、购买或发布。
- `current_state.prev.md` 和不可回写的状态快照。

### Schema 化记录

- 为 `active.md`、`task_index.md`、`plan.md`、`current_state.md`、`history.md` 和 snapshots 定义稳定 Schema。
- 固定检索字段：
  - `TASK_ID`；
  - `PLAN_REF`；
  - `STEP_ID`；
  - `EVENT_ID`；
  - `EVENT_TYPE`；
  - `STATUS`；
  - `SUBJECT`；
  - `TAGS`。
- 固定 `PLAN_REVISION_BEGIN/END`、`HISTORY_EVENT_BEGIN/END` 和 `TASK_INDEX_EVENT_BEGIN/END` 块边界。
- plan、history 和 task index 改为 Search First / Read Narrow：先搜索精确字段，再读取单个记录块。
- history 只追加事件增量和 snapshot 指针；完整旧状态保存在 snapshot，避免每次重新生成整份状态。
- current_state 保持完整但短小，恢复时默认全文读取。

### GlobalRules 变化

- 明确完整的指令层级和材料/指令边界。
- 将用户明确行动请求视为任务内常规步骤授权，减少不必要确认。
- 明确只有实质影响目标、交付、成本、外部对象、敏感数据或不可逆后果的问题才应阻塞询问。
- 加强事实与执行诚实、时效核验、引用、用户前提核查和工具结果验证。
- 加强敏感数据、第三方外发、外部动作、远端结果未知及宿主审批边界。
- 恢复文件、版本控制、依赖环境、失败排查、验证和完成标准。
- 上下文压缩后，当前需要的规则若已不在上下文必须重读；不要求全量重读规则库。

### ProjectRules 变化

- `ProjectRules/AGENTS.md` 成为唯一入口，入口直接定义路径、配置、会话判断、记录模式、生命周期、动作路由和读取策略。
- 正式计划默认在用户已授权任务内继续执行；只有用户要求先审批，或具体高影响动作缺少授权时等待。
- 普通检查点保存后自动继续；用户要求准备压缩时保存后暂停。
- 新会话不再自动等于新任务；任务唯一且用户明确续接时直接恢复。
- 状态文件定义为恢复入口，恢复时必须与实际文件、工具结果和远端状态核对。

### 移除的默认要求

- 每项任务强制创建六类目录；
- 所有任务默认建立完整项目账本；
- 续接旧任务必须双次确认；
- 普通任务必须先确认需求、再批准计划；
- 每个历史事件都在 history 内重复整份 current_state；
- 全项目文件归属登记和每轮人工结算；
- 所有程序强制建立持久日志、日志轮转和关联 ID；
- 使用固定失败次数决定终止整个目标；
- 模型监控上下文占用或使用固定 Token 阈值。

### 破坏性兼容变化

- 旧 `ProjectRules/OPERATING_RULES.md`、`TASK_STATE_MACHINE.md` 和根层旧 `SCHEMA.md` 不再是 v3 执行链的一部分。
- v3 的 ProjectRules 改为 `AGENTS.md + .agent-protocol/`。
- 旧任务目录、计划、current state 和 history 不自动转换为 v3 Schema。
- 不应让旧状态机与 v3 同时管理同一任务，否则可能产生重复审批、重复写入和状态冲突。

### 迁移

1. 在更新前建立 Git 标签或备份。
2. 保留旧任务记录，不批量重写或删除。
3. 安装新的 GlobalRules。
4. 用新项目入口和 `.agent-protocol/` 替换旧项目规则执行链。
5. 仅迁移仍要继续的任务：读取旧 current state 和当前计划，核对实际文件后建立 v3 状态，并保留旧记录路径。
6. 旧发布证据可继续保留为 legacy 资料，但不再代表 v3 当前结构。

### 验证范围

- 已检查两个分发包内的文件完整性和隐藏目录；
- 已检查项目入口引用的所有规则文件；
- 已检查五类模板的必填字段；
- 已检查两个包使用完全相同的 GlobalRules；
- 已检查 ZIP 内文件与源目录内容一致。

尚未在所有 Agent 型号和宿主中完成长期、多轮压缩的行为回归，也没有提供 Token 节省百分比。v3 降低状态丢失、规则重载和重复操作风险，不宣称零故障。

## 0.2.0 - 2026-08-20

### 四层结构与项目记忆

- `ProjectRules` 由三文件扩展为四文件：`AGENTS.md`（宪法层，含触发索引表）、`OPERATING_RULES.md`（触发纪律层，WHEN-THEN）、`TASK_STATE_MACHINE.md`（机制层）、`SCHEMA.md`（契约层）；
- 任务目录更名：`_agent_tasks/` → `tasks/`，避免下划线前缀造成的“隐藏目录”观感；
- 新增项目级机制文件 `TASK_INDEX.md`（任务全景索引，投影式）与 `FILE_INDEX.md`（文件归属登记，追加式流水）；
- 新增跨任务续接协议：新会话先读 `TASK_INDEX.md` 判定归属，用户首句提及旧任务并经双次确认后直接续接，不新建任务、不另立索引区块；
- 新增轮次关闭前的文件归属结算流程；
- README 中英双语同步；路径占位符统一为“你的用户名”，并明确禁止添加括号。

## 0.1.0 - 2026-08-19

### 初始发布

- 发布 `GlobalRules/AGENTS.md` 全局行为基线；
- 发布 `ProjectRules/` 三文件架构（`AGENTS.md`、`TASK_STATE_MACHINE.md`、`SCHEMA.md`）；
- 提供任务状态机、三本账与计划审批流程；
- 提供上下文恢复、用户验收与跨工具安装说明。
