# Portable Agent Project Operating Protocol

PAPOP · **v4.0.0**

A Markdown-only protocol for tool-using agents: behavior boundaries, execution authority, milestone checkpoints, and recovery after compaction or interruption. It requires no database, background service, or particular model.

Project home: [github.com/canpus/portable-agent-project-operating-protocol](https://github.com/canpus/portable-agent-project-operating-protocol)

**v4 has three distribution packages. Plan Approval and Task Delegation are peer governance choices sharing one state and recovery core.**

[中文](README.md) · [Installation and daily use](docs/INSTALL.md) · [Migration and switching](docs/MIGRATION.md) · [Changelog](CHANGELOG.md) · [Behavior checks](docs/BEHAVIOR_CHECKS.md)

## Choose one package

| ZIP | Intended use | Default behavior |
|---|---|---|
| `portable-agent-project-operating-protocol-v4.0.0-global-rules-only.zip` | Behavior constraints without a state machine | GlobalRules only; no PAPOP task ledger |
| `portable-agent-project-operating-protocol-v4.0.0-plan-approval.zip` | Human review of the execution plan and delivery | Confirm requirements → approve exact revision → execute → human acceptance → close |
| `portable-agent-project-operating-protocol-v4.0.0-task-delegation.zip` | Continuous execution after delegating a goal | Proceed within task authority; wait for missing decisions, specific authorization, or user-defined gates |

GlobalRules is byte-identical in all three packages. Each project package contains one generated `ProjectRules/AGENTS.md` and the same `.agent-protocol/` directory. Install only one project entry. Pure questions and discussions create no task records.

Plan Approval does not approve every tool call or every plan step separately. Execution within the approved plan continues; users can add finer gates, such as waiting after investigation or before the second step.

## Quick installation

1. Extract the selected ZIP. Install `GlobalRules/AGENTS.md` in the host's supported global-instruction mechanism. Back up and merge existing rules; preserve host and organizational requirements.
2. GlobalRules Only needs no project installation.
3. For either project package, copy the **contents of ProjectRules** into the target project root, including the hidden directory:

```text
your-project/
├── AGENTS.md
├── .agent-protocol/
└── existing source, inputs, documents, and deliverables…
```

4. Merge an existing project AGENTS.md rather than overwriting it. Remove old state-machine loading pointers while preserving original rules and ledgers.
5. Verify that the host actually loads the entry and that `.agent-protocol/` is present. Rules grant no physical permissions.

The repository's `ProjectRules/AGENTS.template.md` is a build template, **not an installable entry**. Package entries already contain the selected configuration.

## Two independent dimensions

| Configuration | Values | Responsibility |
|---|---|---|
| GOVERNANCE_MODE | PLAN_APPROVAL / TASK_DELEGATION | Execution authority, waiting gates, and closure |
| RECORD_MODE | AUTO / TRACKED | Which actual tasks persist state |

Plan Approval uses `PLAN_APPROVAL + TRACKED`, including small tasks. Task Delegation defaults to `TASK_DELEGATION + AUTO`: a short continuous task with no formal plan, waiting, handoff, recovery need, or user gate may use FAST. Formal multi-milestone plans, dependent intermediate results, waiting, uncertain external actions, or an explicit recording request upgrade the task to TRACKED until completion or cancellation.

Maintainers may set Task Delegation to TRACKED. Plan Approval cannot use AUTO to avoid approvals. Agents cannot change governance modes themselves; active tasks follow the [migration guide](docs/MIGRATION.md).

## Daily use

Plan Approval:

> Fix the login refresh issue. Investigate and confirm the requirements first, write the plan, and wait for my approval before implementation.

The agent waits for requirements confirmation, then approval of the exact plan revision, then human acceptance of a concrete delivery. Silence, extra information, or confirming understanding is not plan approval; a new revision cannot inherit approval of an old one.

Task Delegation:

> Fix the login refresh issue, check the affected behavior, and save a checkpoint after each formal plan step.

The agent proceeds within task authority. You can still specify:

> Write the plan and wait for my approval before modifying files. Ask separately before publishing.

Task-specific gates do not automatically change the project's governance mode. Publishing, purchasing, private-data transmission, production changes, permissions, and destructive actions still require specific authorization. Existing specific authorization is not requested again when its scope is unchanged.

## Shared state and recovery

TRACKED tasks persist milestone state rather than recording every command:

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

- current_state: complete but short recovery entry, including governance, active/proposed plans, authority, progress, acceptance, unknowns, and the next permitted action.
- plan: append-only, self-contained revisions. Writing a proposal neither approves nor activates it.
- decisions: append-only actual human decisions bound to exact revisions, delivery candidates, actions, or gates.
- history: append-only milestone changes and snapshot pointers.
- snapshots: byte-identical copies of committed current_state; never rewritten.
- active/task_index: short pointer and append-only index; neither grants authority.

Checkpoint on plan creation/revision/activation, each completed step, important human decisions, delivery awaiting acceptance, waiting/blocking, external intent/result, completion, or cancellation. A partially completed step is progress, not completion.

### Before compaction

> Save and verify a PRE_COMPACTION checkpoint. Preserve governance, active and proposed plans, approval references, user gates, delivery and acceptance status, evidence, rejected approaches, uncertain external actions, and the next permitted action. Pause afterwards and give me the current_state path.

The user or host controls compaction. Agents do not pretend to observe hidden token usage or invent universal thresholds. Saving does not release approval gates or complete unfinished work.

### Resume

> Read `<current_state path>`. Follow recovery.md to check plans, decisions, the last event, and the real files needed for the next action. Preserve existing gates and do not restart.

An explicit path needs no second confirmation. Read current_state fully, search stable IDs to read individual plan/decision/history blocks, and verify real files and remote results. Pending plan approval or acceptance remains pending after recovery.

Query uncertain external results before retrying. A task ledger has one writer; project-index allocation and appends also require serialization. Append-only files do not eliminate races.

## Source layout and builds

```text
GlobalRules/AGENTS.md                  # shared by all packages
ProjectRules/AGENTS.template.md        # generates both project entries
ProjectRules/.agent-protocol/          # shared rules and schema
profiles/plan-approval.json
profiles/task-delegation.json
docs/                                 # installation, migration, behavior checks
scripts/build_release.py
scripts/validate_release.py
tests/
legacy/v1/                            # existing older archive
legacy/v3/                            # preserved v3 active rules
```

Maintainer tools use Python 3's standard library only:

```text
python scripts/build_release.py
python scripts/validate_release.py
python -m unittest discover -s tests -v
```

`dist/` contains three ZIPs, SHA256SUMS, and release-manifest.json. A source whitelist excludes old ledgers, original inputs, Git metadata, and test outputs. Packages include installation guidance, version, license, and file hashes. ZIP timestamps are fixed for reproducibility, not evidence of real task timing.

## Verification and limits

Use the read-only installation check in [INSTALL](docs/INSTALL.md), then observe actual behavior using [BEHAVIOR_CHECKS](docs/BEHAVIOR_CHECKS.md). Detailed operational guides and executable rule text are in Chinese; this English overview describes the same modes and defaults.

Maintainer tools check references, profiles, templates, enumerations, archive contents and source bytes, hashes, and core data invariants. They do not run an agent or demonstrate long-term compliance by every model. Physical permissions and approvals remain controlled by the host.

v4 records are incompatible with older schemas. Preserve original evidence, create verified new state following [MIGRATION](docs/MIGRATION.md), and never let two active state machines manage the same task. Strict governance remains a supported choice rather than an obsolete version.

## License

[MIT](LICENSE).
