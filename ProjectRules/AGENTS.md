# AGENTS.md — 通用项目级 Agent 工作纪律

**适用范围**：本文件所在目录及其项目树。  
**PROJECT_ROOT**：本 `AGENTS.md` 所在目录。  
**默认 TASKS_ROOT**：`<PROJECT_ROOT>/_agent_tasks/`。  
**默认项目时区**：`Asia/Shanghai`（UTC+8）；若项目已有明确时区约定，以项目约定为准。  
**定位**：本文件只定义项目级行为纪律、Task 边界、目录治理、资产保护、主/子 Agent 协作与权威文档指针。

> 本规则不假定特定模型、厂商、IDE、CLI、工具名称或上下文长度。实际宿主的系统规则、安全策略、权限边界与真实工具能力始终优先；不得假装不存在的能力可用。

---

## 0. 权威文件与职责分工

项目根目录长期有效的三份规范：

1. **`AGENTS.md`**
   - 定义：项目纪律、顶层会话与 Task 边界、目录与资产治理、主/子 Agent 从属关系。
2. **`TASK_STATE_MACHINE.md`**
   - 定义：需求确认、Plan、审批、施工、交付、验收、返工、重新规划、History 转写、Idle、Case 复盘等状态转换。
3. **`SCHEMA.md`**
   - 定义：`plan.md`、`task_current_state.md`、`task_history.md`、`cases/` 的字段、ID、格式、索引、证据和交叉引用。

**职责判定：**
- “什么时候写 / 什么时候必须等待用户 / 什么时候允许进入下一阶段” → `TASK_STATE_MACHINE.md`
- “写哪些字段 / ID 怎么分配 / 记录长什么样” → `SCHEMA.md`
- “文件放哪里 / 哪些不能动 / 谁负责治理” → `AGENTS.md`

三者直接冲突时，不得自行选择更方便的一方；停止冲突步骤并向用户说明。用户当前明确指令可以改变当前 Task 的后续要求，但不得回写或篡改已经形成的 Append-Only 记录。

### 0.1 权威文件必须按需实际读取

不得只凭模型记忆声称“遵循了”指针文件：

- 首次创建 Task 或即将发生生命周期状态转换时，如果对应规则不在当前上下文，先按状态名/标题定位并读取 `TASK_STATE_MACHINE.md` 的相关章节。
- 即将写入 `plan.md`、`task_current_state.md`、`task_history.md` 或 `cases/` 时，如果对应契约不在当前上下文，先按子 Schema 名、字段名或标题定位并读取 `SCHEMA.md` 的相关章节。
- `TASK_STATE_MACHINE.md` 与 `SCHEMA.md` 默认采用**搜索定位 + 局部读取**；除全局一致性审查外，不得为了省事整文件加载。
- 读取规则文件属于必要验证，不得以“模型大概记得”为由跳过。

---

## 1. 顶层 Session = Task

本规则中的 **Top-Level Session** 指由用户直接发起、承载当前项目工作的顶层 Agent 会话/执行上下文。不同宿主可称为 conversation、chat、session、thread、run 等。

**一个 Top-Level Session 唯一对应一个 Task。**

- 新建 Top-Level Session = 新建 Task。
- 同一 Session 内的全部请求、追加、返工、验证和后续交付均属于同一 Task。
- 同一 Session 不因子目标变化、文件类型变化、跨午夜、上下文压缩、模型切换或调用子 Agent 而创建第二个 Task。
- Task 一旦建立，其 Task 编号、Task 根路径与创建日期在整个 Session 生命周期内保持不变。
- 同一 Task 内允许存在多个 **Round**；Round 是一次“需求确认 → Plan → 施工 → 验收 → 关闭”的工作循环，不是新 Task。
- 若宿主不暴露稳定 Session ID，则将当前顶层用户上下文视为同一 Session，直到用户显式新开顶层会话或明确要求新建 Task。

---

## 2. Task Onboarding

当前 Top-Level Session 首次进入实际项目工作时，只执行一次 Onboarding：

1. 确定项目时区下的 `YYYYMMDD`。
2. 在 `<TASKS_ROOT>/<YYYYMMDD>/` 扫描已有 `task<N>_*`，分配下一个 Task 编号。
3. 创建：
   - `01_inputs/`
   - `02_src/`
   - `03_temp/`
   - `04_evidence/`
   - `05_docs/`
   - `05_docs/cases/`
   - `06_outputs/`
4. 默认初始化：
   - `05_docs/plan.md`
   - `05_docs/task_current_state.md`
   - `05_docs/task_history.md`
5. 初始化内容必须符合根目录 `SCHEMA.md`。
6. `cases/` 必须存在，但**不得默认创建任何 Case 文件**。
7. 后续整个 Session 持续复用当前 Task 路径。

### 2.1 PROJECT_ROOT 与 TASKS_ROOT

- `PROJECT_ROOT` 永远是本 `AGENTS.md` 所在目录，不写死绝对路径。
- 默认 `TASKS_ROOT = <PROJECT_ROOT>/_agent_tasks/`。
- 若用户或项目已有规范明确指定其他 Task 根目录，则使用明确指定值，并在 CurrentState 记录。
- 不得为了套模板搬迁整个现有项目。

---

## 3. Project Baseline：既有项目树默认原位保护

为了使本规则能直接放入任意代码库、文档项目或业务项目，必须区分：

1. **Project Baseline / Canonical Project Assets**：项目本来就存在的源码、配置、测试、文档、模板、数据目录、构建文件等；
2. **Task-local Assets**：当前 Task 新增的输入、辅助脚本、中间产物、证据、生命周期账本和独立交付物。

### 3.1 既有项目资产不因 Task 收纳而搬迁

以下内容默认在其 canonical path 原位保留：

- 会话开始前已属于项目结构的源码与模块；
- 既有 `src/`、`lib/`、`tests/`、`docs/`、`config/`、`assets/`、模板目录等；
- 版本控制元数据与项目配置；
- 依赖声明、锁文件、构建配置、CI 配置；
- README、LICENSE、设计文档；
- 隐藏配置目录和宿主专用目录；
- 用户明确声明为共享或长期项目资产的文件。

**修改既有源码时，应在原 canonical path 上做最小必要修改，不得为了目录整洁把它复制/搬进 `02_src/`。**

### 3.2 `02_src/` 的真实职责

`02_src/` 仅用于当前 Task 专用、原项目不存在的辅助工程资产，例如：

- 一次性或 Task 专用处理脚本；
- 数据转换管线；
- 临时验证程序；
- 与主项目源码解耦的生成器或迁移辅助脚本。

如果某个新文件实际属于项目正式源码结构，应按 Approved Plan 写入项目 canonical path，而不是为了满足模板强塞进 `02_src/`。

---

## 4. 默认生命周期文档

所有 Task 默认启用：

- `05_docs/plan.md`
- `05_docs/task_current_state.md`
- `05_docs/task_history.md`

状态转换必须遵守 `TASK_STATE_MACHINE.md`。

### 4.1 Plan Gate

任何**实质施工**前，默认必须完整经过：

`用户提出需求 → Agent 确认理解 → 用户确认需求理解 → Plan 落盘 → 用户批准精确 Plan Revision → 才能施工`

用户确认“你理解对了”不等于批准 Plan。

在需求确认与计划阶段，允许执行**只读调查和低风险验证**，例如查看文件、检索代码、读取配置、查询文档、运行不改变项目状态的诊断；不得提前执行会改变业务资产、项目行为或外部状态的施工。

不对项目现状产生影响的纯聊天、咨询或讨论（包括工作流程中插入的闲聊），无需进入计划流程，也无需产生任何落盘（不分配 Round、不写 plan.md / task_current_state.md / task_history.md）。

### 4.2 CurrentState

`task_current_state.md` 是当前 Task 的**唯一当前状态真相**：

- 可全量覆盖；
- 只描述当前实际状态；
- 不承担不可变历史职责；
- 必须与真实文件、验证结果、当前 Approved Plan 和未完成项一致。

### 4.3 History

`task_history.md` 是 **Append-Only** 的历史快照账本：

- 禁止回写；
- 禁止修改、删除、重排已存在的历史记录；
- 每条 History 的 Snapshot Body 必须来自某一时点 `task_current_state.md` 的**完整原文转写**；
- 不得先总结 CurrentState 再冒充历史快照。

### 4.4 Cases

`05_docs/cases/` 永远存在，但 Case **只由用户显式指令触发**。

明确触发示例：
- “复盘一下”
- “记录这个坑”
- “做个 case”
- “总结这次踩坑”
- “把这次问题沉淀下来”

不得因为出现 Bug、多次返工、任务结束或 Agent 自认为“值得记录”而自动创建 Case。

---

## 5. 长期账本检索纪律：Search First, Read Narrow

`plan.md` 与 `task_history.md` 可能增长到数千乃至数万行。**禁止默认整文件读取。**

### 5.1 强制读取顺序

需要恢复上下文、查找旧 Plan、审批、历史状态或旧验收结果时：

1. **先完整读取 `task_current_state.md`**
   - 它是受控大小的当前快照；
   - 获取 `ROUND_ID`、`ACTIVE_PLAN_REF`、`APPROVAL_REF`、`WORKFLOW_PHASE`、`SAFE_RESUME_POINT`、相关 Subject/ID。
2. 对 `plan.md` 使用内容搜索工具，例如 grep、rg、宿主提供的文本搜索或等效索引能力：
   - 优先搜索精确 `PLAN_ID` / `PLAN_REF` / `PLAN_EVENT_ID`；
   - 其次搜索 `SEARCH:` 中的 `SUBJECT` / `STATUS` / `TAGS`。
3. 仅读取命中记录块及必要相邻块。
4. 对 `task_history.md` 同样先搜索：
   - 优先 `ENTRY_ID` / `ROUND_ID` / `PLAN_REF`；
   - 其次 `SEARCH:` 中的 `SUBJECT` / `REASON` / `STATUS`。
5. 只读取与当前判断直接相关的历史 Snapshot。

### 5.2 无 grep/rg 工具时

若宿主没有内容搜索工具：

1. 优先使用宿主的文件索引、symbol search、find-in-file、分块读取或等效能力；
2. 能限定行范围/块范围时必须限定；
3. 只有无法以任何方式定位记录，且该历史确实是当前决策所必需时，才允许扩大读取范围；
4. 全量读取长期账本是最后手段，不是默认路径。

### 5.3 允许全读的例外

仅限：

- 用户明确要求完整审计 / 全量复盘；
- 索引损坏且多轮由窄到宽的搜索仍无法定位；
- 正在修复账本自身结构完整性；
- 文件本身刚初始化、规模很小且不存在上下文成本问题。

### 5.4 Schema / State Machine 检索

`SCHEMA.md` 与 `TASK_STATE_MACHINE.md` 较长时，同样优先按：

- 标题；
- Schema 名；
- 状态名；
- 字段名；
- Event 类型；

搜索定位后局部读取。只有全局一致性审查时才全量读取。

---

## 6. 主 Agent / 子 Agent 从属关系

本规则中的 **Subagent** 泛指主 Agent 派生、委派或并行启动的子 Agent、worker、delegate、tool-agent、peer-agent 等从属执行单元。

所有 Subagents 均从属于当前 Top-Level Session 对应的唯一 Task。

### 6.1 禁止独立建 Task

Subagent 不得：

- 创建新的日期目录；
- 创建新的 `task<N>_*`；
- 把自己的子问题解释为独立 Task；
- 自行改变当前 Task 的状态机阶段。

### 6.2 生命周期账本由主协调者串行治理

默认只有主 Agent / 主协调者可以：

- 分配正式 Round / Plan / Plan Event / History / Case ID；
- 向 `plan.md` 追加正式记录；
- 覆盖 `task_current_state.md`；
- 向 `task_history.md` 追加正式快照；
- 宣布状态机阶段转换。

Subagent 可在明确委派下提供候选内容、证据、代码和分析，但不得并发写生命周期账本造成竞态。

### 6.3 委派必须携带 Task 状态

调用 Subagent 时，主 Agent 必须明确提供：

- `PROJECT_ROOT`；
- 当前 Task 根路径；
- 允许读写的目录/文件范围；
- 当前 `ROUND_ID`；
- 当前 Approved Plan Ref（如存在）；
- 当前状态机阶段；
- 禁止超范围施工的约束。

不得假定 Subagent 已自动继承全部上下文或本文件内容。

---

## 7. Task 目录职责

```text
<PROJECT_ROOT>/
├── AGENTS.md
├── TASK_STATE_MACHINE.md
├── SCHEMA.md
├── <既有项目 canonical assets ...>
└── _agent_tasks/
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

- `01_inputs/`：当前 Task 的新增原始输入；只读保护。
- `02_src/`：仅当前 Task 专用且不属于既有项目 canonical tree 的辅助脚本/管线。
- `03_temp/`：可重建中间产物、缓存、预览和调试文件。
- `04_evidence/`：日志、diff、OCR 原始结果、验证截图、测试与校验证据。
- `05_docs/`：生命周期账本与按需 Case。
- `06_outputs/`：独立可交付产物、导出包、报告、生成文档等。

### 7.1 软件项目交付例外

若交付物本质上是**对既有项目源码/配置的修改**，不得为了形式要求复制一份到 `06_outputs/`。

此时：

- canonical project files 本身是实施结果；
- `06_outputs/` 可为空；
- CurrentState 必须记录实际修改路径、验证结果和版本控制状态；
- 如有构建包、报告、导出文件等独立产物，再放入 `06_outputs/`。

---

## 8. 新增输入与散落文件的正向归属

禁止采用“非白名单 = 当前 Task 文件”的反向判断。

只有满足至少一项证据时，才能把散落文件归入当前 Task：

- 用户在当前 Session 明确点名、引用或描述；
- 本 Session 开始后新增，且类型、文件名或内容与当前任务高度一致；
- 查看文件名、时间、内容或元数据后可高置信度确认归属。

若归属不明确：

1. 先低成本检查；
2. 仍无法确定则保持原位；
3. 不得为了“整洁”强行移动、删除或归档；
4. 不得因此阻塞无关工作。

---

## 9. 原始资产、覆盖与清理

### 9.1 原始输入

`01_inputs/` 中原始文件不得直接覆盖、污染或删除。需要转换或修改时保留原件，派生结果进入其他目录。

### 9.2 既有用户改动

修改受版本控制或已有项目文件前，应检查可观察的当前状态/diff。不得覆盖、还原、格式化或删除与当前 Approved Plan 无关的用户改动。

### 9.3 临时文件

`03_temp/` 不因 Task 结束自动获得删除授权。仅当文件同时满足：

1. 明确由当前 Task 生成；
2. 可可靠重建；
3. 不承担证据或交付作用；
4. 删除不影响后续复查；

才可清理。

### 9.4 Evidence / History / Outputs

- `04_evidence/` 默认保留。
- `task_history.md` 永不自动删除、截断或回写。
- 已交付独立产物不得无依据覆盖旧版本。
- 无法确认来源或用途的文件不自动删除。

---

## 10. 工具与执行原则

本规则不规定具体工具名。Agent 应使用宿主当前真实可用的等效能力：

- 文件读取 / 目录浏览；
- 内容搜索；
- 精确编辑 / 写入；
- 命令执行 / 测试；
- 版本控制状态检查；
- 网页或官方文档检索；
- 图片/文档原生感知；
- 子 Agent 调度。

当工具能直接降低关键不确定性时，应实际使用；工具不可用时明确说明限制，不得把未验证结果写成已确认事实。

---

## 11. 完成门槛

宣布一次交付完成前至少检查：

- 当前 Top-Level Session 是否始终只有一个 Task；
- 当前 Round 是否使用用户批准的精确 Plan Revision；
- 是否存在未批准的范围扩张；
- `task_current_state.md` 是否反映真实现状；
- 应写入 History 的 CurrentState 是否已完整转写；
- `plan.md` / `task_history.md` 是否保持 Append-Only；
- 是否未经用户显式要求创建 Case；
- Subagent 是否误建 Task 或并发修改生命周期账本；
- 既有项目 canonical assets 是否被错误搬迁；
- 当前 Task 新增输入是否得到保护；
- 独立交付物是否位于 `06_outputs/`（若该任务确有独立交付物）；
- 软件/配置修改是否保留在正确 canonical path；
- 必要验证是否真实执行；
- 长账本读取是否遵守 Search First / Read Narrow。

状态转换细节以 `TASK_STATE_MACHINE.md` 为准。
