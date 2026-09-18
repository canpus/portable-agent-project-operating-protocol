# Portable Agent Project Operating Protocol v5.0.2

[English](README_EN.md) · [为什么要用状态机](docs/WHY.md) · [状态机怎样工作](docs/HOW.md) · [安装指南](docs/INSTALL.md) · [从旧版迁移](docs/MIGRATION.md) · [Windows 图文安装指南](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/guides/PAPOP-v5.0.2-strict-approval-windows-guide-zh.pdf) · [设计思路 #001](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/philosophy/01-让AI像人一样记忆.md)

PAPOP 是一套给 Agent 使用的工作规则和项目状态机。

这里的 **Agent**，就是能读取文件、修改内容、运行命令并连续完成任务的 AI；**Harness** 是承载 Agent 的工具，例如 Codex、Claude Code、OpenCode、ZCode 或 DeepSeek Harness。

普通聊天主要依靠当前对话里的上下文。对话变长、发生自动压缩、换模型或隔几天继续时，细节可能丢失。PAPOP 把最终目标、计划、用户决定、当前状态和历史证据写入项目文件，使 Agent 能从磁盘恢复，而不是猜测自己上次做到了哪里。

## **你需要做什么**

安装只做一次。日常使用时，你真正需要做的是下面这些事：

1. **开始项目时说清最终想得到什么。** Agent 会和你讨论需求。一个 Task 就是一个项目；同一项目换对话继续时，应当继续原来的 Task，不要重复创建。
2. **选择适合你的工作方式。** 想逐个把关就使用 Strict Approval；愿意把整个任务交给 Agent 就使用 Autonomous。模式会写进 Task，不能因为后来替换规则文件而静默改变。
3. **严格审批模式下，认真处理四个审查点。** 你需要依次确认需求、审批 `goal.md`、阅读并审批当前阶段的 `plan.md`、查看真实交付物后决定是否验收。不要只回复“继续”；要明确说哪里正确、哪里要改、是否批准当前版本。
4. **自主推进模式下，先说清授权边界。** Agent 可以在这个边界内连续工作，但关键决定、具体外部动作、不可逆操作、你设置的关卡以及最终目标变化，仍然会停下来等你决定。
5. **主动管理上下文。** 如果 Harness 能显示上下文占用，建议在大约一半时准备压缩；即使看不到占用，也建议在一个 Stage 完成并落盘后压缩。先让 Agent 保存检查点，并确认脚本输出 `CHECKPOINT_COMMITTED`，再手动压缩。不要等自动压缩先发生，因为尚未落盘的细节可能丢失。
6. **压缩、更换模型或换一次新对话后，先核对恢复结果。** Agent 必须重新读取 `goal.md` 和当前状态，并向你复述最终目标、当前阶段、已有批准、未完成事项和下一步。复述不对就立刻纠正，不要让它带着错误继续施工。
7. **验收时看实际产物和机器证据。** 测试、脚本和 diff 负责验证；Agent 不能靠一句“已经完成”证明结果正确。`AGENT_COMPLETION=COMPLETE` 只表示 Agent 做完了自己的部分，不等于你已经验收。
8. **随时给文件，但保留原件。** 你引用当前 Task 外的文件时，Agent 会把它复制到该 Task 的 `UserInput/`。工作区外的源文件只复制、不询问删除；工作区内但在 Task 外的源文件，复制并验证后才会询问你是否删除。
9. **自己备份整个 Task。** **`.agent-state/` 默认被 Git 忽略，PAPOP 不提供自动备份、同步或导出。备份或迁移时必须复制完整 Task 目录，并确认隐藏的 `.agent-state/` 也在其中。**

日常主流程如下。更完整的状态、账本和恢复说明见 [HOW.md](docs/HOW.md)。

![PAPOP v5 用户视角项目流转图](docs/diagrams/v5-user-workflow.png)

## 先选择一个发布包

PAPOP v5 提供三个 ZIP。只安装其中一个，不要把两种状态机同时放进同一工作区。

| 发布包 | 适合谁 | Agent 如何工作 |
|---|---|---|
| **GlobalRules Only** | 只想规范 Agent，不需要项目状态机 | 约束证据、权限、Git、`.gitignore`、`.venv`、依赖、代码修改、验证和外部动作 |
| **Strict Approval** | 希望重要阶段都由人确认 | 需求确认 → Goal 审批 → Stage Plan 审批 → 施工和验证 → Delivery 验收 |
| **Autonomous** | 愿意把整个 Task 委托给 Agent | 在授权范围内持续推进，遇到关键决定、具体授权或用户关卡时等待 |

Strict Approval 并不是每执行一个命令都问一次。用户批准的是需求、最终目标、阶段计划和阶段交付；已批准 Plan 内的普通施工步骤可以连续执行。

Autonomous 也不是“放任不管”。授权范围之外的动作仍然需要你的明确决定，Agent 完成和用户验收仍然是两件事。

## 五分钟安装思路

1. 从 Release 下载所需 ZIP，并完整解压。点号开头的目录可能被系统隐藏，不要漏掉 `.agent-rules/` 或 `.agent-protocol/`。
2. 把 `GlobalRules/` 的内容安装到 Harness 的用户级规则位置。
3. 如果选择状态机包，把 `ProjectRules/AGENTS.md` 和 `ProjectRules/.agent-protocol/` 放到工作区根目录；不要多套一层 `ProjectRules/`。
4. 如果已有自己的规则文件，先备份并合并，不要直接覆盖。
5. 开始一个全新 Session，让 Agent 说明它实际加载了哪些规则、当前工作区默认是哪种模式，并运行一次安装检查。

Codex、Claude Code、OpenCode、ZCode、DeepSeek Harness 在 Windows、Linux 和 macOS 上的具体位置与验证方法见 [安装指南](docs/INSTALL.md)。终端用户不需要另外安装 Python、Node 或 Mermaid；Windows 使用包内 CMD/PowerShell 工具，Linux 和 macOS 使用包内 POSIX Shell 工具。

Windows 用户也可以直接照带截图的分步教程走：[PAPOP v5.0.2 图文安装与使用指南](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/guides/PAPOP-v5.0.2-strict-approval-windows-guide-zh.pdf)。该指南对应 v5.0.2，只覆盖 Windows 与 Strict Approval 包，且只有中文版；其他平台与其他包仍以上面两个文件为准。

## 工作区长什么样

```text
<WORKSPACE_ROOT>/
├── AGENTS.md                         # 工作区状态机入口
├── .agent-protocol/                  # 规则、模板、跨平台脚本
├── .agent-work/                      # 事务与锁，默认忽略
├── .agent-cases/                     # 用户批准升格的工作区 Case
└── tasks/
    └── task1_YYYYMMDD_项目名/         # 一个 Task 就是一个项目
        ├── .agent-state/              # 账本目录，默认忽略
        │   ├── goal.md
        │   ├── plan.md
        │   ├── decisions.md
        │   ├── history.md
        │   ├── current_state.md
        │   ├── snapshots.md
        │   └── cases/
        ├── UserInput/                 # 外部输入的只读副本
        ├── .gitignore
        └── <项目文件和交付物>
```

Task、Session 和 Stage 不是一回事：

- **Task**：整个项目，可以跨很多次对话。
- **Session**：一次顶层对话、压缩后的恢复、模型更换或任务交接。
- **Stage**：一次可以单独计划、施工、交付和验收的工作周期。

## 六个账本各自做什么

| 文件 | 作用 | 写入方式 |
|---|---|---|
| `goal.md` | 保存项目最终目标及其修订历史 | 只追加；修改 Goal 必须追加新版本并明确告知用户 |
| `plan.md` | 保存每个 Stage 的方案、步骤和审批版本 | 只追加 |
| `decisions.md` | 保存用户明确作出的批准、拒绝、授权和改变 | 只追加；Agent 不能替用户补写决定 |
| `current_state.md` | 保存现在走到哪里、下一步是什么 | 唯一允许覆写的核心账本 |
| `snapshots.md` | 连续保存每次检查点的完整 Current State | 只追加；整个 Task 只有这一个 Snapshot 文件 |
| `history.md` | 历史检索入口，连接 Plan、Decision、Case、Input 和 Snapshot 行号 | 只追加，由 checkpoint 脚本生成 |

Case 位于 `.agent-state/cases/`。同一 Task 中，同一个已确认根因第三次发生时，Agent 必须提醒你，并建议把它记录成 Case。只有你同意后才创建；你还可以决定把通用 Case 升格到工作区或全局。

## 状态为什么不会只靠模型自觉

`checkpoint` 工具会先校验状态转移和引用，再原子覆写 `current_state.md`，把完整内容追加到单一 `snapshots.md`，计算精确起止行和哈希，最后向 `history.md` 追加索引并重新读取验证。

只有脚本输出 `CHECKPOINT_COMMITTED` 才算保存成功。只读检查必须输出 `TASK_STATE_VALID`。模型不能手工补写这三个生成账本，也不能把自己的复述当作验证结果。

## 进一步阅读

- [WHY：状态机解决什么问题，为什么值得使用](docs/WHY.md)
- [HOW：状态流转、用户参与点、账本、恢复、Case 与文件导入](docs/HOW.md)
- [INSTALL：五个 Harness 和三大操作系统的安装方法](docs/INSTALL.md)
- [MIGRATION：从旧版本迁移到 v5](docs/MIGRATION.md)
- [BEHAVIOR_CHECKS：安装后应该实际检查什么](docs/BEHAVIOR_CHECKS.md)
- [图文安装与使用指南：Windows 分步截图版（中文，对应 v5.0.2）](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/guides/PAPOP-v5.0.2-strict-approval-windows-guide-zh.pdf)
- [设计思路 #001：让 AI 像人一样记忆](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/philosophy/01-让AI像人一样记忆.md)（[English](https://github.com/canpus/portable-agent-project-operating-protocol/blob/main/docs/philosophy/01-Make-AI-Remember-Like-a-Human_EN.md)）
- [CHANGELOG：版本变化](CHANGELOG.md)

## 能做什么，不能保证什么

PAPOP 能减少上下文丢失、目标漂移、跳过审批、重复外部动作、历史难以查找和同类错误反复发生。它不能替代 Harness 的沙箱与权限系统，不能保证模型永不出错，也不能替你备份文件。

状态文件是恢复入口，不是不可质疑的事实。每次恢复仍要核对用户最新指令、实际文件、diff、测试和外部状态。

## License

[MIT License](LICENSE) © 2026 Canpu
