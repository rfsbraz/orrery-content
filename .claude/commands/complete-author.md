---
description: Take one author from nothing (or from partial) to a complete, sourced, verified, illustrated and translated wing by running every curation agent in dependency order, with explicit handoffs between them.
argument-hint: <author or franchise> [--slug <slug>] [--from <stage>] [--locales pt-PT,...]
---

# /complete-author

Complete **$ARGUMENTS** as an Orrery wing.

This is the drill. Each stage is an agent with its own skill file, and **those
skill files are the source of truth for how the work is done.** This command
owns only what no single agent can see: **what order they run in, what they hand
each other, and what has to be true before the next one starts.**

You are the orchestrator. You do not do the stages' work. You sequence them,
carry the handoffs, verify the artefacts, and collect the curator's decisions.

## The two rules that matter most

**1. Stages that write the same file must not run in parallel.**

Learned expensively: completeness and visual-metadata were once run concurrently
on the same `works.yaml`. Both branched from the same base, both edited the same
lines, and the naive merge would have shipped covers for only the pre-audit works
while looking complete. Check the footprint table before putting anything in a
parallel group.

**2. Agents cannot see each other's work. You are the channel.**

Every stage writes a handoff file; every stage reads the ones before it. A stage
that does not know 18 works were just added will silently skip them, and the gap
will look like completion. This has happened twice: 23 works reached main
unaudited for spoilers, and the editions layer never re-ran after a completeness
audit, leaving 0 of 18 new works with an edition.

## File footprints

Parallel groups below are parallel *because* their members touch different files.

| Skill | Writes |
|---|---|
| `franchise-research` | everything (stage 1 only, runs alone) |
| `completeness-auditor` | `works.yaml` |
| `press-archaeology` | `authors/<id>.yaml`, `events.yaml` |
| `world-events` | `events/global.yaml` |
| `eras` | `eras.yaml` |
| `reading-orders` | `orders.yaml` |
| `event-resonance` | `franchise.yaml` (`globalEvents`) |
| `where-to-start` | `franchise.yaml` (`startHere`) |
| `spoiler-audit` | cross-cutting: works, events, characters, authors, orders |
| `visual-metadata` | `works.yaml` (images), `franchise.yaml` (header), `authors/<id>.yaml` |
| `editions` | `editions.yaml` |
| `translation` | `content/i18n/<locale>/**` only |
| `wing-audit` | read-only, plus trivial mechanical fixes |

Two collisions are easy to miss: **`event-resonance` and `where-to-start` both
write `franchise.yaml`**, and **`spoiler-audit` and `visual-metadata` both write
`works.yaml`**. Never pair either.

## The handoff contract

Each stage writes `.orrery/<slug>/<stage>.yaml` on its branch before finishing:

```yaml
stage: completeness-auditor
summary: "77 works -> 95"
produced:
  newWorkIds: [stephen-king/elevation, stephen-king/danse-macabre]
  changedProse: [stephen-king/insomnia]      # ids whose prose changed
  changedDates: [stephen-king/the-eyes-of-the-dragon]
forStages:
  visual-metadata: "18 new works need covers"
  editions: "18 new works have no edition"
  spoiler-audit: "18 new synopses unaudited"
  translation: "18 synopses + 4 author bios need pt-PT"
  reading-orders: "orders claiming to be complete are now stale"
openQuestions:
  - "The Eyes of the Dragon redated 1987 -> 1984; this reorders the default order."
```

**Every agent's first instruction is to read `.orrery/<slug>/` in full.** Every
agent's last is to write its own file. Pass the relevant `forStages` lines into
the next agent's prompt as well; a file it must remember to read is weaker than a
brief it cannot miss.

`openQuestions` accumulate across stages and become the curator's list at the end.

**A handoff that does not parse is worse than a missing one.** The next stage is
told to read it, silently gets nothing, and its resulting gap looks like
completion. This happened: a stage wrote a mapping key followed by a sequence
under the same key, which is invalid YAML, and every check stayed green because
nothing validated `.orrery/`. `validate.py` now errors on an unparseable
handoff. Write the file, then confirm it loads before you call the stage done.

These files are branch-local working state, not canon. **The integration stage
deletes `.orrery/` before the final merge** - the PR bodies are the durable
record.

## Prep

1. **Resolve the slug.** `content/franchises/<slug>/`. Reuse an existing slug;
   otherwise lowercase-hyphenated, accents stripped (`joao-tordo`). Author ids
   follow the same rule. Ids are permanent; choose carefully once.
2. **Record the starting state** and keep the numbers, because every later claim
   of progress is measured against them:
   `python scripts/validate.py`, `python scripts/i18n_coverage.py`,
   `python scripts/event_density.py`.
3. **One worktree per agent**, branched from that stage's base:
   `git worktree add ../wt-<slug>-<stage> -b <slug>/<stage> <base>`
4. **Read `docs/SCHEMA.md`.** All of it. It is the contract every stage writes to.

## The pipeline

### Stage 1 - Research (`franchise-research`)
Skip if the bundle exists. One agent produces the whole thing: author profile and
`lifeEvents`, bibliography, eras, franchise events, orders, and where the
franchise earns them, characters, connections, `startHere`.

**Gate:** validator green, and the capability set is a deliberate choice. A
franchise with no real connections should have connections **off**; the
fewer-layers case is a feature, not a deficiency.

### Stage 2 - Completeness (`completeness-auditor`)
**Before anything that annotates works**, because it changes how many exist.
Missing works, first-publication dates, tier consistency, subseries links,
`withAuthorIds` and `authorRole`.

**Gate:** validator green and **the work list is final**. A late-arriving work
costs a re-run of stages 4 through 8.

### Stage 3 - Enrichment and structure (parallel: 4 agents, different files)
`press-archaeology` · `world-events` · `eras` · `reading-orders`

- **`press-archaeology`** is where a wing stops being a list and starts being a
  reading. Hold it to 3-8 surviving facts, not thirty.
- **`world-events` only runs** if this author extends the span the catalogue
  covers, or a decade the author publishes in is empty. Most authors should
  trigger none: a global event renders on every timeline, so its cost scales
  with the catalogue while its value does not.
- **`eras` and `reading-orders` share one principle with `where-to-start`:
  received, not invented.** An era or an entry path with no source outside this
  repo is our opinion in a serif font. Fewer, or none, beats coined.

**Gate:** validator green, all four merged into the stage branch, and
`event_density.py` re-run if `world-events` ran.

### Stage 4 - Franchise-level judgement (sequential: both write `franchise.yaml`)
**`event-resonance`, then `where-to-start`.** Never together.

`event-resonance` decides which global events actually reached *this* author. The
engine already filters to the authors' lifetimes, which is arithmetic; the agent
rules on the residue. Most wings should end with fewer global events than they
started with.

`where-to-start` then writes entry paths, and it needs stage 3's orders to point
at, which is why it follows rather than leads.

**Gate:** validator green, and every `globalEvents` and path id resolves.

### Stage 5 - Spoiler audit (`spoiler-audit`, alone)
**After all prose exists, before translation.** Translation copies prose, so a
spoiler fixed afterwards must be fixed twice in two languages and the second fix
is the one that gets forgotten. It runs alone because it is cross-cutting.

Know the engine's real shape: **`spoilerAfter` works only on events, author
`lifeEvents` and character `appearsIn`.** Synopses, `connections`, character
`description`/`aka`, and order and path prose are ungated and ship to every
visitor. In those fields rewriting is not the preferred option, it is the only
one. The validator now rejects a boundary the engine cannot honour, because one
written onto a work used to validate green and protect nothing.

**Gate:** validator green. **When in doubt this stage redacts** and says so. A
false negative spoils a reader permanently; a false positive is merely annoying.
But respect the cost of over-redaction: a reader who meets a shield over
back-cover copy learns the shields are noise and clicks through on reflex.

### Stage 6 - Artefacts (parallel: 2 agents, different files)
`visual-metadata` · `editions`

Both run **after the work list and all prose are final**, because they annotate
works. Read stage 2's handoff: newly added works are exactly what gets missed.

Non-negotiables, each already the cause of a real error: pass `?default=false` on
OpenLibrary **ISBN** lookups (a blank placeholder returns HTTP 200; this does not
apply to `/b/id/` URLs); **look at every image**, because retailer-watermarked
scrapes pass every HTTP check; check ISBN prefixes (`978-85`/`978-65` are
Brazilian, and OpenLibrary merges pt-BR and pt-PT under one work record).

**Expect low coverage outside the anglophone canon and do not pad it.** An empty
slot renders as a designed typographic tile; a wrong cover is a legal problem and
a lie about the edition.

**Gate:** validator green, every image URL fetched and confirmed to be real.

### Stage 7 - Translation (`translation`, one agent per locale)
**Last, because it copies whatever the earlier stages settled on.**

Overlays carry **prose only**: never ids, never `isbn13`, never `language`,
never a `title` in `works.yaml`/`editions.yaml`, and never a `startHere` path's
`workIds`, `orderId` or `fit`. Those are structure. Copying nested overlay values
over the base once destroyed exactly that: Portuguese life events lost their
dates and vanished from the timeline entirely, and every entry path lost its
target so the wizard recommended nothing.

**Gate:** `i18n_coverage.py` shows **no regression against the prep number**. A
stage that adds prose and leaves a locale partial has shipped a regression.

### Stage 8 - Critic (`wing-audit`)
The final pass, and the only one that looks at the seams. What is missing, stale
or quietly wrong across the whole wing, plus the content types no other skill
owns (`theme.yaml`, `achievements.yaml`, capability declarations).

Its output is the **next round of work**, routed to the owning skill. It does not
do everyone's job.

### Stage 9 - Integration and merge
**Do this yourself. Do not delegate it.**

1. Merge every stage branch in pipeline order into one integration branch.
   **Re-read every branch tip at this point; do not trust the merge you did
   when the agent said it was finished.** An agent that has reported done and
   gone idle can still commit afterwards - reacting to another agent's finding,
   or tidying its own handoff. On one run two agents each pushed a further
   commit after their completion notice, and one of them carried 17 lines of
   real `editions.yaml` content, not just a handoff note. Merging on the
   completion signal alone silently drops that work, and nothing downstream
   fails. `git merge-base --is-ancestor <branch> <integration>` on every stage
   branch, immediately before the final validation, is the check.
2. `validate.py`, `i18n_coverage.py`, `event_density.py` - clean, no regression.
3. **Build the app against the merged content and run its suite.** The content
   validator cannot catch an app-side break, and twice it has not.
4. **Open the rendered page in every locale.** Four separate i18n bugs shipped
   with green CI while the non-default locale was visibly wrong. This step is the
   only one that would have caught any of them.
5. Delete `.orrery/`, then open the PRs.

## Verifying the agents, not just the content

Green CI means well-formed YAML. It does not mean the content is true. All of
these passed every check:

- prose that validated but never reached the reader, because the loader did not
  merge that shape
- a coverage script reporting 48/48 while five franchises were visibly English,
  then later 52/52 while six order names were untranslated
- a `spoilerAfter` on a work: accepted, ignored, protecting nothing
- `displayFace` and `signature` values outside the app's curated sets, falling
  back silently so five wings render a look nobody chose
- an agent reporting success on a scripted edit that had silently no-op'd

So **check artefacts, not reports.** Fetch the URL. Open the image. Read the
translated line. Re-derive the number with the repo's own scripts. An agent's
summary of its own work is a claim, not evidence.

And **treat a suspiciously complete number as a reason to look harder.** A wing
reporting 100% on everything has usually hidden its awkward cases.

## What comes back to the curator

Collect `openQuestions` from every handoff into one list rather than burying them
across nine PR bodies:

- **ordering changes** - a corrected date that reorders the derived order
- **naming and grouping** - a thread that could carry two different `subseries`
- **scope** - anthologies, secondary authorship, unfinished or unpublished works
- **rights judgement calls** - anywhere the rules point two ways
- **anything an agent flagged as its own weakest decision.** Agents that name
  their weak points are doing the job right; never quietly ratify those.

## Done means

The bibliography is verified against primary sources and its gaps documented
rather than invisible. The aura is sparse, dated and sourced. Eras and entry
paths are received rather than coined. Spoilers are bounded with the asymmetry
respected. Imagery is licensed and credited, or honestly absent. Every locale is
at full coverage and renders correctly. The app builds and its tests pass against
the merged content. And the curator has one short list of decisions that were
genuinely theirs to make.

**The honest artefact of a complete author includes the covers that do not exist,
the dates the record will not settle, and the archives that would not open.**
