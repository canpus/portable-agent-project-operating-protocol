# How PAPOP v5 Works

[Back to README](../README.md) · [Why use a state machine](WHY_EN.md) · [Installation guide](INSTALL.md)

This document explains how the state machine moves a project forward, in what state the Agent works, what each file is responsible for, and what you should do at each review point.

## Five words to remember first

| Name | Plain-language explanation |
|---|---|
| Workspace | The workspace you hand to the Harness. The root contains the workspace `AGENTS.md`, `.agent-protocol/`, and `tasks/` |
| Task | One complete project. The directory name looks like `task1_20260917_rewrite-product-docs` |
| Session | One top-level conversation. A post-compaction recovery, a model change, or a handoff also starts a new Session, but does not create a new project |
| Stage | One cycle that can be planned, implemented, delivered, and accepted on its own. A long Task can have many Stages |
| Checkpoint | A state point already written and re-verified by the script, which can later be used for recovery |

The hierarchy is fixed:

```text
Global rules
└── Workspace rules and default governance mode
    └── Task (Project)
        ├── Session 1
        ├── Session 2
        └── Stage 1, Stage 2 ...
```

Global rules constrain the Agent's basic behavior in all projects. Workspace rules decide whether new Tasks default to Strict Approval or Autonomous. Once a Task is created, the mode is written into its own Current State; replacing the workspace `AGENTS.md` later does not silently change old Tasks.

## The complete main flow you see

[Open the full-size PNG](diagrams/v5-user-workflow.png) · [View the Mermaid source](diagrams/v5-user-workflow.mmd)

![PAPOP v5 user workflow](diagrams/v5-user-workflow.png)

When a new conversation starts, the Agent first decides whether this is a new project or a continuation of an existing Task. When an existing project continues, what is created is a Session, not a Task.

Recovery first runs the read-only `verify`, then reads `goal.md`, `current_state.md`, the three levels of Case indexes, and the most recent History, and checks them against the actual files, diffs, tests, and external state. The Agent then restates to you:

- the final Goal;
- the current Stage and Phase;
- the approvals or authorizations already obtained;
- the work that is not yet finished;
- what it plans to do next.

Only after you confirm that this restatement is correct does the Agent continue under the governance mode already frozen in the Task.

## The two governance modes

### Strict Approval

Strict mode has four mandatory human review points:

```text
Requirements discussion and clarification
→ [you confirm the Requirements]
→ Agent writes the Goal
→ [you approve the Goal]
→ Agent writes the current Stage Plan
→ [you approve the Plan]
→ Agent implements and runs machine verification
→ [you accept the Delivery]
→ Stage closed
→ next Stage Plan
```

When a review does not pass, the flow returns to the matching stage:

- Requirements are incorrect: the discussion continues;
- the Goal is worded incorrectly: append a new Goal Revision;
- the Plan is unacceptable: append a new Plan Revision;
- the Delivery is not acceptable: go into rework; if the rework would materially change the approved Plan, return to Plan approval first.

Approvals are bound to exact references. An approved Plan R1 does not mean Plan R2 is approved automatically; an accepted Delivery R1 also cannot close a Delivery R2 that was produced by rework.

### Autonomous

Autonomous mode works continuously after you explicitly authorize the whole Task. The Agent may organize the Goal, divide Stages, maintain the Plan, implement, and run verification on its own.

It must still pause in these situations:

- a key decision that would materially change the result is missing;
- a specific authorization is needed for an external action;
- the action has irreversible consequences;
- you have explicitly set a review or acceptance gate;
- the Agent is about to materially change the final Goal;
- the Harness itself requires a real permission approval.

If you did not ask for acceptance, the Stage may write `ACCEPTANCE_STATUS=NOT_REQUIRED`, but it must not be faked as `ACCEPTED`.

## What you should do at each point

| Point | What you need to check | Suggested reply |
|---|---|---|
| Choosing or creating a Task | Whether this is a new project or a continuation of an old one | "Continue `task2_...`" or "Create a new Task with strict approval mode" |
| Recovery confirmation | Whether the Goal, current stage, approvals, unfinished items, and next step are true | Point out the specific mistake; confirm explicitly when everything is correct |
| Requirements confirmation | Whether the in-scope items, out-of-scope items, constraints, deliverables, and acceptance criteria are complete | "Confirm REQ-0001" or list what to add or remove |
| Goal approval | Whether the final result in `goal.md` is exactly what you want and whether the boundary is clear | "Approve G-0001-R0001" or ask for an additional revision |
| Plan approval | What each step does, which scope it changes, how it is verified by machine, which external actions and user gates exist | Read the actual `plan.md`, then approve the exact `PLAN_REF`, or explain why you do not approve |
| Authorization requests during implementation | Whether the object, action, data, cost, impact, and reversibility are clear | Approve only the specific object and scope you understand |
| Delivery acceptance | Whether the actual files, interface, report, or other deliverables meet the Goal; whether the tests/diff really exist | "Accept DLV-..." or list the rework items; do not accept based only on the Agent's summary |
| Goal change | Whether this changes the project's final purpose rather than an ordinary implementation detail | If you agree, append a new Goal Revision; if not, continue with the original Goal |
| Case recommendation | Whether it really is the same root cause recurring, and whether recording it can prevent it from happening again | Agree or refuse to create it; when needed, decide separately whether to promote it |
| Before compaction | Whether the current state has already been saved through a checkpoint | Compact manually only after you see `CHECKPOINT_COMMITTED` |
| After compaction or a model change | Whether the Agent reread the Goal and restated the project correctly | Allow work to continue only when the restatement is correct |

## The Agent's own states and file record points

[Open the full-size PNG](diagrams/v5-agent-state-ledger-flow.png) · [View the Mermaid source](diagrams/v5-agent-state-ledger-flow.mmd)

![PAPOP v5 Agent state and ledger flow](diagrams/v5-agent-state-ledger-flow.png)

`current_state.md` does not store just one "state name". The following five groups of fields together determine what the Agent may do now:

| Field | The question it answers |
|---|---|
| `PHASE` | How far the workflow has come |
| `EXECUTION_STATUS` | Whether the current work is executing, waiting, blocked, complete, or cancelled |
| `AUTHORIZATION_STATUS` | Which kind of approval is being awaited, or what authorization has already been granted |
| `AGENT_COMPLETION` | Whether the Agent's own implementation is complete |
| `ACCEPTANCE_STATUS` | Whether you have already accepted the current Delivery |

For example, in the `AWAITING_DELIVERY_ACCEPTANCE` phase, `AGENT_COMPLETION` can be `COMPLETE` while `ACCEPTANCE_STATUS` is still `AWAITING`. This means the Agent has delivered, but the project has not yet received your acceptance.

### The main Phases in strict mode

```text
REQUIREMENTS_DISCUSSION
→ AWAITING_REQUIREMENTS_CONFIRMATION
→ GOAL_DRAFTING
→ AWAITING_GOAL_APPROVAL
→ PLAN_DRAFTING
→ AWAITING_PLAN_APPROVAL
→ IMPLEMENTATION
→ VERIFYING
→ AWAITING_DELIVERY_ACCEPTANCE
→ STAGE_CLOSED
```

A rejection or a failed verification moves into the matching discussion, drafting, or `REWORKING` state. When work cannot continue it moves to `BLOCKED`; when you cancel it moves to `CANCELLED`.

Autonomous mode uses the same Phase field, but after the Task is authorized it may skip strict mode's four fixed human wait points. Gates you set in addition still apply.

## The six core ledgers

All core ledgers live in the current Task's `.agent-state/`.

### `goal.md`: what the project must finally achieve

The Goal is formed after the initial requirements clarification and usually stays stable across many Stages. It contains the final result, the in-scope and out-of-scope items, the deliverables, the acceptance criteria, and the stable constraints.

The Goal can be changed, but it must not be overwritten silently. The Agent must first state clearly to you that this will change the project's final goal; after you agree, it appends a new Goal Revision and keeps the old version.

After every post-compaction recovery, model change, new Session, or task handoff, the Agent must reread `goal.md` and restate the final Goal to you.

### `plan.md`: how the current stage will be done

A Plan is bound to one Stage and one Goal Revision, and contains:

- what the current stage must deliver;
- the implementation steps;
- how each step is verified by a script, a test, or a diff;
- the scope that may be modified;
- the gates you set;
- the external actions that need separate authorization.

The Plan is append-only. When rework materially changes the approach, write a new Revision instead of modifying the old record that was already approved.

### `decisions.md`: what you actually decided

A Decision records only the approvals, rejections, authorizations, mode switches, Case creations, Goal changes, or task cancellations that you explicitly stated.

Silence, vague replies, and the Agent's own inferences must not be written as user Decisions. Every Decision is bound to an exact target, for example a specific `GOAL_REF`, `PLAN_REF`, or `DELIVERY_REF`.

### `current_state.md`: where things are now

This is the only core ledger that may be overwritten. It stays complete but as short as possible, and stores the current Session, Stage, Phase, active Goal/Plan, execution status, evidence, blockers, next action, and recent events.

The Agent does not write this file directly. Instead it produces a pending next-state, which the checkpoint script validates and replaces atomically.

### `snapshots.md`: the complete state of every checkpoint

A Task has only one `snapshots.md`, and it keeps growing. Every checkpoint appends the complete text of the committed `current_state.md` to the end.

A Snapshot is not a summary, and it is not split into many small files. The script calculates the start line, end line, byte count, and hash of each Snapshot block.

### `history.md`: the first place to look when searching history

History does not duplicate the whole body of the project history. It is a searchable index that records:

- keywords, subject, and summary;
- the Session, Stage, Phase, and event status at the time;
- Requirements, Goal, Plan, Decision, Case, and Input references;
- the exact start and end lines of the Snapshot in `snapshots.md`;
- the State and Snapshot hashes;
- what was done at the time, where the evidence is, and what the next step is.

## How History reassembles the past

When searching history, do not read the whole `snapshots.md` first. The order is:

1. search `history.md` for the subject, a keyword, an event number, or a status;
2. read only the matching History blocks;
3. look at their `PLAN_REFS`, `DECISION_REFS`, `CASE_REFS`, and `INPUT_REFS`;
4. read only the specific record blocks in the corresponding ledgers;
5. when the complete state at the time is needed, read the exact range from `SNAPSHOT_START_LINE` to `SNAPSHOT_END_LINE` in `snapshots.md`;
6. check against the hashes and the actual files instead of trusting old records blindly.

This answers: why the work was done at the time, how it was going to be done, which revision you approved, what happened, how it was verified, and why it was later redone.

## How Checkpoint prevents missing state

Every formal state boundary is committed through the checkpoint tool for the platform:

1. atomically take the current Task's lock;
2. before overwriting any ledger, validate the paths, fields, enumerations, identifiers, mode gates, references, and the next state;
3. pre-compute the content needed for the Snapshot and History;
4. atomically replace `current_state.md`;
5. append the complete Current text to the single `snapshots.md`;
6. calculate the Snapshot start and end lines and the hash from the actual append result;
7. append the index entry to `history.md`;
8. read the three files back and verify consistency;
9. delete the successful transaction and release the lock.

If the process is interrupted after step 4 or step 5, rerun the commit with the same next-state. The script continues from whichever step has already been completed and does not append the same event twice. The same ID with different content fails.

Only `CHECKPOINT_COMMITTED` means the commit succeeded. `verify` is a read-only operation and prints `TASK_STATE_VALID` on success.

## When a Checkpoint must be saved

- before requesting a Requirements, Goal, Plan, or Delivery review;
- after you make an approval, a rejection, or another key Decision;
- when switching Phase, Stage, or Session;
- when saving valuable implementation progress or machine verification results;
- when entering rework, a block, a pause, or a close;
- before context compaction, a model change, or a task handoff;
- before starting the next Stage's Plan.

When you prepare to compact, the Phase usually stays the same. The Agent only saves a recoverable checkpoint, then stops starting new steps, delegations, and external actions.

## Context compaction and model changes

The Agent cannot reliably see the true Token usage of every Harness, so whether to compact is managed by you or by the host.

Recommended practice:

1. if the Harness shows context usage, consider compacting at about halfway;
2. the end of a Stage, after its save is confirmed, is also a good time to compact;
3. tell the Agent to save a pre-compaction checkpoint first and pause;
4. wait until the script explicitly returns `CHECKPOINT_COMMITTED`;
5. then use the Harness's manual compaction feature;
6. after compaction finishes or the model changes, ask the Agent to continue through the recovery flow, not to restart the project;
7. check the Agent's restatement of the Goal and the current state.

You can say this directly to the Agent:

> I am about to compact the context. Please save and verify the current Task's checkpoint first, keeping the Goal, the current Plan, user Decisions, existing authorizations, actual progress, machine evidence, failed routes, unfinished items, and the next step. After you get `CHECKPOINT_COMMITTED`, pause and do not start new work.

For recovery you can say:

> This is a post-compaction recovery or a model change. Please run the read-only verify first, reread `goal.md`, `current_state.md`, the Case indexes, and the recent History, check the actual files and the diff, and then restate to me the final Goal, the current stage, existing approvals, unfinished items, and the next step. Wait for my confirmation before continuing.

## Why file intake is not part of the state machine

You may reference a new file at any stage through a path, an attachment, or `@`. The appearance of a file does not mean the requirements, the Goal, or the Plan changed, so intake is a separate flow that does not change the current Phase.

| File location | How it is handled |
|---|---|
| Already inside the current Task | Used in place, not copied again |
| Inside the Workspace, outside the current Task | Copied and verified into `UserInput/I-NNNN/`; the copied contents are listed; you are asked whether to delete the source files |
| Outside the Workspace | Copied and verified into `UserInput/I-NNNN/`; you are only told that it has been copied, and you are not asked to delete the source files |
| No active Task at the moment | A single file does not create a project automatically; first let the user choose or create a Task |

intake only handles paths you explicitly mention. It refuses to copy `.git`, state directories, protocol directories, symbolic links, junctions, and a recursive `tasks` automatically.

## How a Case is formed

At the start of every step, and after a compaction recovery or a model change, the Agent reads only the Case indexes of Global, Workspace, and the current Task. An index contains a short summary, the root cause, and the trigger scenario; the detailed Case is read only when the current scenario matches.

After an error occurs:

1. the Agent and the script record the error signature, the confirmed root cause, and the evidence;
2. checkpoint counts occurrences of the same `ROOT_CAUSE_KEY` in the current Task History;
3. the first and second occurrences only keep accumulating;
4. on the third occurrence, when no Case exists yet, the script prints `CASE_RECOMMENDATION_REQUIRED`;
5. the Agent explicitly warns you and recommends saving it;
6. after you agree, append `CASE_RECORD_APPROVED` to `decisions.md`, then write the Case index and details;
7. History stores the Case ID and links it to the Plan, Decision, and Snapshot of the time.

When you consider a Task Case very general, you can approve promoting it to a Workspace Case or a Global Case. The original Case is not moved or deleted, and the promotion record keeps the source and the applicable boundary.

## Three platform tool entries

The release package contains all the scripts. The Agent picks the entry based on the current operating system:

- Windows: `.agent-protocol/tools/checkpoint.cmd` and `intake.cmd`; when a path contains CMD metacharacters such as `%`, `!`, `&`, or `^`, call the corresponding `.ps1` directly with PowerShell instead;
- Linux: `sh .agent-protocol/tools/checkpoint.sh` and `sh .agent-protocol/tools/intake.sh`;
- macOS: the same as Linux.

End users need no Python, Node, or other additional runtime. CMD only calls PowerShell and does not process ledger text. All ledgers use UTF-8, no BOM, LF, and one trailing newline, so that PowerShell, CMD, and POSIX Shell do not break hashes or line numbers through different text handling.

## What to trust during recovery

The evidence priority is not "the ledger is always right". A normal recovery needs to look at all of the following at the same time:

1. your latest explicit instructions;
2. the read-only verification result of checkpoint;
3. the actual files and the version-control diff;
4. tests, builds, and artifacts;
5. the real state of external actions;
6. the Current State and the historical ledgers.

When a ledger and the actual workspace conflict, keep the original history and append a correction record. You must not modify an old Decision, fake that the past was already correct, or blindly redo an external action whose result is unknown.
