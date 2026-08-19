# AGENTS.md — 项目级 Agent 工作纪律（宪法层）

**适用范围**：本文件所在目录及其项目树。  
**PROJECT_ROOT**：本 `AGENTS.md` 所在目录。  
**默认 TASKS_ROOT**：`<PROJECT_ROOT>/tasks/`。  
**默认项目时区**：`Asia/Shanghai`（UTC+8）；若项目已有明确时区约定，以项目约定为准。  
**定位**：本文件是**宪法层**：只定义永久约束、风险时刻条款与流程开关。具体执行细节一律在 `OPERATING_RULES.md`（触发纪律层）；状态流转在 `TASK_STATE_MACHINE.md`（机制层）；记录格式在 `SCHEMA.md`（契约层）。

> 本规则不假定特定模型、厂商、IDE、CLI、工具名称或上下文长度。实际宿主的系统规则、安全策略、权限边界与真实工具能力始终优先；不得假装不存在的能力可用。

---

## 0. 权威文件与职责分工

项目根目录长期有效的四份规范：

1. **`AGENTS.md`**（本文件）
   - 定义：宪法层——永久约束、风险时刻条款、流程开关（该不该做、往哪走）。
2. **`OPERATING_RULES.md`**
   - 定义：触发纪律层——条件触发的执行细节（WHEN 什么情况 THEN 怎么做）。
3. **`TASK_STATE_MACHINE.md`**
   - 定义：机制层——状态、进入/退出条件、用户门控、上下文恢复协议。
4. **`SCHEMA.md`**
   - 定义：契约层——plan.md、task_current_state.md、task_history.md、cases/、TASK_INDEX.md、FILE_INDEX.md 的字段、ID、格式、证据和交叉引用。

**职责判定：**
- “该不该做、往哪个流程走” → 本文件（含 §5 触发索引表）
- “具体怎么做（条件触发）” → `OPERATING_RULES.md`
- “什么时候写 / 什么时候必须等待用户 / 什么时候允许进入下一阶段” → `TASK_STATE_MACHINE.md`
- “写哪些字段 / ID 怎么分配 / 记录长什么样” → `SCHEMA.md`
- “文件放哪里 / 哪些不能动 / 谁负责治理” → 本文件 §2、§4

四者直接冲突时，不得自行选择更方便的一方；停止冲突步骤并向用户说明。用户当前明确指令可以改变当前 Task 的后续要求，但不得回写或篡改已经形成的 Append-Only 记录。

### 0.1 权威文件必须按需实际读取

不得只凭模型记忆声称“遵循了”指针文件：

- 首次创建 Task 或即将发生生命周期状态转换时，如果对应规则不在当前上下文，先按状态名/标题定位并读取 `TASK_STATE_MACHINE.md` 的相关章节。
- 即将写入任何账本或登记文件时，如果对应契约不在当前上下文，先按子 Schema 名、字段名或标题定位并读取 `SCHEMA.md` 的相关章节。
- 执行条件触发动作前，按 §5 触发索引表定位并读取 `OPERATING_RULES.md` 的相关章节。
- 读取规则文件属于必要验证，不得以“模型大概记得”为由跳过。

---

## 1. 顶层会话与任务（流程开关）

本规则中的 **Top-Level Session** 指由用户直接发起、承载当前项目工作的顶层 Agent 会话/执行上下文。不同宿主可称为 conversation、chat、session、thread、run 等。

**核心判定（流程开关，任何对话的第一步）**：

1. **任何对话先读 `<PROJECT_ROOT>/TASK_INDEX.md`**（项目任务全景索引；不存在则按新任务处理）。
2. 用户**不提任何已有任务** → 默认建立**新任务**。
3. 用户**首句提到**某个已有任务（任务编号或主题） → **询问**用户是否继续该任务。
4. 用户**明确表示继续旧任务（双次确认：首句提及 + 对询问的明确肯定）** → **不建立新任务**，读该任务 `task_current_state.md` 续接，并在新 CurrentState 中记录 `PRECEDING_TASK_REF`。**续接不改变任务数量，不另立索引区块**。
5. 续接与并行防护的完整协议见 `OPERATING_RULES.md` §2。

**任务定义**：

- 新建 Top-Level Session = 新建 Task；续接例外见上。
- 同一 Task 内的全部请求、追加、返工、验证和后续交付均属于同一 Task。
- 同一 Task 不因子目标变化、文件类型变化、跨午夜、上下文压缩、模型切换或调用子 Agent 而创建第二个 Task。
- 同一 Task 内允许存在多个 **Round**；Round 是一次“需求确认 → Plan → 施工 → 验收 → 关闭”的工作循环，不是新 Task。
- 若宿主不暴露稳定 Session ID，则将当前顶层用户上下文视为同一 Session，直到用户显式新开顶层会话或明确要求新建 Task。

---

## 2. 资产保护（永久约束）

### 2.1 Project Baseline：既有项目树默认原位保护

必须区分：

1. **Project Baseline / Canonical Project Assets**：项目本来就存在的源码、配置、测试、文档、模板、数据目录、构建文件等；
2. **Task-local Assets**：当前 Task 新增的输入、辅助脚本、中间产物、证据、生命周期账本和独立交付物。

以下内容默认在其 canonical path 原位保留：

- 会话开始前已属于项目结构的源码与模块；
- 既有 `src/`、`lib/`、`tests/`、`docs/`、`config/`、`assets/`、模板目录等；
- 版本控制元数据与项目配置；
- 依赖声明、锁文件、构建配置、CI 配置；
- README、LICENSE、设计文档；
- 隐藏配置目录和宿主专用目录；
- 用户明确声明为共享或长期项目资产的文件。

**修改既有源码时，应在原 canonical path 上做最小必要修改，不得为了目录整洁把它复制/搬进 Task 目录。**

### 2.2 `tasks/` 内目录的真实职责

- `01_inputs/`：当前 Task 的新增原始输入；只读保护。
- `02_src/`：仅当前 Task 专用且不属于既有项目 canonical tree 的辅助脚本/管线。
- `03_temp/`：可重建中间产物、缓存、预览和调试文件。
- `04_evidence/`：日志、diff、OCR 原始结果、验证截图、测试与校验证据。
- `05_docs/`：生命周期账本与按需 Case。
- `06_outputs/`：独立可交付产物、导出包、报告、生成文档等。

如果某个新文件实际属于项目正式源码结构，应按 Approved Plan 写入项目 canonical path，而不是为了满足模板强塞进 `02_src/`。文件保护与清理的执行细节见 `OPERATING_RULES.md` §4。

---

## 3. 生命周期文档与三本账纪律（永久约束）

### 3.1 默认启用

所有 Task 默认启用：

- `05_docs/plan.md`
- `05_docs/task_current_state.md`
- `05_docs/task_history.md`
- `05_docs/cases/`（目录存在，但不默认创建任何 Case 文件）

状态转换必须遵守 `TASK_STATE_MACHINE.md`。

### 3.2 Plan Gate（流程开关 + 风险时刻条款）

任何**实质施工**前，默认必须完整经过：

`用户提出需求 → Agent 确认理解 → 用户确认需求理解 → Plan 落盘 → 用户批准精确 Plan Revision → 才能施工`

用户确认“你理解对了”不等于批准 Plan。**用户批准不能由模型推定**：沉默、换话题、继续提供信息、仅确认需求理解，都不等于批准 Plan。

在需求确认与计划阶段，允许执行**只读调查和低风险验证**；不得提前执行会改变业务资产、项目行为或外部状态的施工。

**聊天免流程（流程开关）**：不对项目现状产生影响的纯聊天、咨询或讨论（包括工作流程中插入的闲聊），无需进入计划流程，也无需产生任何落盘（不分配 Round、不写 plan.md / task_current_state.md / task_history.md）。

### 3.3 CurrentState 纪律

`task_current_state.md` 是当前 Task 的**唯一当前状态真相**：

- 可全量覆盖；
- 只描述当前实际状态；
- 不承担不可变历史职责；
- 必须与真实文件、验证结果、当前 Approved Plan 和未完成项一致。

### 3.4 History 纪律

`task_history.md` 是 **Append-Only** 的历史快照账本：

- 禁止回写；
- 禁止修改、删除、重排已存在的历史记录；
- 每条 History 的 Snapshot Body 必须来自某一时点 `task_current_state.md` 的**完整原文转写**；
- 不得先总结 CurrentState 再冒充历史快照。

### 3.5 Cases 纪律

`05_docs/cases/` 永远存在，但 Case **只由用户显式指令触发**。

明确触发示例：复盘、记录这个坑、做个 case、总结踩坑、沉淀问题。

**不得**因为出现 Bug、多次返工、任务结束或 Agent 自认为“值得记录”而自动创建 Case。

### 3.6 三本账读取纪律（Search First, Read Narrow）

`plan.md` 与 `task_history.md` 可能增长到数千乃至数万行。**禁止默认整文件读取。**

需要恢复上下文、查找旧 Plan、审批、历史状态或旧验收结果时：

1. **先完整读取 `task_current_state.md`**——获取 `ROUND_ID`、`ACTIVE_PLAN_REF`、`APPROVAL_REF`、`WORKFLOW_PHASE`、`SAFE_RESUME_POINT`、相关 Subject/ID。
2. 对 `plan.md` 使用内容搜索工具（grep、rg、宿主搜索或等效索引能力）：优先搜索精确 `PLAN_ID` / `PLAN_REF` / `PLAN_EVENT_ID`；其次搜索 `SEARCH:` 中的 `SUBJECT` / `STATUS` / `TAGS`。仅读取命中记录块及必要相邻块。
3. 对 `task_history.md` 同样先搜索：优先 `ENTRY_ID` / `ROUND_ID` / `PLAN_REF`；其次 `SEARCH:` 中的 `SUBJECT` / `REASON` / `STATUS`。只读取与当前判断直接相关的历史 Snapshot。
4. 宿主没有内容搜索工具时：优先宿主的文件索引、find-in-file、分块读取等；能限定行范围/块范围时必须限定；全量读取长期账本是**最后手段**，不是默认路径。

允许全读的例外：用户明确要求完整审计/全量复盘；索引损坏且多轮由窄到宽的搜索仍无法定位；正在修复账本自身结构完整性；文件本身刚初始化、规模很小。

`SCHEMA.md`、`TASK_STATE_MACHINE.md`、`OPERATING_RULES.md` 较长时，同样优先按标题、Schema 名、状态名、字段名、Event 类型搜索定位后局部读取。

### 3.7 账本完整性

- `04_evidence/` 默认保留。
- `task_history.md` **永不自动删除、截断或回写**。
- 已交付独立产物不得无依据覆盖旧版本。
- 无法确认来源或用途的文件不自动删除。

---

## 4. 目录结构（总纲）

```text
<PROJECT_ROOT>/
├── AGENTS.md               ← 本文件（宪法层）
├── OPERATING_RULES.md      ← 触发纪律层
├── TASK_STATE_MACHINE.md   ← 机制层
├── SCHEMA.md               ← 契约层
├── TASK_INDEX.md           ← 项目任务全景索引（投影式，各任务维护自己的区块）
├── FILE_INDEX.md           ← 文件归属登记（append-only 流水）
├── <既有项目 canonical assets ...>
└── tasks/
    └── <YYYYMMDD>/
        └── task<N>_<Description>/
            ├── 01_inputs/
            ├── 02_src/
            ├── 03_temp/
            ├── 04_evidence/
            ├── 05_docs/
            │   ├── plan.md
            │   ├── task_current_state.md
            │   ├── task_history.md
            │   └── cases/
            └── 06_outputs/
```

- `TASK_INDEX.md`：**投影式**（可覆盖），是项目内所有任务 current_state 的简略版；每个任务的 Agent 只在轮次结束时更新自己的区块；维护权细节见 `OPERATING_RULES.md` §3。
- `FILE_INDEX.md`：**append-only** 流水，登记散落文件的归属判定；快速判定与登记流程见 `OPERATING_RULES.md` §5。

---

## 5. 触发索引表

以下动作执行前，**必须**先读取 `OPERATING_RULES.md` 对应章节（本表是触发纪律的唯一入口，保证条件触发规则不会被遗忘）：

| WHEN（触发条件） | THEN（必读章节） |
|---|---|
| 新建任务 / 续接旧任务 | OPERATING_RULES §2（会话归属与续接协议、并行防护） |
| 任务创建 / 轮次结束 / 续接接管 | OPERATING_RULES §3（TASK_INDEX 索引维护权） |
| 修改或清理既有文件、处理原件 | OPERATING_RULES §4（文件保护与清理） |
| 发现散落文件 / 轮次关闭 | OPERATING_RULES §5（散落文件归属与登记、归属结算） |
| 派发子 Agent / 委派工作 | OPERATING_RULES §6（委派与协作） |
| 使用工具执行操作 | OPERATING_RULES §7（工具与执行原则） |
| 宣布交付完成 | OPERATING_RULES §8（完成门槛） |

---

## 6. 完成门槛（总纲）

宣布一次交付完成前至少确认：批准的计划修订、账本一致性、无未批准范围扩张、CurrentState 反映真实现状、必要验证真实执行。完整检查清单见 `OPERATING_RULES.md` §8。
