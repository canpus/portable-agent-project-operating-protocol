# AGENTS.md — PAPOP v5 工作区状态机入口

PROTOCOL_VERSION: 5.0.1
WORKSPACE_GOVERNANCE_MODE: @@GOVERNANCE_MODE@@

## 0. 层级与身份

- 层级固定为：全局规则 → 工作区 → Task（Project）。本文件位于 `WORKSPACE_ROOT`，决定此工作区中新 Task 的默认治理模式。
- Task 就是 Project，目录为 `tasks/task<N>_YYYYMMDD_<任务名>/`；同一项目跨多次对话始终复用同一 Task。
- `TASK_ID` 在目录创建后不变；每次新对话/恢复分配 `SESSION_ID`；每个“计划—施工—交付—验收”周期分配 `STAGE_ID`。
- Task 创建时把工作区模式冻结到 `current_state.md`。修改本文件只影响新 Task；既有 Task 切换模式需要用户明确决定和迁移检查点。
- 纯讨论不自动创建 Task。用户确认开始项目，或第一个人工审查点即将发生时，创建/选择 Task。

## 1. 工作区与 Task 结构

```text
<WORKSPACE_ROOT>/
├── AGENTS.md
├── .agent-protocol/                 # 规则、模板、跨平台工具
├── .agent-work/                     # 临时事务与锁；默认忽略
│   ├── .txn/
│   └── locks/
├── .agent-cases/                    # 用户批准升格的工作区 Case
│   ├── index.md
│   └── WC-0001.md
├── tasks/
│   └── task1_YYYYMMDD_<任务名>/     # Task 即 Project
│       ├── .agent-state/            # 默认忽略
│       │   ├── goal.md              # append-only
│       │   ├── plan.md              # append-only
│       │   ├── decisions.md         # append-only
│       │   ├── history.md           # append-only，检索索引
│       │   ├── current_state.md      # 唯一可覆写的核心账本
│       │   ├── snapshots.md          # append-only，单文件增长
│       │   └── cases/
│       │       ├── index.md         # 短摘要与触发场景
│       │       └── C-0001.md        # 触发匹配时才读取
│       ├── UserInput/               # 独立文件导入流程产生的只读原件
│       ├── .gitignore
│       └── <项目文件>
└── .gitignore
```

- `.agent-state/` 只允许六个核心账本和 `cases/`；不得创建多快照目录、逐快照文件、`current_state.prev`、活动索引或项目级共享状态。
- 工作区 `.gitignore` 最小加入 `.agent-work/` 与 `tasks/*/.agent-state/`。Task 是独立 Git 仓库时，其 `.gitignore` 还必须加入 `.agent-state/`。不覆盖已有规则。
- `.agent-state/` 默认不受 Git 保护，不得记录秘密、凭据或不必要的敏感正文。

## 2. 规则路由

开始实际工作前读取：

1. `.agent-protocol/rules/lifecycle.md`
2. 当前 Task 冻结模式对应的一个文件：
   - `STRICT_APPROVAL` → `strict-approval.md`
   - `AUTONOMOUS` → `autonomous.md`
3. 写状态前读取 `checkpoint.md`；收到位于当前 Task 外的明确文件引用时读取 `intake.md`；处理重复错误时读取 `cases.md`；恢复/异常时读取 `recovery.md`。

字段、枚举和块格式以 `.agent-protocol/SCHEMA.md` 为准。全局 AGENTS 继续负责权限、环境、`.git`、实现、验证和外部动作纪律。

## 3. 阶段提交屏障

以下动作前必须运行平台对应的 checkpoint 工具，并取得 `CHECKPOINT_COMMITTED`：

- 宣称阶段、审查点、交付或返工已经完成；
- 请求需求确认、Goal 审批、Plan 审批或交付验收；
- 切换 Phase、Stage、Session，暂停、交接、压缩或结束任务；
- 开始下一阶段计划。

Windows 使用 `checkpoint.cmd`；Linux/macOS 使用 `sh checkpoint.sh`。模型不得直接写 `current_state.md`、`snapshots.md` 或 `history.md`，不得用自己的复述代替脚本验证。结构、哈希、行号、引用、状态转移和副本一致性由脚本、测试或 diff 验证；没有机器证据时写“未验证”。

## 4. History 检索

History 是项目历史入口。先 grep `KEYWORDS`、`SUBJECT`、`SUMMARY`，只读命中块，再沿 `PLAN_REFS`、`DECISION_REFS`、`CASE_REFS` 和 Snapshot 行号范围读取对应内容。History 回答“在哪里找”；Plan 回答“准备做什么”；Decision 回答“用户为什么授权/拒绝”；Snapshot 回答“当时实际状态与动作”；Case 回答“如何避免已知根因”。

## 5. Case 必读与升格

- 每个步骤开始和压缩恢复后，只读取 Global、Workspace、当前 Task 三层 Case index；仅在 `TRIGGERS` 匹配时读取详细 Case。
- 同一 Task 中，同一个已确认 `ROOT_CAUSE_KEY` 第三次发生且尚无 Case 时，脚本输出 `CASE_RECOMMENDATION_REQUIRED`。模型必须提醒并建议落盘；用户未同意不得创建。
- Task Case 使用 `C-NNNN`。用户可用 `CASE_ELEVATION_APPROVED` 将其复制升格为 Workspace `WC-NNNN` 或 Global `GC-NNNN`；原 Case 不移动、不删除，升格记录来源链与适用边界。

## 6. 独立文件处理

文件导入不属于状态机 Phase，不改变审批状态。用户随时明确引用文件/文件夹时：

- 已在当前 Task 内：原地使用；
- 在工作区内但不在当前 Task 内：复制并验证到 `UserInput/I-NNNN/`，提醒已复制并询问是否删除源；
- 不在工作区内：只复制并验证，提醒已复制，不询问删除；
- 没有活动 Task：不因此创建 Task，等待选择/创建 Task 后处理。

只处理用户明确提到的路径。状态目录、协议目录、`.git`、符号链接/junction 不自动复制。复制、哈希、tree diff 与删除前复核由 `intake` 脚本完成，模型不能自行宣称完整。

## 7. 完成与沟通

- `AGENT_COMPLETION=COMPLETE` 不等于用户验收；严格模式只有当前 Delivery 的 `DELIVERY_ACCEPTED` 才能关闭 Stage。
- 最终回复前运行只读 `verify`，并引用实际产物、测试/diff 和未验证项。
- 不提交、推送、打标签、删除源文件或执行其他高影响动作，除非用户已经明确授权对应对象和范围。
