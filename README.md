# Portable Agent Project Operating Protocol

**便携 Agent 项目运行协议** —— 一套纯文本文件，让 AI 编程助手（Agent）在长期项目里不丢记忆、不犯迷糊、不乱编。

> 🌐 **English version**: [README_EN.md](README_EN.md) · *中文为主版，英文版为完整翻译*

不需要安装任何软件，不需要写一行代码。你只需要把几个 `.md` 文件复制到指定位置，你的 AI 助手就会自动遵守一套"工作纪律"，从此：

- ✅ 对话被压缩、上下文超长之后，**历史记忆不丢失**
- ✅ 项目越来越大、信息越来越多，**记忆不混乱**
- ✅ 模型不会凭想象编造项目里不存在的文件、规则和"事实"（防幻觉）
- ✅ 任何时候都知道**当前做到哪一步**，下一步该干什么
- ✅ 换一个新的对话窗口、甚至换一个 AI 工具，**项目记忆依然还在**

---

## 目录

1. [30 秒看懂：这是什么](#1-30-秒看懂这是什么)
2. [它解决了什么问题](#2-它解决了什么问题)
3. [仓库里有什么](#3-仓库里有什么)
4. [你需要准备什么](#4-你需要准备什么)
5. [部署第一步：安装"全局宪法"（GlobalRules）](#5-部署第一步安装全局宪法globalrules)
6. [部署第二步：安装"项目纪律"（ProjectRules）](#6-部署第二步安装项目纪律projectrules)
7. [部署第三步：验证装好了没有](#7-部署第三步验证装好了没有)
8. [工作机制：它到底是怎么做到的](#8-工作机制它到底是怎么做到的)
9. [常见问题 FAQ](#9-常见问题-faq)
10. [许可证](#10-许可证)
11. [附录：路径核验信息](#11-附录路径核验信息)

---

## 1. 30 秒看懂：这是什么

这是 **两套规则文件 + 一套自动运转的记账系统**：

| 部分 | 是什么 | 比喻 |
|------|--------|------|
| `GlobalRules/AGENTS.md` | **全局宪法**：无论你在哪个项目里，AI 都必须遵守的底线（不许撒谎、不许瞎编、保护你的文件、不乱改系统……） | 家里的"家规" |
| `ProjectRules/`（3 个文件） | **项目纪律**：只在某一个项目里生效的工作流程（每次干活前要写计划、记状态、留历史……） | 某个班级的"班规" |
| 自动运转的记账系统 | AI 按规则自动在你的项目里建 `_agent_tasks/` 目录，写三本账：计划账本、当前状态、历史快照 | 班级的"值日记录本" |

你把规则文件放到 AI 工具认得的位置 → AI 每次开会话自动读到规则 → 干活时自动记账 → 任何时刻翻开"当前状态"就能知道做到哪了。

> 这个仓库本身，就是用这套规则管理出来的项目：发布前先写计划、经你批准后才施工、README 经过审阅才推送、每一步验证都有存档。不信可以看看仓库根目录的 `task1_GitHub_Publish/` 文件夹——那是本项目诞生过程的真实账本（发布时点的快照，作者本地工作区的账本仍在持续更新）。你部署这套规则后，自己的项目里也会长出同样的账本。

---

## 2. 它解决了什么问题

用 AI 助手做中型项目（比如一个多文件的程序、一批报表、一份长期文档）时，你会遇到五个经典毛病：

| # | 痛点 | 为什么会发生 | 这套协议怎么解决 |
|---|------|--------------|------------------|
| 1 | **对话一长就"失忆"** | 上下文被压缩后，早期的约定、字段、命名全被揉碎 | 所有重要信息早就写进了磁盘上的"当前状态"文件，压缩也丢不了 |
| 2 | **历史记忆混乱** | 上下文越长，模型越分不清"过去说的"和"现在定的" | 计划账本只追加不改写，过去的决策链清晰可查 |
| 3 | **模型幻觉** | 模型记不清时会"合理编造"文件、规则、结论 | 宪法明文禁止捏造；凡是"没验证过"的信息必须标注为未验证 |
| 4 | **当前状态丢失** | 干到一半被打断，AI 不知道做到哪、下一步干嘛 | 每一步都在"当前状态"文件里留痕，随时可恢复 |
| 5 | **换对话就全忘了** | 新开一个窗口，AI 对项目一无所知 | 新对话先读"当前状态"文件即可无缝接管（状态机有专门的恢复协议） |

一句话：**把记忆从"模型的脑子里"搬进"磁盘上的文件里"**。模型会换、对话会关，文件不会。

---

## 3. 仓库里有什么

```text
portable-agent-project-operating-protocol/
├── README.md                        ← 你正在看的这个文件
├── LICENSE                          ← MIT 许可证
├── GlobalRules/
│   └── AGENTS.md                    ← 全局宪法（跨项目、跨机器、跨工具）
└── ProjectRules/
    ├── AGENTS.md                    ← 项目纪律（本项目工作流程总纲）
    ├── TASK_STATE_MACHINE.md        ← 状态机（什么时候能做什么、什么时候必须等你批准）
    └── SCHEMA.md                    ← 数据契约（账本怎么写、ID 怎么编）
```

- `GlobalRules/AGENTS.md` —— **放一次，所有项目生效**。它是"行为宪法"：禁止幻觉、保护你的已有文件、未经允许不外传数据、不碰系统设置……
- `ProjectRules/` 三个文件 —— **每个项目放一份**。它们定义了"一个 Agent 任务"的完整生命周期：需求确认 → 写计划 → 你批准 → 施工 → 验收 → 留历史，以及三本账（计划/状态/历史）的写法。

---

## 4. 你需要准备什么

1. **一台电脑**（Windows / macOS / Linux 都行）
2. **一个 AI 编程助手**（下面统称 Harness，就是"能读写你项目文件的 AI 工具"，比如 OpenAI Codex、Claude Code、Cursor、ZCode、GitHub Copilot、Windsurf 等）
3. **一个项目文件夹**（你想让 AI 帮忙干的活所在的文件夹）
4. **能新建文件/文件夹、能复制粘贴** —— 就这么多

> 看不懂"用户名"是什么意思？以 Windows 为例：打开文件资源管理器，进入 `C:\Users\` 文件夹，里面那个以你的名字命名的文件夹（比如 `Xiaoming`），就是你的用户名目录。下文统一**假设你的电脑用户名是 `Xiaoming`**，所有路径都按这个写，你只要把 `Xiaoming` 换成你自己的名字即可。

---

## 5. 部署第一步：安装"全局宪法"（GlobalRules）

**这一步做什么**：把 `GlobalRules/AGENTS.md` 这个文件，放到你的 AI 工具的"全局规则"位置。放好后，这个 AI 工具在**任何项目**里都会自动遵守宪法。

**为什么分工具讲**：不同 AI 工具读取全局规则的位置和文件名不一样。下面按工具逐个说明，你**只需要看你用的那个工具**那一节。

### 5.1 通用步骤（每个工具都一样）

1. 找到 `GlobalRules/AGENTS.md`（仓库源码里，或从 Release 压缩包解压后的 `GlobalRules` 文件夹里）
2. 按下方你所用工具的说明，**新建对应文件夹**（没有就新建，有就跳过），**把文件复制过去**
3. 文件名要改成对应工具要求的名字（有的工具要 `AGENTS.md`，有的要 `CLAUDE.md`，见下表）
4. 重启/新开一个 AI 对话，让规则生效

### 5.2 各工具的具体放置位置

> 表格里的路径已经按"用户名 Xiaoming"写全。macOS 和 Linux 的 `~` 就是用户主目录。

#### ① ZCode

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.zcode\AGENTS.md` | `AGENTS.md`（不用改） |
| macOS | `/Users/Xiaoming/.zcode/AGENTS.md` | `AGENTS.md`（不用改） |
| Linux | `/home/xiaoming/.zcode/AGENTS.md` | `AGENTS.md`（不用改） |

- 没有 `.zcode` 文件夹就新建一个。
- 放好后，ZCode 的**每一个**会话都会自动注入这份宪法。

#### ② OpenAI Codex（命令行版 codex）

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.codex\AGENTS.md` | `AGENTS.md`（不用改） |
| macOS | `/Users/Xiaoming/.codex/AGENTS.md` | `AGENTS.md`（不用改） |
| Linux | `/home/xiaoming/.codex/AGENTS.md` | `AGENTS.md`（不用改） |

- 小知识：Codex 还会优先读 `C:\Users\Xiaoming\.codex\AGENTS.override.md`（同一层二选一，谁存在读谁）。如果你已经有这个 override 文件，把宪法内容放进 override 文件即可，效果一样。
- 注意：**不要**把文件放进项目内部的 `.codex` 文件夹——官方只认用户目录 `~/.codex` 和项目根目录的 `AGENTS.md`。

#### ③ Claude Code

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.claude\CLAUDE.md` | **先把 `AGENTS.md` 重命名为 `CLAUDE.md`** |
| macOS | `/Users/Xiaoming/.claude/CLAUDE.md` | 同上 |
| Linux | `/home/xiaoming/.claude/CLAUDE.md` | 同上 |

- 第一步：把 `GlobalRules/AGENTS.md` **重命名**为 `CLAUDE.md`（复制一份再改名，原文件保留也没关系）。
- 第二步：把改好名的文件放进 `C:\Users\Xiaoming\.claude\`（没有 `.claude` 文件夹就新建）。
- 放好后，Claude Code 在**每个项目**里开会话时都会自动加载它。
- 提醒：Claude Code 官方建议每个 `CLAUDE.md` 控制在 200 行以内（加载效率友好）。这份宪法约 590 行，Claude Code 会**完整加载**（官方明确不会截断），只是会占一些上下文；如果你觉得上下文吃紧，可以只把宪法的核心章节放进全局，把其余内容作为项目级规则——见 FAQ「文件太长怎么办」。

#### ④ Cursor

推荐用**设置界面**（最稳、云同步、换电脑不丢）：

1. 打开 Cursor → 左下角设置（Settings）→ `Customize`（定制）→ `Rules`（规则）
2. 找到 **User Rules**（用户规则），把 `GlobalRules/AGENTS.md` 的**全部内容粘贴进去**
3. 保存即可，所有项目生效

如果你更想用文件的方式（可选，官方文档承认该路径，但社区反馈部分版本自动加载不稳定）：

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.cursor\rules\global.mdc` | 内容粘贴进去，扩展名必须是 `.mdc` |
| macOS | `/Users/Xiaoming/.cursor/rules/global.mdc` | 同上 |
| Linux | `/home/xiaoming/.cursor/rules/global.mdc` | 同上 |

> 稳妥做法：优先用"设置 → Rules"粘贴，文件方式作为备选。

#### ⑤ GitHub Copilot（VS Code / CLI）

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.copilot\instructions\global.instructions.md` | 扩展名必须是 `.instructions.md` |
| macOS | `/Users/Xiaoming/.copilot/instructions/global.instructions.md` | 同上 |
| Linux | `/home/xiaoming/.copilot/instructions/global.instructions.md` | 同上 |

- 没有 `.copilot\instructions` 文件夹就逐级新建。
- 如果你用的是 Copilot 命令行版（copilot CLI），还可以用单文件方式：`C:\Users\Xiaoming\.copilot\copilot-instructions.md`（内容同样整份粘贴）。

#### ⑥ Windsurf

| 系统 | 放置路径 | 文件名 |
|------|----------|--------|
| Windows | `C:\Users\Xiaoming\.codeium\windsurf\memories\global_rules.md` | 文件名固定为 `global_rules.md` |
| macOS | `/Users/Xiaoming/.codeium/windsurf/memories/global_rules.md` | 同上 |
| Linux | `/home/xiaoming/.codeium/windsurf/memories/global_rules.md` | 同上 |

- 把 `GlobalRules/AGENTS.md` 的内容**整份粘贴替换**进 `global_rules.md`（注意：该文件有 6000 字符上限，如果内容放不下，可以只保留宪法的核心章节）。
- 也可以在 Windsurf 的 Cascade 面板右上角 Customizations 图标里编辑全局规则。

### 5.3 全局规则速查表（把本页收藏，换工具时照着放）

| 工具 | Windows 放置路径 | 文件名要求 | 核验 |
|------|------------------|-----------|------|
| ZCode | `C:\Users\Xiaoming\.zcode\` | `AGENTS.md` | ✅ |
| Codex CLI | `C:\Users\Xiaoming\.codex\` | `AGENTS.md` | ✅ |
| Claude Code | `C:\Users\Xiaoming\.claude\` | 改名 `CLAUDE.md` | ✅ |
| Cursor | 设置 → Rules 粘贴（推荐）或 `C:\Users\Xiaoming\.cursor\rules\` | `.mdc` | ✅/⚠️ |
| GitHub Copilot | `C:\Users\Xiaoming\.copilot\instructions\` | `.instructions.md` | ✅ |
| Windsurf | `C:\Users\Xiaoming\.codeium\windsurf\memories\` | `global_rules.md` | ✅ |

macOS 把 `C:\Users\Xiaoming\` 换成 `/Users/Xiaoming/`，Linux 换成 `/home/xiaoming/`，其余相同。

---

## 6. 部署第二步：安装"项目纪律"（ProjectRules）

**这一步做什么**：把 `ProjectRules/` 里的 **3 个文件**复制到你**想管起来的项目**的根目录。放好后，AI 在你这个项目里干活时，就会自动遵守"写计划 → 你批准 → 施工 → 记账"这套流程。

### 6.1 步骤

1. 把 `ProjectRules/` 文件夹里的 **3 个文件全部复制**到你的项目根目录：
   - `AGENTS.md`
   - `TASK_STATE_MACHINE.md`
   - `SCHEMA.md`
2. **三个文件必须放在同一个文件夹里、互相挨着**（`AGENTS.md` 内部用相对文件名引用另外两个，分开就找不到了）。
3. 如果你的项目根目录已经有 `AGENTS.md`（比如公司/团队已有的规则），不要直接覆盖——把两边的 `AGENTS.md` 内容合并，或者把 `ProjectRules` 三件套放在项目的一个子文件夹里并在已有的 `AGENTS.md` 中加一句引用（具体见 FAQ「项目里已经有 AGENTS.md 怎么办」）。
4. 各工具对项目级文件的读取位置（和全局规则不同，项目级文件名有差异）：

| 工具 | 项目级读取方式 |
|------|---------------|
| ZCode / Codex / Copilot / Cursor | 项目根目录的 `AGENTS.md` 自动读取（三个文件照原样放根目录即可） |
| Claude Code | 项目根目录的 `CLAUDE.md` 自动读取——请把 `AGENTS.md` **复制一份改名为 `CLAUDE.md`** 放在项目根目录（`AGENTS.md` 也可以保留，不冲突） |
| Windsurf | 根目录 `AGENTS.md` 常驻生效；也可把内容放进 `.windsurf/rules/*.md` |

5. **什么都不用手动创建**——AI 第一次进入项目干活时，会自动按照规则创建 `_agent_tasks/` 目录和三本账。你只需要保证"放对了文件"，剩下的交给规则本身。

### 6.2 第一次干活时你会看到什么

AI 按规则开始第一次任务时，会自动：

```text
你的项目/
├── AGENTS.md                        ← 你放的
├── TASK_STATE_MACHINE.md            ← 你放的
├── SCHEMA.md                        ← 你放的
└── _agent_tasks/                    ← AI 自动创建的
    └── 20260819/
        └── task1_XXX/
            ├── 01_inputs/           ← 输入材料
            ├── 02_src/              ← 辅助脚本
            ├── 03_temp/             ← 临时产物
            ├── 04_evidence/         ← 证据
            ├── 05_docs/             ← 三本账在这里！
            │   ├── plan.md
            │   ├── task_current_state.md
            │   ├── task_history.md
            │   └── cases/
            └── 06_outputs/          ← 交付物
```

看到这个目录结构，说明纪律已经生效了。**`task_current_state.md`（当前状态）是整件事的核心**——任何时候打开它，你就知道项目做到哪一步了。

---

## 7. 部署第三步：验证装好了没有

**方法**：新开一个 AI 对话窗口（重要：一定要新开会话，让规则重新加载），然后问它：

> "你读到了哪些规则文件？请列出你加载的全局规则和项目规则。"

**判断标准**：

- ✅ **装好了**：它能说出你放的位置、规则里的关键概念（比如"三本账"、"plan.md"、"状态机"、"先批准再施工"、"不捏造事实"等），并且能准确说出这些规则的作用。
- ❌ **没生效**：它一脸茫然，说"我没有收到任何规则"。此时检查：
  1. 路径对不对（特别注意用户名是不是写成了 `Xiaoming` 之外的名字）？
  2. 文件名对不对（Claude 要 `CLAUDE.md`、Copilot 要 `.instructions.md`、Cursor 要 `.mdc`）？
  3. 是不是新开的对话（旧对话不会重新加载规则）？
  4. 工具是否重启过？

**再验一步**（验证防失忆）：给 AI 一个任务，让它按规则建好 `_agent_tasks/` 并干两步，然后**关掉对话，重新开一个**，问它：

> "我们上一个对话在做什么？现在进行到哪一步了？"

它应该能打开 `task_current_state.md`，准确回答出任务编号、当前阶段、下一步。这就是"换对话不丢记忆"的现场演示。

---

## 8. 工作机制：它到底是怎么做到的

### 8.1 三本账

| 账本 | 文件 | 性质 | 作用 |
|------|------|------|------|
| 计划账本 | `05_docs/plan.md` | 只追加，永不改写 | 记录"你要什么 → AI 怎么计划 → 你批准了什么"，决策链清晰可查 |
| 当前状态 | `05_docs/task_current_state.md` | 可覆盖，永远反映当下 | 回答"现在做到哪、下一步是什么"，是恢复上下文的唯一真相 |
| 历史快照 | `05_docs/task_history.md` | 只追加，永不改写 | 每个里程碑都把"当时的当前状态"完整存档，形成不可篡改的时间线 |

### 8.2 状态机（什么时候能做什么）

`TASK_STATE_MACHINE.md` 定义了一个任务的生命周期：

```text
需求确认 → 写计划 → 你批准 → 施工 → 交付 → 你验收 → 关闭
                ↑                      │
                └──── 不批准就改 ───────┘
```

关键的门槛有三个：

- **计划门（Plan Gate）**：任何实质性的修改，必须先有"你批准过的计划"。AI 不能自己拍脑袋就改你的代码。
- **批准只能来自你**：AI 永远不能把"你没说话"理解成"你批准了"。
- **验收门**：活干完，AI 交付并说明验证结果，由你验收，AI 不能替自己签字。

### 8.3 换对话/换电脑怎么恢复

1. 新对话的 AI 先读 `05_docs/task_current_state.md`
2. 从里面拿到：任务编号、当前阶段、进行到哪一步、批准过的计划编号
3. 需要看细节时，去 `plan.md` / `task_history.md` 按编号搜索局部读取（不整文件硬读）
4. 从"安全恢复点"继续干活

这套机制对"上下文被压缩"同样有效：压缩丢了模型记忆，但丢不了磁盘上的账本。

### 8.4 防幻觉是怎么落实的

宪法里对 AI 的硬性要求包括：

- 没读过的文件不许假装读过；没跑过的测试不许说"通过了"
- 推测、假设必须与"已确认事实"分开标注
- 未经核实的信息要明说"未核验"，而不是包装成结论
- 用户说的话也要"有限怀疑"：能低成本验证的，先验证再采信

---

## 9. 常见问题 FAQ

**Q1：需要安装任何软件吗？**
完全不用。全部是 `.md` 纯文本文件，复制粘贴即可。你现有的 AI 工具不用做任何配置（除了把规则文件放到正确位置）。

**Q2：这套规则会乱动我的代码吗？**
不会。规则要求 AI：修改项目文件前必须经过"计划 → 你批准"；未经批准只能做只读调查；已有文件必须最小修改、保护你的原有内容。账本全部写在 `_agent_tasks/` 里，和你的项目文件分开。

**Q3：我同时用两个工具（比如 Codex + Claude Code），要放几份？**
项目级：`AGENTS.md` 一份放在项目根目录即可，两个工具都认；Claude Code 再复制一份叫 `CLAUDE.md`。全局级：每个工具各放一份（按 5.2 节各自的路径）。规则内容是一样的，多放几份不影响。

**Q4：全局宪法太长（约 590 行），Claude Code 会不会加载不完？**
Claude Code 官方明确：`CLAUDE.md` 无论多长都会完整加载，不会截断；但官方建议每文件控制在 200 行以内以节省上下文。如果觉得吃紧，可以只把宪法的核心章节（认知诚实、资产保护、数据边界等）放进全局 `CLAUDE.md`，其余内容按需放进项目级规则。

**Q5：我的项目里已经有 `AGENTS.md` 了，会冲突吗？**
不冲突，但别直接覆盖别人的规则。推荐做法：把 `ProjectRules` 三件套放到项目根目录下一个子文件夹（比如 `docs/agent-rules/`），然后在已有的 `AGENTS.md` 末尾加一行引用："另见 `docs/agent-rules/` 中的规则，与本文件同等效力"。多数工具支持在项目内任意层级读取规则文件。

**Q6：默认时区是 Asia/Shanghai，我能改吗？**
能。打开项目根目录的 `AGENTS.md`，第 6 行写着"默认项目时区：Asia/Shanghai"，改成你所在时区即可（比如 `UTC+8` 换 `UTC-5` 之类）。改完新开会话生效。

**Q7：换电脑 / 换机器怎么办？**
全局宪法：按 5.2 节重新放置到新电脑的对应位置。项目记忆：把整个项目文件夹（含 `_agent_tasks/`）复制过去即可，账本文件本身就是记忆。新机器上 AI 读到 `task_current_state.md` 就能无缝接管。

**Q8：规则文件更新了（比如我改了 ProjectRules），旧账本会乱吗？**
不会。账本是"只追加"的，规则文件是"可修改"的，两者互不干扰。改规则只影响以后的干活方式，历史记录原样保留。

**Q9：AI 不遵守规则怎么办？**
先检查放置位置和文件名（见第 7 节验证方法）。如果确实放对了还不遵守，可以在对话里直接提示"请遵守项目根目录 AGENTS.md 中的规则"。另外注意：不同工具的规则加载机制不同（比如 Cursor 部分版本对用户级文件加载不稳定），如果某个工具始终不生效，换用该工具官方推荐的配置方式（如 Cursor 用设置界面粘贴）。

**Q10：这个框架支持哪些 AI 工具？**
已核验：ZCode、OpenAI Codex、Claude Code、Cursor、GitHub Copilot、Windsurf。由于 `AGENTS.md` 已成为跨工具的事实标准（20+ 工具支持），大部分现代 AI 编程工具都能直接用。其他工具请查阅其官方文档是否支持读取 `AGENTS.md` 或 `CLAUDE.md`。

---

## 10. 许可证

[MIT License](LICENSE) © 2026 Canpu

你可以自由使用、修改、分发、商用，只需保留版权声明。

---

## 11. 附录：路径核验信息

**核验日期：2026-08-19**。所有放置路径均经官方文档/官方源码核验（详见仓库发布说明与证据），其中：

- ✅ **VERIFIED（官方确认）**：ZCode、OpenAI Codex、Claude Code、GitHub Copilot、Windsurf 的全部路径；Cursor 的项目级路径
- ⚠️ **PARTIAL（官方承认但社区反馈不稳定）**：Cursor 用户级文件 `~/.cursor/rules/*.mdc` 的自动加载（建议使用设置界面方式）

**重要提示**：AI 工具迭代很快，规则文件路径可能随版本变化。安装时如果发现某个路径不存在，请以该工具的**官方文档**为准：

| 工具 | 官方文档链接 |
|------|-------------|
| ZCode | ZCode 客户端的配置指南（Settings → 插件与配置说明） |
| OpenAI Codex | https://developers.openai.com/codex/guides/agents-md · github.com/openai/codex |
| Claude Code | https://code.claude.com/docs/en/memory |
| Cursor | https://cursor.com/docs/rules · https://cursor.com/help/customization/rules |
| GitHub Copilot | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide |
| Windsurf | https://docs.windsurf.com/windsurf/cascade/memories（自动跳转 docs.devin.ai） |
