# Why It Is Designed This Way (WHY)

This document explains why PAPOP turned out the way it did: what problems it is trying to solve, what flaw each mechanism is aimed at, and what you as a user need to do.

If all you want is how to install and use it, [README](../README.md) and [Installation instructions](INSTALL.md) are enough; this document answers the "why".

---

## In short

When I use AI to get work done, it has burned me a few times: halfway through a conversation it suddenly "loses its memory", it drifts off while working, and in the end I have no idea what it actually touched. So I put together this set of rule files, aimed squarely at these few problems.

It is not software, there is nothing to install, just a few Markdown text files that you drop into your project, and the AI reads them by itself every time it starts work.

## 1. What problems it solves

### 1. One context compaction, one model switch, and everything said before is forgotten

**Problem**: the AI's "memory" is just a context window of limited length. Talk long enough and the client compacts it; or you switch to another model or another window, and what was said before and how far the work got are all gone.

**Solution**: move the memory out of its head and onto the disk. The project gets a `.agent-work/` directory that exists purely to hold the ledger. At every milestone (plan finished, a step done, you make a key decision, delivery coming up, hitting a wait, before and after an external action), the AI writes the current state down again. Compaction can wipe what is in its head; it cannot wipe files on the hard drive.

The ledger has a few pieces:

| File | What it does |
|------|------|
| `current_state.md` | **Current state**, short but complete: what the project looks like now, how far it has got, what to do next |
| `plan.md` | **The plan**, append-only; every change to the plan adds a whole new block and leaves the old ones untouched |
| `decisions.md` | **Your decisions**; every time you say "approved", "acceptance passed", or "this one can ship", it writes that down, bound precisely to the plan or the delivery revision of that moment |
| `history.md` | **Milestone events**, append-only; each entry records only "what changed this time", never copying the full text again |
| `snapshots/` | On every checkpoint it stores a **verbatim copy** of the current state, and once stored that copy must not be changed |

### 2. Once the context gets long, attention scatters and it forgets what it should be doing right now

**Solution**: `current_state.md`. Its core requirement is "short + complete + readable at any moment" — one read has to tell three things: what has already been finished, what state the project is in now, and what to do next. Before it picks the work back up, the AI reads this first, instead of digging through tens of thousands of lines of history.

### 3. It drifts off target while working and forgets what it originally set out to do

**Solution**: `plan.md` plus your approval. The rules require that before it touches anything, it must first write the plan down and show it to you; only after you nod does the work start. The plan is appended block by block, and each block carries its own goal, scope, what it will not do, the steps, and how each step counts as done.

There is a key design point here: **writing a new plan does not mean you have approved it**; and what you approve is *that one revision* — change it once and you have to approve it again; an old approval cannot quietly move over to a new revision. That is how it is stopped from changing the goal behind your back.

### 4. History keeps piling up, and reading all of it is costly and pollutes the context

**Solution**: fix the field format of the records, then **locate by search and read only that small block**. Every record has fixed tags (task ID, plan revision number, event ID, state, subject, and so on). When it needs history, it first runs `grep` to search for the ID and locate the block, reads only that block (a few dozen lines), and never loads the whole file. History itself also stores only "what changed this time" plus a snapshot pointer, instead of copying the entire state again.

### 5. Not knowing what it actually did, and being afraid it will go off the rails

**Solution**: several locks chained together —

- before it touches anything there must be a plan you approved (Plan Approval mode);
- the moment a step is finished, the ledger has to be updated;
- after delivery **you** have to do the acceptance, and the rules hard-code it: **the agent passing its own checks only proves that it checked; it cannot say "acceptance passed" in your place**;
- external actions (publishing, sending messages, buying things, changing production) need separate authorization, with an entry written before and after execution; when the result is uncertain (it went out but you do not know whether it worked) it must **check first and must not resend**;
- you can define gates at any time, for example "wait for my confirmation before publishing" — the agent **cannot decide for itself that such a gate is "no longer important" and drop it**; a gate is released only when you explicitly release it.

### 6. Not every project deserves this much weight

**Solution**: grade them into tiers.

- **Plan Approval mode**: for real projects, where every key point needs your nod;
- **Task Delegation mode**: for when you just want to hand over a goal and let it push forward on its own — it works within the boundary you set, and stops to ask only when a key decision is missing, specific authorization is missing, or it runs into a gate you set;
- **FAST**: small jobs that can be finished in one go create no ledger; it just does the work and shows you the result.

## 2. What you need to do

### 1. Keep an eye on the context, and call a halt yourself when it is time to compact

Under these rules, **the AI does not estimate tokens and does not set a fixed threshold** (that is deliberate — different models and different clients have different limits, and hard-coding a number is only misleading). So this job is yours: when the client's context usage looks about full, tell it:

> Persist the current state to disk, the context is getting a bit long and I want to compact manually.

It will save the ledger and check it over, then **stop and wait for you**. Once you have confirmed it is saved, run the compaction yourself (for example `/compact`), and when that is done tell it:

> Continue

It will read `current_state.md`, check it against the real files, and carry on. Note: **gates that were never released and deliveries that were never accepted are still there after compaction** — compaction does not turn them into "approved by default".

### 2. When it asks you to approve a plan, read it carefully

This is the most valuable part of the whole thing, so do not be lazy. If it looks fine, reply "approved"; if not, just say what is wrong and how you want it changed — it will put out a new revision and you approve again. **Only your "approved" counts**; its own "I understand your requirements now" is not an approval.

### 3. When it asks you for acceptance, test it step by step

It will give you the deliverable, the acceptance steps, and the pass criteria. Try them one by one: if they pass, say "acceptance passed"; if something is wrong, just describe it — "XXX has a bug, and this is how it shows up". It will rework a new revision, and you check it again.

### 4. For pure chat, just say hello

If you are only asking something in passing or discussing an idea, say one line to it:

> A pure Q&A: XXX

That way it will not create a task ledger for you, and it will not make you approve a plan.

## 3. A few points that are easy to mix up

- **"A plan was written" is not "you approved it"**: persisting a plan to disk only makes it a proposal; it takes your nod to take effect.
- **"It says it is done" is not "you passed acceptance"**: these two are recorded separately — it can mark "complete", but the acceptance state is still "waiting for your acceptance".
- **It cannot say "acceptance passed" in your place**, and it cannot mark an unfinished step as finished.
- **Decision records are append-only and never rewritten**: if you change your mind later, it adds a correction entry instead of quietly editing the old one — so "who approved what, and when" can always be looked up.
- **Once a small job has been upgraded into a formal task it never drops back down**: this prevents downgrading a job that should leave a record into one that leaves none, just to save effort.

---

**One sentence to sum it up**: it turns "what the AI did, who approved it, how far it got, whether the next move is allowed" into records on disk that can be looked up, handed over, and recovered — instead of relying on the model to remember it all inside an ever-growing conversation.
