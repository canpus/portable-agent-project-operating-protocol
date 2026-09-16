# Portable Agent Project Operating Protocol

便携 Agent 项目运行协议（PAPOP） · **v4.0.0**

一套纯 Markdown 协议，为能读写文件、调用工具的 Agent 定义行为边界、执行授权、状态保存和压缩后的恢复方法。不需要数据库、后台服务或固定模型。

项目主页：[github.com/canpus/portable-agent-project-operating-protocol](https://github.com/canpus/portable-agent-project-operating-protocol)

**v4 提供三种分发包。计划审批和任务委托是并列的治理选择，共用状态与恢复机制。**

[English](README_EN.md) · [安装与日常使用](docs/INSTALL.md) · [迁移与切换](docs/MIGRATION.md) · [更新记录](CHANGELOG.md) · [行为验收场景](docs/BEHAVIOR_CHECKS.md)

## 选择一个包

| 压缩包 | 适合谁 | 默认行为 |
|---|---|---|
| `portable-agent-project-operating-protocol-v4.0.0-global-rules-only.zip` | 只想约束模型行为，不需要状态机 | 只有 GlobalRules，不创建本协议账本 |
| `portable-agent-project-operating-protocol-v4.0.0-plan-approval.zip` | 希望执行路线由人类先审阅、交付由人类验收 | 确认需求 → 批准精确计划 → 执行 → 人工验收 → 关闭 |
| `portable-agent-project-operating-protocol-v4.0.0-task-delegation.zip` | 希望委托目标后由 Agent 持续推进 | 在任务授权范围内执行，缺关键决定/具体授权或遇用户关卡时等待 |

三个包包含完全相同的 GlobalRules。两个状态机包各包含一个生成好的 `ProjectRules/AGENTS.md` 和相同的 `.agent-protocol/`，安装时只选择一个。普通问答和纯讨论不创建任务记录。

“计划审批”不是批准每条工具调用，也不默认要求每个计划步骤重新批准。获批计划内可以持续执行；需要更细控制时指定“调查完成后等我”“第二步前确认”等关卡。

## 快速安装

1. 解压所选 ZIP，将 `GlobalRules/AGENTS.md` 内容安装到宿主支持的全局规则位置。已有规则先备份、合并，保留宿主和组织要求。
2. GlobalRules Only 到此结束。不需要项目状态文件。
3. 两个状态机包：把 ZIP 内 **ProjectRules 的内容**复制到目标项目根，而不是多套一层 ProjectRules 目录：

```text
你的项目/
├── AGENTS.md
├── .agent-protocol/
└── 原来的源码、输入、文档和交付物……
```

4. 项目已有 AGENTS.md 时合并入口与稳定项目约束，不覆盖原规则。移除旧状态机的加载指针，保留历史原文和账本。
5. 确认隐藏的 `.agent-protocol/` 已复制且入口被宿主实际加载。规则只说明行为，不授予宿主没有的权限。

源码仓库的 `ProjectRules/AGENTS.template.md` 是构建模板，**不能直接安装**。包内的 AGENTS.md 已替换好模式配置。

## 两个独立维度

| 配置 | 可选值 | 控制什么 |
|---|---|---|
| GOVERNANCE_MODE | PLAN_APPROVAL / TASK_DELEGATION | 谁授权执行、何时等待、何时关闭 |
| RECORD_MODE | AUTO / TRACKED | 哪些实际任务记录状态 |

计划审批包固定采用 `PLAN_APPROVAL + TRACKED`：小任务也要有可审阅计划和批准记录。任务委托包默认 `TASK_DELEGATION + AUTO`：连续工作可完成、无正式计划/等待/恢复需要的小任务 FAST；多步骤计划、中间成果、等待、交接、未知外部动作或用户要求记录时升级 TRACKED，结束前不降级。

TASK_DELEGATION 可以由维护者改成 TRACKED，获得全部实际任务的记录。PLAN_APPROVAL 不能用 AUTO 绕过审批。模型不自行切换模式；活动任务的切换按 [迁移指南](docs/MIGRATION.md) 保存真实决定。

## 日常怎么用

计划审批模式：

> 修复登录刷新问题。请先调查并确认需求，再把计划落盘，等我批准后执行。

Agent 先做允许的调查、提交需求理解并等待。需求确认后提交精确计划修订；批准计划后执行，交付具体候选后等你验收。沉默、补充信息和确认理解不能代替计划批准；新修订不能继承旧修订的批准。

任务委托模式：

> 修复登录刷新问题，检查受影响行为，每个正式计划步骤完成后保存检查点。

Agent 在任务授权范围内持续推进；你仍可指定：

> 先把计划落盘，等我批准再修改文件。发布前另外等我确认。

这种任务关卡不会自动改变整个项目的治理模式。公开发布、购买、外发私有材料、生产或权限变更等仍检查具体授权；已有具体授权且范围未变时不重复询问。

## 共用状态与恢复

TRACKED 任务按里程碑保存，而不是每条命令都写账本：

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

- `current_state.md`：完整、短小、可更新的恢复入口；记录模式、活动/待批计划、授权、进度、验收、未知项和下一允许动作。
- `plan.md`：只追加自包含修订。写入提案不等于批准，也不自动激活待批修订。
- `decisions.md`：只追加真实用户决定；精确绑定计划修订、交付候选、外部动作或关卡。
- `history.md`：只追加里程碑增量与完整快照指针。
- `snapshots/`：提交时 current_state 的字节相同副本，不回写。
- `active.md` / `task_index.md`：短指针与追加式任务索引，不能扩大授权。

正式计划创建/修订/激活、每步验收完成、关键用户决定、交付待验收、等待/阻塞、外部动作前后、完成/取消时保存检查点。未达步骤验收条件只保存进展，不标完成。

### 准备压缩

> 我准备压缩上下文。请保存并核验 PRE_COMPACTION 检查点，保留治理模式、活动和待批计划、批准引用、用户关卡、交付候选和验收状态、成果证据、失败路线、未知外部动作及下一允许动作。保存后暂停，给出 current_state 路径。

模型不假装观察不可见 Token，不自行设定通用压缩阈值。保存不释放审批关卡，未完成任务不标 DONE。

### 压缩或换会话后恢复

> 读取 `<current_state 路径>`，按 recovery.md 核对计划、决定、最后事件及下一步依赖的实际文件后继续。保留原有关卡，不重新开始。

明确路径直接恢复，不双次确认。恢复先完整读 current_state，再按稳定 ID 搜索 plan/decisions/history 中的单个块，核对实际文件与外部结果；状态不能代替事实或扩大权限。待批计划和待人工验收仍保持等待。

外部动作结果未知先查询，不重复发送、购买、发布或部署。一个任务账本只有一个写入者；项目索引也需要串行治理，追加式文件不自动避免并发冲突。

## 源码结构与构建

```text
GlobalRules/AGENTS.md                  # 三个包共用
ProjectRules/AGENTS.template.md        # 生成两个项目入口
ProjectRules/.agent-protocol/          # 共用规则与契约
profiles/plan-approval.json            # 计划审批配置
profiles/task-delegation.json          # 任务委托配置
docs/                                 # 安装、迁移、验收场景
scripts/build_release.py              # 仅维护者构建使用
scripts/validate_release.py            # 源码和包结构核对
tests/                                # 分发包与数据约束检查
legacy/v1/                            # 原有旧规则存档
legacy/v3/                            # v3 活跃规则原文存档
```

维护者使用 Python 3 标准库，无需额外依赖：

```text
python scripts/build_release.py
python scripts/validate_release.py
python -m unittest discover -s tests -v
```

产物在 `dist/`：三个 ZIP、SHA256SUMS 和 release-manifest.json。构建白名单不包含历史账本、输入原件、Git 元数据或测试输出；包内包含安装说明、版本、许可和文件哈希清单。ZIP 时间戳固定以便可复现构建，不能拿 ZIP 元数据当实际任务时间。

## 验证与边界

先按 [安装说明](docs/INSTALL.md) 做只读规则加载检查，再用 [行为验收场景](docs/BEHAVIOR_CHECKS.md) 观察真实宿主中的表现。

维护者工具核对源文件引用、配置、模板、枚举、包内文件与源字节、哈希和核心状态约束。它们不执行 Agent，也不能证明所有模型长期遵循协议。规则不是物理权限系统；真实文件、网络、账号权限和审批由宿主控制。

v4 的记录格式与旧版不兼容。旧任务按 [迁移指南](docs/MIGRATION.md) 建立新状态，保留原记录；不能同时加载两套状态机管理同一任务。两种模式并列维护，不表示严格治理应被委托模式取代。

## 许可

[MIT](LICENSE)。
