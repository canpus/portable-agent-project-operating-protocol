# Portable Agent Project Operating Protocol

**A set of plain-text files that keep your AI coding assistant (Agent) from losing memory, getting confused, or hallucinating on long-term projects.**

No software to install. No code to write. You just copy a few `.md` files to the right places, and your AI assistant automatically follows a "work discipline" that:

- ✅ Survives context compression and very long conversations — **history is never lost**
- ✅ Keeps **memory organized** as the project grows
- ✅ Stops the model from inventing files, rules, or "facts" that don't exist (anti-hallucination)
- ✅ Always knows **where the project stands and what to do next**
- ✅ Keeps project memory even when you **start a new conversation or switch AI tools**

> **中文版请见 [README.md](README.md)** · *Chinese version: [README.md](README.md)*

---

## Table of Contents

1. [What is this? (30 seconds)](#1-what-is-this-30-seconds)
2. [Problems it solves](#2-problems-it-solves)
3. [What's in this repository](#3-whats-in-this-repository)
4. [What you need](#4-what-you-need)
5. [Step 1 — Install the Global Constitution (GlobalRules)](#5-step-1--install-the-global-constitution-globalrules)
6. [Step 2 — Install the Project Discipline (ProjectRules)](#6-step-2--install-the-project-discipline-projectrules)
7. [Step 3 — Verify the installation](#7-step-3--verify-the-installation)
8. [How it works](#8-how-it-works)
9. [FAQ](#9-faq)
10. [License](#10-license)
11. [Appendix: path verification](#11-appendix-path-verification)

---

## 1. What is this? (30 seconds)

It is **two sets of rule files + a self-running bookkeeping system**:

| Part | What it is | Analogy |
|------|-----------|---------|
| `GlobalRules/AGENTS.md` | **Global Constitution**: ground rules your AI must follow in *every* project (no lying, no inventing facts, protect your files, don't touch system settings…) | "Family rules" at home |
| `ProjectRules/` (3 files) | **Project Discipline**: workflow rules that apply inside *one specific project* (write a plan before working, keep state, keep history…) | "Class rules" for one class |
| Self-running bookkeeping | The AI automatically creates a `_agent_tasks/` directory in your project and keeps three ledgers: plan, current state, and history snapshots | The class "duty log" |

You put the rule files where your AI tool looks for them → the AI reads them at the start of every session → it keeps the ledgers while working → at any moment, opening the "current state" file tells you exactly where things stand.

> This repository itself was produced using these very rules: plans were written and approved before any work, the README was reviewed before release, and every step kept evidence. Curious? Look at the `task1_GitHub_Publish/` folder in this repository's root — it's the real ledger of this project's own creation (a snapshot at release time; the author's local workspace ledger keeps evolving). Once you deploy these rules, your own project will grow the same kind of ledgers.

---

## 2. Problems it solves

Using an AI assistant on a medium-sized project (a multi-file program, a batch of reports, a long-lived document), you'll hit five classic problems:

| # | Problem | Why it happens | How this protocol solves it |
|---|---------|---------------|----------------------------|
| 1 | **The AI "forgets" in long conversations** | Context gets compressed; early agreements, fields, and naming get crushed | All important information was already written to the on-disk "current state" file — compression can't delete it |
| 2 | **History becomes confusing** | The longer the context, the harder it is to tell "what was said before" from "what is decided now" | The plan ledger is append-only; the full decision trail stays inspectable |
| 3 | **Hallucination** | When the model can't remember, it "reasonably invents" files, rules, and conclusions | The constitution explicitly forbids fabrication; anything unverified must be labeled as unverified |
| 4 | **Current state lost mid-task** | Interrupted halfway, the AI doesn't know what's done and what's next | Every step leaves a trace in the "current state" file; recovery is always possible |
| 5 | **New conversation = total amnesia** | A fresh window knows nothing about the project | A new conversation first reads the "current state" file and takes over seamlessly (the state machine has a dedicated recovery protocol) |

In one sentence: **move memory out of the model's head and into files on disk.** Models change and conversations close; files don't.

---

## 3. What's in this repository

```text
portable-agent-project-operating-protocol/
├── README.md                        ← This document (Chinese) / README_EN.md (English)
├── LICENSE                          ← MIT license
├── GlobalRules/
│   └── AGENTS.md                    ← Global Constitution (works across projects, machines, tools)
└── ProjectRules/
    ├── AGENTS.md                    ← Project Discipline (the workflow master)
    ├── TASK_STATE_MACHINE.md        ← State machine (when you can do what, when you must wait for approval)
    └── SCHEMA.md                    ← Data contract (how ledgers are written, how IDs work)
```

- `GlobalRules/AGENTS.md` — **install once, applies to all projects.** It's the "behavior constitution": no hallucination, protect your existing files, no unauthorized data sharing, no touching system settings…
- `ProjectRules/` (3 files) — **install once per project.** They define the full lifecycle of an "agent task": requirements confirmation → plan → your approval → implementation → acceptance → history, plus the exact format of the three ledgers.

> Note: the rule files themselves are written in Chinese. That's fine — AI assistants understand Chinese rules no matter what language you chat in. You may translate them, but keeping the originals avoids translation drift in the rules that govern your work.

---

## 4. What you need

1. **A computer** (Windows / macOS / Linux)
2. **An AI coding assistant** (below called a "Harness" — an AI tool that can read and write files in your project, e.g., OpenAI Codex, Claude Code, Cursor, ZCode, GitHub Copilot, Windsurf)
3. **A project folder** (the folder containing the work you want the AI to help with)
4. **The ability to create folders and copy-paste files** — that's all

> Don't know what "username" means? On Windows, open File Explorer and go to `C:\Users\` — the folder named after you (e.g. `Xiaoming`) is your user directory. Throughout this document we **assume your PC username is `Xiaoming`**; replace `Xiaoming` with your own name everywhere.

---

## 5. Step 1 — Install the Global Constitution (GlobalRules)

**What this does:** put `GlobalRules/AGENTS.md` in your AI tool's "global rules" location. After that, the tool follows the constitution in *every* project.

**Why it's per-tool:** different tools look for global rules in different locations and with different filenames. Instructions below are per tool — **only read the section for the tool(s) you use.**

### 5.1 Generic steps (same for every tool)

1. Get `GlobalRules/AGENTS.md` (from the repository source, or from the `GlobalRules` folder after extracting the release zip)
2. Create the target folder listed below for your tool (create it if missing), and **copy the file there**
3. Rename the file if required (some tools want `AGENTS.md`, some want `CLAUDE.md` — see below)
4. Restart / open a **new** conversation so the rules load

### 5.2 Per-tool installation paths

#### ① ZCode

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.zcode\AGENTS.md` | `AGENTS.md` (no rename) |
| macOS | `/Users/Xiaoming/.zcode/AGENTS.md` | `AGENTS.md` (no rename) |
| Linux | `/home/xiaoming/.zcode/AGENTS.md` | `AGENTS.md` (no rename) |

- Create the `.zcode` folder if it doesn't exist.
- After this, every ZCode session automatically injects the constitution.

#### ② OpenAI Codex (CLI)

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.codex\AGENTS.md` | `AGENTS.md` (no rename) |
| macOS | `/Users/Xiaoming/.codex/AGENTS.md` | `AGENTS.md` (no rename) |
| Linux | `/home/xiaoming/.codex/AGENTS.md` | `AGENTS.md` (no rename) |

- Tip: Codex also checks for `C:\Users\Xiaoming\.codex\AGENTS.override.md` first (only one of the two is used, whichever exists). If you already have an override file, put the constitution content there instead — same effect.
- Do **not** put the file inside a project-local `.codex` folder — Codex only reads `~/.codex` and the project-root `AGENTS.md`.

#### ③ Claude Code

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.claude\CLAUDE.md` | **Rename `AGENTS.md` to `CLAUDE.md` first** |
| macOS | `/Users/Xiaoming/.claude/CLAUDE.md` | same |
| Linux | `/home/xiaoming/.claude/CLAUDE.md` | same |

1. **Rename** `GlobalRules/AGENTS.md` to `CLAUDE.md` (copy it first if you want to keep the original name too).
2. Put the renamed file into `C:\Users\Xiaoming\.claude\` (create the `.claude` folder if missing).
3. Claude Code then loads it in every project.
- Note: Claude Code officially suggests keeping each `CLAUDE.md` under 200 lines for context efficiency. This constitution is ~590 lines; Claude Code loads it **in full** (officially no truncation), it just consumes context. If context is tight, move the core chapters to the global file and the rest to project-level rules (see FAQ "File too long").

#### ④ Cursor

Recommended: use the settings UI (most reliable, cloud-synced, survives machine changes):

1. Open Cursor → Settings → `Customize` → `Rules`
2. Find **User Rules**, paste the **entire content** of `GlobalRules/AGENTS.md` there
3. Save. Applies to all projects.

If you prefer a file (optional — officially documented, but some versions have unreliable auto-loading per community reports):

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.cursor\rules\global.mdc` | extension must be `.mdc` |
| macOS | `/Users/Xiaoming/.cursor/rules/global.mdc` | same |
| Linux | `/home/xiaoming/.cursor/rules/global.mdc` | same |

> Safest: use Settings → Rules. The file approach is a fallback.

#### ⑤ GitHub Copilot (VS Code / CLI)

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.copilot\instructions\global.instructions.md` | extension must be `.instructions.md` |
| macOS | `/Users/Xiaoming/.copilot/instructions/global.instructions.md` | same |
| Linux | `/home/xiaoming/.copilot/instructions/global.instructions.md` | same |

- Create the `.copilot\instructions` folders if missing.
- For the Copilot CLI, a single-file alternative also works: `C:\Users\Xiaoming\.copilot\copilot-instructions.md` (same full content).

#### ⑥ Windsurf

| OS | Path | Filename |
|----|------|----------|
| Windows | `C:\Users\Xiaoming\.codeium\windsurf\memories\global_rules.md` | filename is fixed: `global_rules.md` |
| macOS | `/Users/Xiaoming/.codeium/windsurf/memories/global_rules.md` | same |
| Linux | `/home/xiaoming/.codeium/windsurf/memories/global_rules.md` | same |

- Paste the **full content** of `GlobalRules/AGENTS.md` into `global_rules.md` (note: this file has a 6,000-character limit — if it doesn't fit, keep the core chapters).
- You can also edit global rules from the Customizations icon in the top-right of Windsurf's Cascade panel.

### 5.3 Quick-reference table (bookmark this page)

| Tool | Windows path | Filename | Verified |
|------|--------------|----------|----------|
| ZCode | `C:\Users\Xiaoming\.zcode\` | `AGENTS.md` | ✅ |
| Codex CLI | `C:\Users\Xiaoming\.codex\` | `AGENTS.md` | ✅ |
| Claude Code | `C:\Users\Xiaoming\.claude\` | rename to `CLAUDE.md` | ✅ |
| Cursor | Settings → Rules (recommended) or `C:\Users\Xiaoming\.cursor\rules\` | `.mdc` | ✅/⚠️ |
| GitHub Copilot | `C:\Users\Xiaoming\.copilot\instructions\` | `.instructions.md` | ✅ |
| Windsurf | `C:\Users\Xiaoming\.codeium\windsurf\memories\` | `global_rules.md` | ✅ |

On macOS replace `C:\Users\Xiaoming\` with `/Users/Xiaoming/`; on Linux with `/home/xiaoming/`. Everything else stays the same.

---

## 6. Step 2 — Install the Project Discipline (ProjectRules)

**What this does:** copy the **3 files** from `ProjectRules/` into the root of the project you want to manage. The AI then follows the "plan → your approval → implement → keep ledgers" workflow inside that project.

### 6.1 Steps

1. Copy **all 3 files** from `ProjectRules/` into your project root:
   - `AGENTS.md`
   - `TASK_STATE_MACHINE.md`
   - `SCHEMA.md`
2. **All three files must sit in the same folder, next to each other** (`AGENTS.md` references the other two by relative filename — separated files won't be found).
3. If your project root already has an `AGENTS.md` (e.g. team rules), don't overwrite it — merge the contents, or put the `ProjectRules` trio in a subfolder and add a one-line reference from the existing `AGENTS.md` (see FAQ "My project already has an AGENTS.md").
4. How each tool reads project-level rules (filenames differ from the global level):

| Tool | Project-level reading |
|------|----------------------|
| ZCode / Codex / Copilot / Cursor | `AGENTS.md` at the project root is auto-read (keep all three files as-is in the root) |
| Claude Code | `CLAUDE.md` at the project root is auto-read — **copy `AGENTS.md` and rename it `CLAUDE.md`** in the project root (keeping `AGENTS.md` too is fine) |
| Windsurf | root `AGENTS.md` is always active; content can also go into `.windsurf/rules/*.md` |

5. **You create nothing manually** — the first time the AI works in the project, it automatically creates the `_agent_tasks/` directory and the three ledgers, as the rules require. You only need to have placed the files correctly.

### 6.2 What you'll see on the first task

The AI will automatically create:

```text
your-project/
├── AGENTS.md                        ← placed by you
├── TASK_STATE_MACHINE.md            ← placed by you
├── SCHEMA.md                        ← placed by you
└── _agent_tasks/                    ← created automatically
    └── 20260819/
        └── task1_XXX/
            ├── 01_inputs/           ← input materials
            ├── 02_src/              ← helper scripts
            ├── 03_temp/             ← temporary artifacts
            ├── 04_evidence/         ← evidence
            ├── 05_docs/             ← the three ledgers live here!
            │   ├── plan.md
            │   ├── task_current_state.md
            │   ├── task_history.md
            │   └── cases/
            └── 06_outputs/          ← deliverables
```

Seeing this structure means the discipline is active. **`task_current_state.md` (current state) is the heart of it all** — open it any time to know exactly where the project stands.

---

## 7. Step 3 — Verify the installation

**Method:** open a **new** conversation with your AI tool (important: new session, so rules reload), and ask:

> "Which rule files did you load? Please list your global rules and project rules."

**How to judge:**

- ✅ **Working:** it names the locations and key concepts of the rules (e.g. "three ledgers", "plan.md", "state machine", "approve before implementing", "no fabricating facts"), and explains what they do.
- ❌ **Not working:** it looks blank and says "I received no rules." Then check:
  1. Is the path right (is the username spelled correctly)?
  2. Is the filename right (`CLAUDE.md` for Claude, `.instructions.md` for Copilot, `.mdc` for Cursor)?
  3. Is it a fresh conversation (old conversations don't reload rules)?
  4. Has the tool been restarted?

**One more test** (proves memory survival): give the AI a task, let it create `_agent_tasks/` and do a couple of steps, then **close the conversation, open a new one**, and ask:

> "What were we working on in the previous conversation? Where are we now?"

It should open `task_current_state.md` and accurately answer the task ID, current phase, and next step. That's "no memory loss across conversations", demonstrated live.

---

## 8. How it works

### 8.1 The three ledgers

| Ledger | File | Nature | Purpose |
|--------|------|--------|---------|
| Plan ledger | `05_docs/plan.md` | append-only, never rewritten | Records "what you asked → how the AI planned → what you approved"; the full decision trail |
| Current state | `05_docs/task_current_state.md` | overwritable, always reflects now | Answers "where are we, what's next"; the single source of truth for recovery |
| History snapshots | `05_docs/task_history.md` | append-only, never rewritten | Archives a complete copy of "current state" at each milestone — an immutable timeline |

### 8.2 The state machine (when you can do what)

`TASK_STATE_MACHINE.md` defines a task's lifecycle:

```text
requirements → plan → your approval → implementation → delivery → your acceptance → close
                    ↑                                    │
                    └───── not approved? revise ────────┘
```

Three key gates:

- **Plan Gate:** any substantial change requires an approved plan first. The AI cannot modify your code on a whim.
- **Approval comes only from you:** the AI may never interpret "you stayed silent" as "you approved."
- **Acceptance gate:** when work is done, the AI delivers and states what it verified; you accept — the AI can't sign off on its own work.

### 8.3 Recovery after a new conversation / new machine

1. The AI in a new conversation first reads `05_docs/task_current_state.md`
2. From it: task ID, current phase, progress, approved plan reference
3. For details, it searches `plan.md` / `task_history.md` by ID and reads only the relevant blocks
4. It resumes from the "safe resume point"

The same mechanism handles context compression: compression may lose the model's memory, but not the ledgers on disk.

### 8.4 How anti-hallucination is enforced

Hard requirements in the constitution include:

- Never claim to have read files you didn't read, or say "tests passed" without running them
- Inferences and assumptions must be labeled separately from confirmed facts
- Unverified information must be stated as "unverified", not packaged as conclusions
- Even user statements get "bounded skepticism": if cheap to verify, verify before believing

---

## 9. FAQ

**Q1: Do I need to install any software?**
No. Everything is plain-text `.md` files — copy and paste. No configuration changes to your AI tool (other than placing the rule files correctly).

**Q2: Will these rules mess with my code?**
No. The rules require: plan → your approval before modifying project files; read-only investigation only before approval; minimal modifications that preserve your existing content. All ledgers live in `_agent_tasks/`, separate from your project files.

**Q3: I use two tools (e.g. Codex + Claude Code). How many copies?**
Project level: one `AGENTS.md` in the project root works for both; for Claude Code, also copy it as `CLAUDE.md`. Global level: one copy per tool (per section 5.2). Having multiple copies of identical rules is harmless.

**Q4: The constitution is long (~590 lines). Will Claude Code fail to load it?**
Claude Code officially loads `CLAUDE.md` in full, no truncation; but it recommends under 200 lines per file to save context. If tight, keep only the core chapters (honesty, asset protection, data boundaries) in the global `CLAUDE.md` and move the rest to project-level rules.

**Q5: My project already has an AGENTS.md. Conflict?**
No conflict, but don't overwrite existing rules. Recommended: put the `ProjectRules` trio in a subfolder (e.g. `docs/agent-rules/`), then add one line at the end of the existing `AGENTS.md`: "See also the rules in `docs/agent-rules/`, which have equal effect." Most tools read rule files at any depth within a project.

**Q6: The default timezone is Asia/Shanghai. Can I change it?**
Yes. Open the project-root `AGENTS.md`, find line 6 "默认项目时区：Asia/Shanghai", and change it to your timezone. Takes effect in a new conversation.

**Q7: What about switching computers?**
Global constitution: re-place it per section 5.2 on the new machine. Project memory: copy the whole project folder (including `_agent_tasks/`) — the ledgers *are* the memory. On the new machine, the AI reads `task_current_state.md` and takes over seamlessly.

**Q8: If I update the rule files, do old ledgers break?**
No. Ledgers are append-only; rule files are editable; the two don't interfere. Changing rules affects future work only; history stays intact.

**Q9: The AI doesn't follow the rules. What now?**
Check placement and filenames (see section 7). If placed correctly and still ignored, prompt it directly: "Please follow the rules in AGENTS.md in the project root." Note that different tools have different rule-loading quirks (e.g. some Cursor versions are unreliable at loading user-level files) — if a tool persistently ignores rules, switch to that tool's officially recommended configuration (e.g. Cursor's settings UI).

**Q10: Which AI tools are supported?**
Verified: ZCode, OpenAI Codex, Claude Code, Cursor, GitHub Copilot, Windsurf. Since `AGENTS.md` is becoming a cross-tool standard (supported by 20+ tools), most modern AI coding tools work directly. For others, check their official docs for `AGENTS.md` / `CLAUDE.md` support.

---

## 10. License

[MIT License](LICENSE) © 2026 Canpu

Free to use, modify, distribute, and use commercially, with the copyright notice retained.

---

## 11. Appendix: path verification

**Verified on: 2026-08-19.** All installation paths were checked against official documentation / official source code (see the release notes and evidence for details):

- ✅ **VERIFIED (official):** all paths for ZCode, OpenAI Codex, Claude Code, GitHub Copilot, Windsurf; project-level paths for Cursor
- ⚠️ **PARTIAL (documented but community-reported flaky):** Cursor's user-level files `~/.cursor/rules/*.mdc` auto-loading (the settings-UI approach is recommended instead)

**Important:** AI tools evolve fast; rule-file paths may change between versions. If a path doesn't exist on your machine, defer to that tool's **official documentation**:

| Tool | Official docs |
|------|---------------|
| ZCode | ZCode client configuration guide (Settings) |
| OpenAI Codex | https://developers.openai.com/codex/guides/agents-md · github.com/openai/codex |
| Claude Code | https://code.claude.com/docs/en/memory |
| Cursor | https://cursor.com/docs/rules · https://cursor.com/help/customization/rules |
| GitHub Copilot | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide |
| Windsurf | https://docs.windsurf.com/windsurf/cascade/memories (redirects to docs.devin.ai) |
