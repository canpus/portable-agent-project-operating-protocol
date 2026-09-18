# Make AI Remember Like a Human

> **PAPOP Design Philosophy #001**

---

**I’m starting to suspect that a lot of the conversation around “long-term AI memory” goes off the rails right from the start.**

Context windows go from 100K to 500K to 1M, and sure, that sounds great.

The bigger the window, the more history the model can see. And that creates a very tempting illusion: maybe the model is “remembering” more and more.

But once I actually started using AI on a long-running project, it felt very different.

The further the project went, the more baggage the AI had to carry: old requirements, new requirements, abandoned ideas, random discussions, decisions that still mattered, decisions that no longer did.

Sure, it could still “see” all of it. But that didn’t mean it still knew what was valid **now**.

At some point, this stops looking like better memory and starts looking like a heavier backpack.

## Context Feels More Like a Workbench

I’ve started thinking of Context as a workbench.

A bigger desk is nice. Everyone likes a big desk.

But no matter how big the desk is, you probably wouldn’t dump every company archive, meeting note from three years ago, abandoned design, failed experiment, and random historical artifact onto it all at once.

Do that long enough and your desk turns into a landfill. Huge context windows can feel surprisingly similar.

The hard part of a long-running project isn’t just whether old information still exists. The harder questions are: **what still counts, what has been superseded, why a decision was made, where the project is right now, and what should happen next.**

Context can hold information. It doesn’t automatically organize the relationships between those pieces of information for you.

## Humans Can’t Remember Shit Either

You finish a meeting today, and two days later someone asks, “Who originally requested this?”

A month later, everyone is asking, “Are we even allowed to change this logic?”

Six months later, the team stares at a weird chunk of code in silence because nobody remembers why the hell it exists.

We joke about “spaghetti code” all the time, but code complexity is only part of what makes old systems terrifying. The nastier problem is that the context died, the decision history disappeared, the people who wrote it left, and nobody knows whether deleting one ugly block is going to quietly murder some ancient business rule.

That’s why humans invented requirements docs, project plans, Git, Issues, meeting notes, decision logs, version numbers, checkpoints, runbooks.

If you think about it, all of these tools are basically an admission:

> **We never really trusted the human brain in the first place. It has always been kind of unreliable.**
>
> **Long-lived projects survive because we put important information outside our heads and organize it well enough to find it again.**

## So What Happens If We Apply That Idea to AI Agents?

PAPOP didn’t start out as something this complicated. I just wanted AI to help me build a tool that could automatically generate customs declaration documents.

I’m barely a programmer. If you think a humanities guy who taught himself Python for two weeks three years ago counts as a programmer, fine, you win.

“Programming beginner” is probably more accurate.

So I did what a lot of people do now: I gave the Agent an initial requirement, kept adding more requirements, folded my hands, and prayed it would somehow turn all of that into the thing I wanted.

Then the project kept growing. The context got fatter and fatter. I started worrying that once I compressed the conversation, the model would forget half the project, so I made it write History first.

History grew past 2,000 lines. Reading the whole thing every time was burning too many tokens, so I added Current State, then gave History more structure and indexing so the Agent could first figure out where it was, and only dig into old history when it actually needed to.

Then I realized the AI was a little too... free-spirited. It would just go off and do whatever it thought made sense. I wanted to know what the hell it planned to do before it did it. So Plan showed up.

Then I realized “what we did” wasn’t enough. **Why we did it mattered even more.** So Decision appeared.

Then I needed to know whether important changes had actually been approved by me, or whether the Agent had quietly invented consent inside its own head. That led to Approval, Revision, Checkpoint, Recovery...

At some point I looked back at the whole thing and thought:

This has gotten kind of ridiculous.

All I wanted was to stop an AI from losing the plot during a long project, and somehow I ended up building this fairly elaborate thing.

## What the Fuck Did I Just Build?

At one point I sent the repository to GPT and asked it to draw a flowchart for me.

Side note: the reason I asked GPT to draw the flowchart was that **I had no idea how to explain the damn thing to other people myself.**

Then I looked at the diagram and just sat there for a moment.

**What the fuck is this thing?**

**Wait... I built this thing?**

### Am I allowed to feel a little proud now?

Proud, yes. Completely confident? Not even close.

I still wonder whether someone else built this exact idea years ago. Maybe there are teams out there with systems ten times more mature than mine. I genuinely don’t know.

I got here in the least academic way possible: run into a problem, hack together a solution, hit the next problem, solve that one too, repeat.

I didn’t even know the term “state machine” when I started.

When I pushed v0.1.0 to GitHub for the first time, I was too lazy to come up with a repository name, so I asked DeepSeek to name it for me. It gave me something with `protocol` in the name.

Only later, as I kept discussing the architecture, did I slowly realize:

**Oh. This thing has basically grown state-machine behavior inside it.**

Then more and more people started asking me about the same kinds of problems when we talked about long-running Agent tasks.

That’s when I started feeling a little less crazy.

At least I’m clearly not the only person falling into this hole.

**Is PAPOP a good answer? I’m still testing that. But the problem itself? At this point I’m pretty damn sure it’s real.**

Looking back, it feels like I just kept crashing into walls until I noticed that all of those walls were pointing toward the same thing:

**the model’s conversation context was being forced to carry far more long-term responsibility than it should.**

Every time I hit a wall, I only tried to fix the problem in front of me.

And somehow, one step at a time, it grew into this.

## Give Important Information a Place to Live

Eventually I stopped obsessing over “How do I make AI never forget?”

That goal sounds less convincing the longer I think about it.

What started to matter more was simple: **important project information should have somewhere specific to live.**

- **Goal**: where we are trying to go;
- **Plan**: what we intend to do next;
- **Decision**: why we made a choice;
- **History**: what actually happened;
- **Current State**: where the project is right now;
- **Approval**: which important changes were actually confirmed.

When the model comes back, it doesn’t need to recite the entire project from memory. It just needs to recover the current state, then pull old information only when it is relevant.

That means the AI can actually afford to forget.

As long as the ledgers are still there, one compaction, one dropped session, or one model switch doesn’t have to wipe out the project.

Of course, if you delete the ledgers yourself—or compact the context before the AI has written anything down—then congratulations, you played yourself.

The model doesn’t need to cling to a 500K context window like its life depends on it. Project state can live outside the conversation. History can live outside the conversation. When something matters, go fetch it.

> **Today’s workbench only needs today’s tools. Everything else can stay quietly in the warehouse.**

This feels almost backwards compared with a lot of the “make the model remember more” discussion.

Maybe I’ll eventually prove myself wrong. I’ve stepped on plenty of rakes already, and PAPOP is nowhere near mature.

But I keep coming back to one idea:

# **Even if it forgets, it shouldn’t lose the project.**

I don’t really want an “AI genius” that survives by brute-forcing everything with a ridiculous memory.

I want a reliable **project buddy**.

It doesn’t need the whole world stuffed into its head. But it should know where the project is, which decisions are already settled, where to find history, when to stop and ask me something, and how to recover after losing context.

If PAPOP eventually works the way I hope it does, I think this is the part I’ll find most interesting.

## I Know I’m a Beginner. Beginners Still Have Brains.

I’m not trying to sound authoritative here.

I know exactly what I am: a humanities guy who taught himself Python for two weeks three years ago and now gets Agents to write code for him.

Absolute beginner territory.

But I’m also not going to pretend I didn’t see a real problem just because I came at it from the wrong background.

**Beginners still have brains, okay?**

There is only one thing I’m confident enough to say right now:

> # **Important project state probably shouldn’t live only inside the model’s head.**

How far this idea can go?

I’m still finding out.
