# Why Agent Projects Need a State Machine

[Back to README](../README.md) · [See how the state machine works](HOW_EN.md) · [Installation guide](INSTALL.md)

## In one sentence

An Agent can keep doing things for a long time, but one conversation is not a reliable project record. A state machine turns "how far we are, what has been approved, what is allowed next" into checkable files and explicit transition rules.

It is not there to make the process look more formal. It is there to keep long tasks from gradually losing shared facts after the conversation grows, the model changes, context is compacted, work is redone, and delivery is reviewed several times.

## What usually goes wrong without a state machine

### 1. The conversation is still there, but the details are gone

A long conversation may be compacted automatically. The model usually still remembers the general direction, but it may lose details such as:

- scope you explicitly excluded;
- why one option was rejected;
- which Plan revision was actually approved;
- whether an external action has already been performed;
- whether the tests were really run, or only planned;
- where it is safest to continue from.

If these facts exist only in the chat log, recovery has to rely on a summary or on the model's guess.

PAPOP stores the final Goal, the Plan, user Decisions, the Current State, and historical Snapshots separately. After compaction, it recovers from the files first, then checks them against the actual workspace.

### 2. "Do this project for me" is misread as "every action is approved"

Authorization for a project is not authorization for every action. For example, "help me publish the website" does not necessarily include buying a domain, deleting the old site, overwriting production, or sending private material to a third party.

The state machine splits authorization into recognizable gates:

- strict mode requires exact confirmation of Requirements, Goal, Plan, and Delivery;
- Autonomous mode lets the Agent keep moving inside the Task's authorization boundary;
- both modes pause when a key decision is missing, when a specific external authorization is needed, when a user gate is reached, or when the final Goal is about to change.

This way the Agent does not have to ask again for every small step, and one vague authorization cannot jump over the decisions that really matter.

### 3. The plan changed, but the old approval is still being used

Long projects are redone often. The most dangerous case is not the rework itself, but a Plan that has materially changed while the Agent keeps executing on the "approval" of an old revision.

PAPOP gives Requirements, Goal, Plan, and Delivery stable references. An approval or a rejection is bound to a specific revision. A new revision needs a new decision, and an old approval is not inherited automatically.

### 4. The Agent says "done", but there is no reliable evidence

A model can write a very confident completion note, while it skipped a test, misread command output, failed to check the generated files, or mistook "the file has been produced" for "the result meets the requirement".

PAPOP records separately:

- whether the Agent finished the implementation;
- whether the scripts, tests, or the diff passed;
- whether you accepted the current Delivery.

Structure, state transitions, hashes, Snapshot line numbers, and file copies are verified by scripts. The model's retelling cannot replace machine evidence, and Agent completion cannot replace your acceptance.

### 5. The state was half-written, and recovery cannot tell which copy is real

If the Agent changes the Current State first and is then interrupted while writing History, it leaves files that disagree with each other. The next conversation may read one of them and continue, spreading the error further.

PAPOP's checkpoint tool checks fields, references, and state transitions before writing, takes the Task lock, and then updates Current, Snapshot, and History in a fixed order. It saves transaction information and, after a crash in the middle, finishes idempotently under the same transaction. It prints `CHECKPOINT_COMMITTED` only after the read-back verification succeeds.

### 6. There is plenty of history, but no way to find why it was done that way

Packing everything into one ever-growing file does not create usable memory. Reading all the history every time wastes context, and it is easy to grab the wrong point out of a large amount of text.

PAPOP makes `history.md` the search entry point. Each history record stores keywords and a summary, and links to:

- the corresponding Plan number;
- the user Decision number;
- the Case number;
- the Input number;
- the exact start and end lines of the Snapshot in the single `snapshots.md`;
- the hashes of the State and the Snapshot.

To look up history, search History first, then follow the pointers and read only the records you need. This answers "why it was done, which revision was approved, what was done at the time, and what the result was".

### 7. The same mistake keeps being repeated

Ordinary history can prove that a mistake happened, but it does not necessarily warn the Agent in time the next time the same situation appears.

PAPOP's Case stores the root cause, the trigger scenario, the way to avoid it, and the chain of events. Within one Task, when the same confirmed root cause appears for the third time, the system requires the Agent to explicitly warn you and to recommend fixing it as a Case. The details are read only when the trigger scenario matches, so that not every lesson is loaded every time.

A Task Case affects only the current project. When you consider it strongly general, you can explicitly approve promoting it to the workspace or global level; the original Case and the source chain are still kept.

### 8. You provided files, but origin and ownership became confusing

You may put files in the workspace root first, or reference files outside the workspace during the conversation. If the Agent edits the original directly, it later becomes hard to tell which files are inputs and which are task outputs, and your files may be deleted by mistake.

PAPOP makes file intake a separate flow that does not change the main state machine:

- files already inside the current Task are used in place;
- files inside the workspace but outside the Task are copied and verified, and then you are asked whether to delete the source files;
- files outside the workspace are only copied into `UserInput/`, and you are not asked to delete the source files.

## Why a "state machine" is needed instead of just one progress note

A progress note can only describe "what the model believes happened". A state machine also defines:

- which states are currently legal;
- what conditions allow a move to the next state;
- which transitions require a user Decision;
- which revision of the Goal, Plan, or Delivery is approved;
- when a checkpoint must be written;
- how to stop and recover when a write fails;
- which things are still unknown and must not be written as complete.

A state machine turns natural-language promises into verifiable constraints. What it reduces is the cost of re-explaining the project in every conversation, and the risk of an error growing further after a bad recovery.

## Why both strict approval and autonomous progress are provided

Different users want different levels of control.

Strict approval suits these situations:

- you want to decide the requirements, the final Goal, and the stage plan yourself;
- rework is expensive, so one more look at the Plan before implementation is worth it;
- the project needs to clearly prove who approved which revision and when;
- you do not want the Agent to infer your intent on its own at important points.

Autonomous progress suits these situations:

- the task goal and the authorization boundary are already clear;
- you want the Agent to complete investigation, changes, and verification in a row;
- ordinary implementation choices do not need item-by-item approval;
- you step in only for key decisions, extra authorization, or gates you have set.

Both modes share the same ledgers, recovery, machine verification, Case, and file intake mechanisms. The difference is which state transitions must wait for a human.

## What the state machine cannot solve

PAPOP cannot guarantee that a model never makes an error, and it does not replace:

- the Harness's sandbox, permission, and approval mechanisms;
- operating-system permissions;
- Git, cloud drives, or other backups;
- the release and rollback rules of a production environment;
- human judgment about the requirements, the Plan, and the final deliverables.

Ledger contents can be written incorrectly too, so recovery must compare them with your latest instructions, the actual files, diffs, tests, and external state. State is a recovery entry point, not unquestionable truth.

## When it is worth using

The state machine is usually worth using if a task spans multiple stages, may have its context compacted, involves rework, contains important user decisions, needs a handoff, or will still need maintenance later.

If you only want the Agent to follow basic discipline for files, Git, dependencies, verification, and authorization, and the task is short and needs no persistent state, you can install GlobalRules Only alone.
