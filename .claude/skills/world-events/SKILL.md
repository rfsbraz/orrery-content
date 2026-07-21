---
name: world-events
description: Curate the shared global aura layer - the world, cultural, and industry events that shaped how fiction was written and read - keeping the timeline sparse and impact-weighted. Use when adding or re-grading entries in content/events/global.yaml, or when a new franchise extends the era the catalogue covers.
---

# world-events

Curate `content/events/global.yaml`: the events that belong to **no single
author** but changed the weather every author was writing in.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md) - prime
directives, comment policy, gates and trap registry apply and are not repeated
here. Read `docs/SCHEMA.md` (events) first. This skill narrows the aura
editorial standard (CURATION §6) for the global layer, where the bar is much
higher.

## The sanctuary rule (no exceptions, including for this stage)

**A content YAML file is a sanctuary for the author and the work.** A comment in
one explains the data sitting next to it: the source a value came from, why this
value and not the rival one, why a slot is deliberately empty and what was
checked to establish that, a trap the next reader would otherwise fall into.
That is the whole permitted range.

A comment never mentions the curating. Not the stage, agent, pass, run, budget
or tooling. Not addressing anyone ("a curator call", "left to the curator",
"flag if a future pass finds..."). Not narrating the research instead of the
data ("not yet a finished audit", "first built on one source, since checked
against two", "that remains open") - collapse those to what is known, in the
present tense: "publisher and year are corroborated by two independent sources;
the 2018 title rests on one." The weakness survives the edit. The diary does
not.

The test: **would this comment still be true and useful if the pipeline had
never existed and a human had typed the file by hand?** Process belongs in the
handoff, the PR body and git history. `docs/CURATION.md` §2 is the long form;
`validate.py` scans content comments and warns.

## Why the bar is higher here

A franchise event appears on one timeline. **A global event appears on every
timeline in the catalogue** - six today, more with every franchise added. Its
cost scales with the size of the site; its value does not. So the question is
never "was this historically important?" It is:

> **Did this change what fiction was about, how it was written, or how it
> reached readers - across authors, not just one?**

The Second World War passes: it reshaped what a generation of novelists could
write about, and the books sit visibly on either side of it. A general
election, a moon landing, a famous person's death: almost never, unless the
books answer them.

## The two tests

**1. The narrative test.** An event earns a slot only if a reader, standing at
that point in the walk, would read the surrounding books differently for
knowing it. Ask what specifically changed:

- **What fiction was about** - a war, an occupation, a pandemic, a collapse
  that becomes the subject or the shadow of the books written after it.
- **What could be published** - censorship regimes, obscenity trials, the
  loosening or tightening of what a novel was allowed to say.
- **How books reached readers** - the paperback revolution, mass-market
  distribution, the chain bookshop, ebooks and self-publishing, audiobooks,
  the collapse of the midlist. These reshape careers and catalogues, and are
  chronically under-represented compared to wars.
- **What a genre meant** - the moment a genre was invented, legitimised,
  ghettoised, or absorbed into the mainstream.

**2. The crowding test.** Even a qualifying event can be wrong to add. Before
committing, check the density budget below. If the decade is already full, the
new event must be **better than the weakest one already there** - in which case
say so and propose replacing it, rather than stacking.

## The density budget

Measured against the span the catalogue actually covers (`works.yaml` across
all franchises - currently 1920-2025, eleven decades).

| Rule | Budget |
|---|---|
| Global events per decade | **at most 3**, target 1-2 |
| `impact: high` globally | **at most one per 25 years** |
| Expected mix | roughly 10-20% high, the rest med and low |

**`impact: high` on a global event is expensive.** The app renders high-impact
events as full-bleed interruptions that break the page on every franchise. A
reader walking Discworld should not cross a full-width plate for an event with
no Discworld book anywhere near it. When in doubt grade **down**: `med` for
"explains the shelf", `low` for "texture of the times".

The file currently sits inside the budget: 16 entries graded 2 high (the
Second World War, the COVID-19 pandemic), 9 med and 5 low, with texture in
every decade the catalogue spans. Measure the live distribution before grading
against it - an earlier all-high state is why the budget exists.

## What does not qualify

Cut on sight, however important historically:

- elections, coups, and political milestones with no literary consequence
- disasters and atrocities that no book in the catalogue answers
- sport, celebrity, royal events (a coronation is not a narrative shift)
- technology news that did not change reading or publishing
- anything already covered by a franchise event, better and closer to home
- anything you would justify as "important context" rather than "changes the
  reading"

If the strongest argument is "a reader might find it interesting," it belongs
in a search engine, not the aura.

## Scope: global or franchise?

`reach: global` means **every franchise carries it**. Use it only when the
event is genuinely author-agnostic and touches several catalogues. If the
resonance is specific - a rupture one author wrote directly about - it belongs
in that franchise's `events.yaml` instead, where it can be sharper and safely
higher-impact.

A useful check: name three franchises in the catalogue it changes the reading
for. If you cannot, it is not global.

## Coverage, not just pruning

The point is a timeline that breathes, not an empty one. After pruning, look
for **under-covered decades** the catalogue actually spans, and for the
under-represented categories above (publishing and distribution shifts,
censorship, genre legitimation). A decade with several franchises publishing
and no global texture at all is a gap worth filling with one or two `low` or
`med` entries.

## Hard rules

- **`global.yaml` is a shared file with parallel PRs.** Keep your diff
  **append-only** where possible, check for an existing entry before adding,
  and never reorder or reformat entries you are not changing. Re-grading an
  existing `impact` is the one legitimate in-place edit; call it out explicitly.
- **Stable ids are permanent** - `<slug>-<year>` - because translations and any
  future references key off them. Re-grading impact never changes an id.
- **Neutral, franchise-agnostic prose.** A global description must read
  correctly under every author's page. No "as King later wrote" - that is a
  franchise event.
- **Spoiler-check.** A global event can spoil; use `spoilerAfter` where it
  applies - the `spoiler-audit` skill owns the doctrine.
- **Translations exist.** Adding or renaming an entry leaves the locale
  overlays incomplete (CURATION §3); note the gap in the PR for the
  `translation` stage.

## Process

**Measure first**: read `global.yaml` for the current distribution by decade
and impact, and `python scripts/i18n_coverage.py` for translation state.
**Re-grade** existing entries against the budget before adding anything. Then
identify gap decades and under-represented categories, **draft candidates**
with a one-sentence narrative-test answer each (a weak sentence drops the
candidate), apply the crowding test per decade, and emit the YAML.

## Done means

A PR whose body states: the before/after distribution by decade and by impact,
each added event with its one-sentence narrative justification, each re-graded
event with the reason, candidates you **rejected** and why (this is as useful
as what you added), and the translation-coverage gap your change creates.
