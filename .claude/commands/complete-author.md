---
description: Take one author from nothing (or from partial) to a complete, verified, translated, illustrated wing by running the whole agent pipeline in dependency order.
argument-hint: <author or franchise> [--slug <slug>] [--from <stage>]
---

# /complete-author

Complete **$ARGUMENTS** as an Orrery wing: researched, verified, enriched,
illustrated, spoiler-safe, translated, and merged.

This is the drill. Each stage is an agent with its own skill file, and those
skill files are the source of truth for *how* the work is done. This command's
job is the part no single agent can see: **what order they run in, what they
hand each other, and what has to be true before the next one starts.**

## The one rule that matters most

**Stages that write the same file must not run in parallel.**

This was learned the expensive way. Completeness and visual-metadata were once
run concurrently on the same `works.yaml`; both branched from the same base, both
edited the same lines, and the naive merge would have shipped covers for only the
pre-audit works while silently looking complete. Every parallel group below is
parallel *because its members touch different files*. If you add a stage, check
its file footprint before adding it to a group.

## Prep

1. **Resolve the slug.** `content/franchises/<slug>/`. Reuse the existing slug if
   the franchise exists; otherwise lowercase-hyphenated, no accents (`joao-tordo`,
   not `joão-tordo`). Author ids follow the same rule.
2. **Establish the starting state.** New wing, or existing one being completed?
   Run `python scripts/validate.py` and `python scripts/i18n_coverage.py` now and
   keep the numbers: every later claim of progress is measured against them.
3. **One worktree per agent**, all branched from the same base:
   `git worktree add ../wt-<slug>-<stage> -b <slug>/<stage> main`
   Agents in the same parallel group work simultaneously; agents in different
   stages inherit the previous stage's merged branch.
4. **Read `docs/SCHEMA.md`.** All of it. It is the contract every stage writes to.

## The pipeline

### Stage 1 - Research (`franchise-research`)

Skip only if the franchise bundle already exists.

One agent produces the whole bundle: author profile and `lifeEvents`,
bibliography, eras, franchise events, reading orders, and where the franchise
earns them, characters, connections and `startHere` paths.

**Gate:** `python scripts/validate.py` green, and the capability set is a
deliberate choice rather than an accident. A franchise with no real connections
should have connections **off**; the fewer-layers case is a feature.

### Stage 2 - Completeness (`completeness-auditor`)

**Must run before anything that annotates works.** It changes how many works
exist, and every later stage keys off that list.

Audit the bibliography against authoritative sources: the author's official
bibliography, national library catalogues, the publisher's own catalogue,
OpenLibrary and Wikidata for dates. Find missing works, wrong years, inconsistent
`canonTier`, missing `subseries`, and missing `withAuthorIds`.

**Language follows the author.** For a non-anglophone writer the publisher's
catalogue and the national library are the standard, and an English-only sweep
will report a thin bibliography that is simply wrong.

**Gate:** validate green, and **the work count is final**. Everything downstream
assumes this list is stable. A late-arriving work costs a re-run of stages 4-6.

### Stage 3 - Enrichment (parallel: 3 agents, different files)

| Agent | Writes |
|---|---|
| `press-archaeology` | `content/authors/<id>.yaml`, `content/franchises/<slug>/events.yaml` |
| `world-events` | `content/events/global.yaml` |
| `event-resonance` | `content/franchises/<slug>/franchise.yaml` (`globalEvents`) |
| connections and characters pass (`franchise-research`) | `content/franchises/<slug>/{characters,connections}.yaml` |

**`press-archaeology` is where a wing stops being a list and starts being a
reading.** It reads contemporary press, interviews, obituaries and prize
coverage for the dated, sourced facts a bibliography cannot hold, and it is the
only stage that systematically hunts **corrections** to received wisdom. Give it
the aura density budget and hold it to 3-8 surviving facts, not thirty.

**`world-events` only runs if this author extends the span the catalogue covers**,
or if the density report shows an empty decade the author publishes in. Its bar
is deliberately higher than every other stage: a global event renders on *every*
franchise timeline, so its cost scales with the catalogue and its value does not.
Most authors should trigger no global events at all.

**Gate:** validate green. Merge all three into the stage branch before continuing,
and re-run `python scripts/event_density.py` if `world-events` ran.

### Stage 4 - Spoiler audit (`spoiler-audit`)

**Runs after enrichment, before translation.** Enrichment adds prose that can
spoil; translation copies prose, so a spoiler fixed after translation has to be
fixed twice, in two languages, and the second fix is the one that gets forgotten.

Audit everything: synopses, events, `lifeEvents`, characters, connections,
`startHere`, subseries descriptions. Prefer **rewriting** a sentence so it needs
no boundary over redacting it; reach for `spoilerAfter` only when the fact cannot
be stated safely and is genuinely worth stating.

**Gate:** validate green. **When in doubt this stage redacts**, and says so, so a
curator can loosen it later. A false negative here spoils a reader permanently
and cannot be undone; a false positive is merely annoying. The asymmetry decides
every tie.

### Stage 5 - Visual metadata (`visual-metadata`)

**Runs after the work list and all prose are final**, because it annotates works
and would otherwise collide.

Author portrait, franchise header, and a cover per work. Source ranking, rights
discipline and the credit fields are in the skill; do not improvise them.

Non-negotiable, because each has already caused a real error:
- pass `?default=false` on OpenLibrary cover lookups (it returns HTTP 200 with a
  blank placeholder otherwise)
- **look at every image** - retailer-watermarked scrapes pass every HTTP check
- check the ISBN prefix (`978-85` / `978-65` are Brazilian; OpenLibrary merges
  pt-BR and pt-PT under one work record)

**Expect low coverage outside the anglophone canon and do not pad it.** An empty
slot renders as a designed typographic tile; a wrong or unlicensed cover is a
legal problem and a lie about the edition. Report the true number.

**Gate:** validate green, every URL fetched and confirmed to be a real image.

### Stage 6 - Translation

**Last, because it copies whatever the earlier stages settled on.**

One agent per locale, writing overlays into `content/i18n/<locale>/`. Overlays
carry **prose only**: never ids, never `isbn13`, never `language`, and never a
`title` in `works.yaml` or `editions.yaml` (published titles are edition data,
not translation, and many books keep their original title in a given market).

For pt-PT specifically: **European Portuguese, not Brazilian.** No progressive
gerund constructions, and the vocabulary discriminators are the tell (*banda
desenhada* not *quadrinhos*, *argumento* not *roteiro*). Where an entry concerns
Portugal, it should read as though written by someone who was there.

**Gate:** `python scripts/i18n_coverage.py` reports **no regression against the
number recorded in prep**. A stage that adds prose and leaves the locale partial
has shipped a regression, not a feature.

### Stage 7 - Integration and merge

Do this yourself. Do not delegate it.

1. Merge every stage branch into one integration branch **in pipeline order**.
2. `python scripts/validate.py`, `python scripts/i18n_coverage.py`,
   `python scripts/event_density.py` - all clean, no coverage regression.
3. Build the app against the merged content and run its test suite. The content
   repo's validator cannot catch an app-side break.
4. Open one PR per stage (reviewable), or one PR for the wing (mergeable). Say
   which you chose and why.

## Verifying the agents, not just the content

Green CI means the YAML is well-formed. It does not mean the content is true, and
several real failures here passed every check:

- prose that validated but never reached the reader, because the loader did not
  merge that shape
- a coverage script that counted top-level fields only and reported 48/48 while
  five franchises were visibly English
- an agent reporting success on a change that silently no-op'd

So: **spot-check the actual output, not the report.** Read a few translated
entries for register. Fetch two or three cover URLs. Check one sourced fact
against its source. An agent's summary of its own work is a claim, not evidence.

## What comes back to the curator

Some things are not the pipeline's to decide. Collect them and put them in one
place rather than burying them across seven PR bodies:

- **Ordering changes** - a corrected first-publication date that reorders the
  derived reading order
- **Naming and grouping calls** - a thread that could carry two different
  `subseries` labels
- **Scope calls** - anthology contributions, co-authored books where the author
  is secondary, unfinished or unpublished works
- **Rights judgement calls** - anywhere the rules point two ways
- **Anything an agent flagged as its own weakest decision.** Agents that name
  their weak points are doing the job right; do not quietly ratify those.

## Done means

The wing is complete when: the bibliography is verified against primary sources
and its gaps are documented rather than invisible; the aura is sparse, dated and
sourced; spoilers are bounded with the asymmetry respected; imagery is licensed
and credited or honestly absent; every locale is at full coverage; the app builds
and its tests pass against the merged content; and the curator has a single short
list of decisions that were genuinely theirs to make.

**A wing that reports 100% on everything has almost certainly hidden something.**
The honest artefact of a complete author includes the covers that do not exist,
the dates the record will not settle, and the archives that would not open.
