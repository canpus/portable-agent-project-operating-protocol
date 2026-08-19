# plan.md — 需求、方案与审批账本（Append-Only）

**SCHEMA_VERSION**: PLAN-2

本文件只追加，不回写。每条记录以 `====...====` + `SEARCH:` 行包裹，先搜索定位后局部读取。

================================================================================
SEARCH: RECORD=PLAN EVENT=PROPOSAL ROUND=R0001 PLAN=P-R0001-001 REV=1 ID=PE-R0001-001-001 SUBJECT=github-publish STATUS=AWAITING_APPROVAL TAGS=github,release,readme

PLAN_EVENT_ID: PE-R0001-001-001
SCHEMA_VERSION: PLAN-2
ROUND_ID: R0001
PLAN_ID: P-R0001-001
PLAN_REVISION: 1
PLAN_EVENT: PROPOSAL
PLAN_STATUS_AT_WRITE: AWAITING_APPROVAL
RECORDED_AT: 2026-08-19T19:13:59+08:00
RECORDER_AGENT: ZCode main agent
BASED_ON_STATE: CS-0002

AREA: publish
SUBJECT: github-publish
TAGS:
- github
- release
- readme

SUMMARY:
将 Portable_Agent_Project_Framework 发布为 GitHub 公开仓库 canpus/portable-agent-project-operating-protocol。
文件夹分层结构（GlobalRules/ + ProjectRules/）作为仓库源码；重建分层压缩包（解压后 = GlobalRules + ProjectRules 共 4 份文件）作为 GitHub Release 资产；新增面向零基础用户的 README.md 与 MIT LICENSE。
推送前 README 必须经用户审阅通过。

USER_CONFIRMED_REQUIREMENTS:
- U1 [USER_CONFIRMATION] 仓库名选定为 portable-agent-project-operating-protocol（AskUserQuestion 答案）
- U2 [USER_CONFIRMATION] 双发布：文件夹分层结构作为源码，压缩包作为 Release；压缩包解压后应为 GlobalRules + ProjectRules 共 4 份文件（AskUserQuestion 答案）
- U3 [USER_CONFIRMATION] LICENSE 采用 MIT（AskUserQuestion 答案）
- U4 [USER_STATEMENT] README 面向零基础用户，必须写清各 Harness 的规则文件放置位置，使用"假设用户名是 Xiaoming"式具体路径示例
- U5 [USER_STATEMENT] 用户审阅 README 通过之前不得推送 Git

GOAL:
把带状态机与文件管理纪律的便携 AGENTS 框架发布为 GitHub 公开仓库，任何人（含零基础用户）都能按 README 部署到自己的电脑。

IN_SCOPE:
- 在 F:\AgenticCoding\Portable_Agent_Project_Framework\ 目录执行 git init（main 分支），使其成为仓库工作树
- 撰写 README.md（仓库根，简体中文、小白向、具体路径示例）
- 生成 MIT LICENSE（版权行 Canpu，用户在审阅时确认）
- 重建分层压缩包（解压后 = GlobalRules/AGENTS.md + ProjectRules/ 三件套，共 4 份文件），放 06_outputs/
- 首次提交并推送至 canpus/portable-agent-project-operating-protocol（public）
- 创建 Release（含分层压缩包资产）
- 推送后验证仓库可见性、文件列表、Release 资产

OUT_OF_SCOPE:
- 修改 GlobalRules/ProjectRules 4 个规则文件的正文内容
- 创建 Case
- 把压缩包放入仓库源码树
- 覆盖或删除工作区根目录的原压缩包 Portable_Agent_Project_Framework.zip（保持原位不动）
- 在 GitHub 上发布除仓库与 Release 之外的任何内容（无 Issues 模板、无 Wiki 初始化等）

CONSTRAINTS:
- 推送前必须获得用户对 README 的明确审阅通过（用户审阅 = 推送门）
- 公开内容不得包含个人路径、真实邮箱、用户名泄露；提交 email 使用 GitHub noreply 地址
- 压缩包内容必须与仓库源码（GlobalRules + ProjectRules）哈希一致
- 各 Harness 规则文件路径结论必须经官方文档联网核验并记录核验日期；无法核验的明确标注
- 原始压缩包（平铺版）不被覆盖；新压缩包为任务产物

DELIVERABLES:
- GitHub 公开仓库 canpus/portable-agent-project-operating-protocol
- README.md（仓库根，canonical 文件）
- LICENSE（MIT，canonical 文件）
- Release v0.1.0 + 分层压缩包资产（06_outputs/portable-agent-project-operating-protocol-v0.1.0.zip）

PROJECT_FILES_EXPECTED:
- Portable_Agent_Project_Framework/README.md（新增）
- Portable_Agent_Project_Framework/LICENSE（新增）
- Portable_Agent_Project_Framework/GlobalRules/AGENTS.md（既有，原样提交）
- Portable_Agent_Project_Framework/ProjectRules/AGENTS.md（既有，原样提交）
- Portable_Agent_Project_Framework/ProjectRules/SCHEMA.md（既有，原样提交）
- Portable_Agent_Project_Framework/ProjectRules/TASK_STATE_MACHINE.md（既有，原样提交）

TASK_FILES_EXPECTED:
- 06_outputs/portable-agent-project-operating-protocol-v0.1.0.zip（重建的分层压缩包）
- 04_evidence/harness_paths_verification.md（各 Harness 路径核验证据）
- 04_evidence/ 推送与 Release 验证输出

IMPLEMENTATION_STEPS:
1. 联网核验各 Harness（Codex CLI / Claude Code / ZCode / Cursor / GitHub Copilot / Windsurf 等）的规则文件读取路径与文件名约定；加载 zcode-guide:zcode-configuration-guide 核验 ZCode 部分；证据存 04_evidence
2. 撰写 README.md（结构见 RECOMMENDATION 附注），写入仓库根
3. 撰写 MIT LICENSE
4. 重建分层压缩包：在临时目录组装 GlobalRules/ + ProjectRules/ 后打包，校验解压后文件哈希与源码一致
5. 在仓库目录 git init -b main；配置 repo-local 身份（name=Canpu, email=GitHub noreply）；确认工作树仅含预期文件
6. git add + commit（首次提交）
7. gh repo create canpus/portable-agent-project-operating-protocol --public --source . --push（仅 README 审阅通过后执行）
8. gh release create v0.1.0，附加 06_outputs 压缩包
9. 验证：gh repo view / git ls-remote / 下载 Release 资产并解压比对哈希

VALIDATION_PLAN:
- README 中每个 Harness 路径结论附核验来源与日期（官方文档优先）
- git status 确认工作树仅含预期文件，无 _agent_tasks 等无关内容
- 推送后 gh repo view + gh api repos/.../contents 检查文件列表
- Release 资产下载后解压，文件数与哈希与本地源码一致
- 原压缩包未被修改（哈希不变）

ACCEPTANCE_CRITERIA:
- 用户审阅 README 通过（小白可照做完成部署）
- 仓库公开可访问，文件列表 = README/LICENSE/GlobalRules/ProjectRules
- Release 资产为分层压缩包，解压后 4 份文件与源码哈希一致
- 无个人信息泄露（提交作者为 noreply 邮箱）

RISKS:
- Harness 配置路径随版本变化 → README 标注核验日期与"以官方文档为准"提示
- MIT 版权行姓名需用户确认 → 审阅时一并确认
- 首次发布后发现问题 → 仓库可改名/可删，传播范围有限，风险可控
- 原压缩包与重建压缩包同义命名可能混淆 → 新文件名带版本号区分

INVARIANTS:
- 4 个规则文件正文零修改
- plan.md / task_history.md 只追加
- 未经 README 审阅通过不执行步骤 7/8

SEPARATE_APPROVAL_REQUIRED:
- 创建 GitHub 公开仓库与首次推送（时机：用户审阅 README 通过后由用户明确授权）
- 创建 Release 与上传资产（与推送同批授权）
================================================================================

================================================================================
SEARCH: RECORD=PLAN EVENT=PROPOSAL ROUND=R0001 PLAN=P-R0001-001 REV=2 ID=PE-R0001-001-002 SUBJECT=github-publish+rule-add STATUS=AWAITING_APPROVAL TAGS=github,release,readme,rule

PLAN_EVENT_ID: PE-R0001-001-002
SCHEMA_VERSION: PLAN-2
ROUND_ID: R0001
PLAN_ID: P-R0001-001
PLAN_REVISION: 2
PLAN_EVENT: PROPOSAL
PLAN_STATUS_AT_WRITE: AWAITING_APPROVAL
RECORDED_AT: 2026-08-19T19:17:38+08:00
RECORDER_AGENT: ZCode main agent
BASED_ON_STATE: CS-0004
SUPERSEDES_REVISION: 1
CHANGES_FROM_PREVIOUS:
- 新增需求 U6/U7/U8：在 3 个 AGENTS.md 中添加"简单聊天免流程免落盘"规则
- 解除 rev1 INVARIANTS 中"4 个规则文件正文零修改"的 3 项（GlobalRules/AGENTS.md、ProjectRules/AGENTS.md、工作区根 AGENTS.md）
- SCHEMA.md 与 TASK_STATE_MACHINE.md 仍保持零修改
- 压缩包在规则添加后重建，哈希随之更新

AREA: publish
SUBJECT: github-publish+rule-add
TAGS:
- github
- release
- readme
- rule

SUMMARY:
在 rev1（发布 GitHub 公开仓库 canpus/portable-agent-project-operating-protocol，双发布，MIT，小白向 README）基础上，
新增一条规则修改：在 3 个 AGENTS.md（工作区根 F:\AgenticCoding\AGENTS.md、发布副本 ProjectRules/AGENTS.md、GlobalRules/AGENTS.md）中
各添加"不对项目现状产生影响的简单聊天无需进入计划流程或产生落盘"条款，然后按原计划发布（发布内容包含新规则）。

USER_CONFIRMED_REQUIREMENTS:
- U1 [USER_CONFIRMATION] 仓库名：portable-agent-project-operating-protocol
- U2 [USER_CONFIRMATION] 双发布：分层结构为源码 + 压缩包为 Release 资产（解压后 = GlobalRules + ProjectRules 共 4 份文件）
- U3 [USER_CONFIRMATION] LICENSE：MIT
- U4 [USER_STATEMENT] README 面向零基础用户，写清各 Harness 放置路径（占位用户名具体示例）
- U5 [USER_STATEMENT] 用户审阅 README 通过前不得推送
- U6 [USER_CONFIRMATION] 新规则目标文件 = 工作区纪律 F:\AgenticCoding\AGENTS.md（AskUserQuestion 答案）
- U7 [USER_CONFIRMATION] 新规则同步到发布副本 GlobalRules/AGENTS.md（AskUserQuestion 答案）
- U8 [MODEL_INFERENCE] 工作区根 AGENTS.md 与 ProjectRules/AGENTS.md 哈希一致（证据 04_evidence），为保持发布内容与本地纪律一致，ProjectRules/AGENTS.md 同步修改；此假设经用户批准 rev2 即视为确认

GOAL:
发布一个"任何人（含零基础用户）都能按 README 部署"的公开仓库；同时让纪律文件携带"简单聊天免流程免落盘"规则。

IN_SCOPE:
- 在 3 个 AGENTS.md 中各添加一条规则（最小修改：仅新增条款，其余正文不动）
- 在 F:\AgenticCoding\Portable_Agent_Project_Framework\ 目录 git init（main 分支），作为仓库工作树
- 撰写 README.md（仓库根，简体中文、小白向、具体路径示例）
- 生成 MIT LICENSE（版权行 Canpu，用户在审阅时确认）
- 重建分层压缩包（解压后 = GlobalRules/AGENTS.md + ProjectRules/ 三件套，共 4 份文件），放 06_outputs/
- 首次提交并推送至 canpus/portable-agent-project-operating-protocol（public）
- 创建 Release v0.1.0（含分层压缩包资产）
- 推送后验证仓库可见性、文件列表、Release 资产

OUT_OF_SCOPE:
- 修改 SCHEMA.md / TASK_STATE_MACHINE.md 正文
- 修改 .zcode 全局宪法 C:\Users\Canpu\.zcode\AGENTS.md（用户选定不加）
- 创建 Case
- 把压缩包放入仓库源码树
- 覆盖或删除工作区根目录的原压缩包 Portable_Agent_Project_Framework.zip（保持原位不动）
- 在 GitHub 上发布除仓库与 Release 之外的任何内容

CONSTRAINTS:
- 规则条款为最小新增：仅添加目标条款，不重排、不改写其他内容
- 修改后工作区根 AGENTS.md 与 ProjectRules/AGENTS.md 必须继续哈希一致
- 推送前必须获得用户对 README 的明确审阅通过
- 公开内容不得包含个人路径、真实邮箱；提交 email 使用 GitHub noreply 地址
- 压缩包内容必须与仓库源码哈希一致（含新规则后的版本）
- 各 Harness 规则文件路径结论必须经官方文档联网核验并记录核验日期
- 原始压缩包（平铺版）不被覆盖；新压缩包为任务产物

DELIVERABLES:
- GitHub 公开仓库 canpus/portable-agent-project-operating-protocol
- 3 个 AGENTS.md 各含一条新规则（canonical 修改）
- README.md（仓库根，canonical 文件）
- LICENSE（MIT，canonical 文件）
- Release v0.1.0 + 分层压缩包资产（06_outputs/portable-agent-project-operating-protocol-v0.1.0.zip）

PROJECT_FILES_EXPECTED:
- Portable_Agent_Project_Framework/README.md（新增）
- Portable_Agent_Project_Framework/LICENSE（新增）
- Portable_Agent_Project_Framework/GlobalRules/AGENTS.md（修改：加 1 条规则）
- Portable_Agent_Project_Framework/ProjectRules/AGENTS.md（修改：加 1 条规则）
- Portable_Agent_Project_Framework/ProjectRules/SCHEMA.md（原样提交）
- Portable_Agent_Project_Framework/ProjectRules/TASK_STATE_MACHINE.md（原样提交）
- AGENTS.md（工作区根，修改：加 1 条规则；与 ProjectRules/AGENTS.md 保持一致）

TASK_FILES_EXPECTED:
- 06_outputs/portable-agent-project-operating-protocol-v0.1.0.zip
- 04_evidence/harness_paths_verification.md
- 04_evidence/ 推送与 Release 验证输出

IMPLEMENTATION_STEPS:
0. 在 3 个 AGENTS.md 中添加"简单聊天免流程免落盘"条款（各文件措辞适配自身风格）；重新校验哈希（工作区根 = ProjectRules）并存档 04_evidence
1. 联网核验各 Harness 规则文件路径（Codex CLI / Claude Code / ZCode / Cursor / GitHub Copilot / Windsurf）；加载 zcode-guide:zcode-configuration-guide 核验 ZCode 部分；证据存 04_evidence
2. 撰写 README.md，写入仓库根
3. 撰写 MIT LICENSE
4. 重建分层压缩包（基于含新规则的 4 份文件），校验解压后哈希一致
5. 在仓库目录 git init -b main；配置 repo-local 身份（name=Canpu, email=GitHub noreply）；确认工作树仅含预期文件
6. git add + commit（首次提交）
7. gh repo create canpus/portable-agent-project-operating-protocol --public --source . --push（仅 README 审阅通过后执行）
8. gh release create v0.1.0，附加 06_outputs 压缩包
9. 验证：gh repo view / git ls-remote / 下载 Release 资产解压比对哈希

VALIDATION_PLAN:
- 规则添加后：工作区根 AGENTS.md 与 ProjectRules/AGENTS.md 哈希一致；GlobalRules/AGENTS.md 含新条款且其余正文未动（diff 检查）
- README 中每个 Harness 路径结论附核验来源与日期
- git status 确认工作树仅含预期文件
- 推送后 gh repo view + gh api repos/.../contents 检查文件列表
- Release 资产下载解压，文件数与哈希与本地源码一致
- 原压缩包未被修改（哈希不变）

ACCEPTANCE_CRITERIA:
- 新规则条款在 3 个目标文件中生效且措辞符合用户"大意"
- 用户审阅 README 通过（小白可照做完成部署）
- 仓库公开可访问，文件列表 = README/LICENSE/GlobalRules/ProjectRules
- Release 资产为分层压缩包，解压后 4 份文件与源码哈希一致
- 无个人信息泄露（提交作者为 noreply 邮箱）

RISKS:
- Harness 配置路径随版本变化 → README 标注核验日期与"以官方文档为准"提示
- 三处 AGENTS.md 需同步维护 → 哈希一致性校验兜底
- MIT 版权行姓名需用户确认 → 审阅时一并确认
- 首次发布后发现问题 → 仓库可改名/可删，传播范围有限
- 原压缩包与重建压缩包同义命名可能混淆 → 新文件名带版本号区分

INVARIANTS:
- 3 个 AGENTS.md 仅新增规则条款，其余正文零修改
- SCHEMA.md / TASK_STATE_MACHINE.md 正文零修改
- plan.md / task_history.md 只追加
- 未经 README 审阅通过不执行步骤 7/8

SEPARATE_APPROVAL_REQUIRED:
- 创建 GitHub 公开仓库与首次推送（时机：用户审阅 README 通过后由用户明确授权）
- 创建 Release 与上传资产（与推送同批授权）
================================================================================

================================================================================
SEARCH: RECORD=PLAN EVENT=REVIEW ROUND=R0001 PLAN=P-R0001-001 REV=2 ID=PE-R0001-001-003 SUBJECT=github-publish+rule-add STATUS=APPROVED TAGS=github,release,readme,rule

PLAN_EVENT_ID: PE-R0001-001-003
SCHEMA_VERSION: PLAN-2
ROUND_ID: R0001
PLAN_ID: P-R0001-001
PLAN_EVENT: REVIEW
TARGET_REVISION: 2
RECORDED_AT: 2026-08-19T19:19:11+08:00
RECORDER_AGENT: ZCode main agent
REVIEWED_BY: USER
REVIEW_RESULT: APPROVED

USER_FEEDBACK:
批准

APPROVED_PLAN_REF:
P-R0001-001@rev2

APPROVED_SCOPE:
仅限 rev2 明确范围。

APPROVAL_EXCLUSIONS:
- 创建公开仓库、推送与 Release（rev2 SEPARATE_APPROVAL_REQUIRED）：仍需用户审阅 README 通过后另行授权
================================================================================
