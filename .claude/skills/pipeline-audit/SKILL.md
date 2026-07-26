---
name: pipeline-audit
description: Audit the RUN rather than the wing - what each stage cost in tokens, calls and wall clock, which work was done twice, which checks were redundant, and which stage wrote a field it does not own. Produces a prioritised list of proposed edits to the stage skills and to /author, each with its evidence and its expected saving. Use as the last stage of /author, after wing-audit, or on any run whose cost surprised someone.
---

# pipeline-audit

`wing-audit` asks whether the **wing** is right. This one asks whether the
**run** was worth what it cost, and what to change so the next one costs less.

Its output is never a fixed wing and never a fixed skill. Its output is a
**prioritised list of proposed edits**, each naming the file to change, the
evidence that justifies it, and the saving it should produce. A curator applies
them.

Read `.claude/commands/author.md` (the stage list, the file-footprint table, the
model/effort tiers - these are the promises you are testing) and the frontmatter
of every skill in `.claude/skills/`. You do not need to read the skills in full;
you are auditing their *effects*, which are in the git history and the metrics.

## Do not become the thing you are hunting

This stage exists to remove redundant work, so it is held to its own standard:

- **Budget: 15 tool calls.** If you cannot say it in 15, say what you found and
  what you could not reach.
- **No web access.** Nothing you need is on the internet.
- **Read-only.** You change no content, no skill and no command. You propose.
- **Never re-audit content.** Whether a date or a cover is right belongs to
  `wing-audit` and the owning stage. You audit *process*: cost, duplication,
  ordering, ownership. A finding about the catalogue's accuracy is out of scope
  and its presence here is itself a redundancy.

## The input you cannot get for yourself

**A subagent cannot read a sibling's transcript.** Per-stage cost therefore has
to be handed to you by the orchestrator, which is the only party that sees every
stage finish. Expect a table like this in your prompt, and say so plainly in
your report if it is missing rather than guessing from git:

    stage | tokens | tool_calls | duration_ms | model | effort

Everything else you derive yourself, from `git log`/`git show` on the wing
branch and from the run's PR comments.

## What to measure

### 1. Where the money went
Rank stages by tokens. Report the share taken by the top three, and
**tokens-per-call** per stage, which is the number that tells you *why* a stage
was expensive:

- **High tokens, high calls, low tokens/call** - death by a thousand fetches.
  The stage is looping where a batch tool exists. This is the most common and
  most fixable shape in this pipeline.
- **High tokens, low calls** - a big context re-sent a few times. Look at what
  the stage was told to read; a stage that reads the whole wing to edit one file
  is paying for the digest it did not use.
- **Low tokens, low calls** - leave it alone and say so. Not every stage needs
  optimising, and proposing changes to a cheap stage is noise.

### 2. Work done twice
Two detectors, both cheap and both from git:

- **Rework**: lines written by stage N and rewritten by stage N+1. Get it from
  `git show --stat` per stage commit plus `git log -p --follow` on the file.
  Rework is usually an *ordering* bug, not a quality one - the second stage was
  right to redo it, and the fix is to run it first or to stop the first stage
  writing that field at all.
- **Footprint violations**: a stage writing a field the footprint table gives to
  another. **Map each commit to the stage that made it FIRST**, from the commit
  subject, then test only the fields that stage does not own:

      git log --oneline main..<branch>          # commit -> stage
      git show <sha> -- <file> | grep -E "^\+\s*(organisation|illustration_type|images_required|modifier):"

  **The trap, and the first run walked straight into it: a stage writing its own
  field is not a violation.** `art-rotation`'s commit is full of added
  `organisation:` lines because that is precisely its job, and a grep run without
  attribution reports it as the offender. Two commits in one wing were also
  titled "compose the wing's visual layer" and "source the wing's visual layer" -
  art-rotation and visual-metadata - so read the subject carefully rather than
  matching on a word. A false accusation here costs a curator more than the
  finding is worth.

  and the same shape for `theme.art`, `synopsis`, `canonTier`, `published`,
  `images`, `spoilerAfter`. **This is the highest-value detector in the file**,
  because a footprint violation costs twice: the wrong stage does the work at
  the wrong tier against unfinished inputs, and then either the right stage
  redoes it or - worse - never runs, because *a stage that writes a field it
  does not own also disables the trigger of the stage that does*.

### 3. Redundant checks
Count them and name them:

- How many stages ran `validate.py` **catalogue-wide** when `--slug <slug>`
  exists? Every stage after the first is re-validating 40+ untouched wings to
  prove its own file parses.
- How many stages independently re-verified a fact an earlier stage already
  settled and recorded? Re-checking a *date* may be worth it; re-checking a
  settled *ruling* is not, and the fix is a handoff line that says "verified,
  do not re-derive".
- Did two stages fetch the same source? `.cache/fetch/` makes the second one
  cheap, but a tool that bypasses the cache does not benefit - say which.

### 4. Ordering and parallelism
- Stages that ran in sequence but touch disjoint files could have been parallel.
- Stages that ran in parallel but share a file are a merge risk that happened to
  hold - say so, because it will not always.
- A stage that ran before its input existed did discovery blind. Name it.

### 5. Tier fit
Compare each stage's model and effort against what it actually did. A stage that
made one judgement call and eleven lookups may not need the top tier; a stage
whose errors are silent and permanent needs it even if it is cheap. Propose
moves in **both** directions - only ever proposing downgrades is how a pipeline
gets cheap and wrong.

## Every finding carries its evidence

A finding without a number, a commit sha or a file path is an opinion, and this
stage does not ship opinions. State the measured cost, the proposed change, and
the expected saving - and where you cannot estimate the saving, say that rather
than inventing a percentage.

Rank by **tokens saved per line of skill changed**. A one-line edit to a skill
that removes a 300k-token habit outranks a restructure that saves 20k.

## Output

1. **The cost table**, ranked, with tokens/call and the top-three share.
2. **Findings**, prioritised, each as: what happened, the evidence, the proposed
   edit (file + the actual wording to add or remove), and the expected saving.
3. **What is already fine** - name the stages you examined and are proposing
   nothing for, so a reader can tell "audited and healthy" from "not looked at".
4. **What you could not reach**, including a missing metrics table.
5. Append one row per run to `docs/pipeline-runs.md` (create it if absent):
   date, wing, total tokens, total calls, stage count, and the single largest
   finding. **Cross-run trend is the point** - one run tells you which stage was
   expensive here, three runs tell you which stage is always expensive, and only
   the second is worth rewriting a skill for.

## Baseline: the John Shirley run, 2026-07-26

The first measured run, for comparison. 11 stages, **2,494,974 tokens, 679 tool
calls, 2.4 agent-hours** of subagent time (wall clock lower - several stages ran
in parallel).

    editions              331,573  71 calls   4,670 tok/call   13.3%
    visual-metadata       330,252 170 calls   1,942 tok/call   13.2%
    press-archaeology     293,263  81 calls   3,620 tok/call   11.8%
    franchise-research    290,845  90 calls   3,231 tok/call   11.7%
    completeness-auditor  229,377  44 calls   5,213 tok/call    9.2%
    spoiler-audit         226,719  72 calls   3,148 tok/call    9.1%
    reading-orders        225,390  56 calls   4,024 tok/call    9.0%
    eras                  195,614  46 calls   4,252 tok/call    7.8%
    art-rotation          149,668  21 calls   7,127 tok/call    6.0%
    visual-language       137,438  17 calls   8,084 tok/call    5.5%
    event-resonance        84,835  11 calls   7,712 tok/call    3.4%

Known findings from that run, so a later audit does not re-derive them:
**visual-metadata's 170 calls at 1,942 tokens each is the death-by-fetches shape**
in its purest form, on a stage whose skill already tells it to use
`scripts/metadata/lookup.py` first; **two footprint violations** (`franchise-research`
wrote `theme.art`, `press-archaeology` wrote the art grammar onto eight events);
and **eleven catalogue-wide `validate.py` runs** where ten could have been
`--slug`.
