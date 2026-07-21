---
name: franchise-research
description: Scaffold a new franchise wing for Orrery - scope the franchise, slug the works, create the global author entities, draft the bibliography and series structure, map characters and connections, and set the theme, leaving every other layer as an honestly-marked thin pass for its specialist skill. Use only when content/franchises/<slug>/ does not exist yet or its structure is being redrawn; any other work on an existing wing belongs to a specialist skill.
---

# franchise-research (the scaffold stage)

The first stage of `/author` (`.claude/commands/author.md`). It creates a new
wing's structure, or redraws one, and runs alone because it writes everything.
It runs rarely: if the wing exists and its structure is sound, the work
belongs to a specialist skill, not here.

Read first: **`docs/SCHEMA.md`** (the data contract; every example below is
abbreviated and SCHEMA.md is authoritative) and **`docs/CURATION.md`** (the
working contract: fabrication, permanent ids, received not invented, YAML
mechanics, gates, verification, and the aura editorial standard in its §6).
If unfamiliar with the app, also `docs/CONCEPT.md` §4, §4a and §9.

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

## The framework mindset

Orrery is a framework: every advanced layer is optional, and the app activates
capabilities per franchise from what the data provides (the capabilities table
in SCHEMA.md). Judge which layers this franchise *earns* - a sprawling
multiverse earns characters, connections and a rich aura; a sparse or
non-English author may ship works plus a thin aura and nothing else, and that
is a complete, correct wing. Empty is a supported state (CURATION.md §1).
State in your handoff which capabilities the scaffold activates and why.

## Scoping the franchise

**A wing is an author's complete published body of work - always** (curator
ruling, 2026-07-21). The derived main order spans everything they published;
a shared universe or series lives INSIDE the wing as `subseries`, connections
and characters, never as the wing's boundary. Do not scope a wing to one
universe (the Cosmere) or one series (The Wheel of Time) even when it is what
the author is famous for - that is what `subseries` is for, and the Stephen
King wing (95 works, The Dark Tower as a thread) is the model. `kind: author`
is therefore the norm; `shared-universe`/`series` remain only for a wing that
genuinely has no single author to span.

Two corollaries:

- **A continued universe belongs to its originating author's wing.** The
  Wheel of Time is Robert Jordan's wing; the Sanderson-finished volumes stay
  there as `withAuthorIds` works. A collaborator's own wing never duplicates
  them - a work lives in exactly one franchise - so cross-reference from the
  collaborator's bio/connections instead.
- **A cross-author collaboration** (Good Omens) is included in the wing with
  `withAuthorIds` and `authorRole` per the multi-author rules below.

Also confirm the `canonTier` conventions (what counts as core vs extended vs
apocrypha - completionists care). Pick `<franchise-slug>` deliberately
(lowercase, hyphenated, accents stripped); ids are permanent - which also
means an existing universe-scoped wing being widened to its author KEEPS its
slug and every existing work id, and new works take the same prefix.

## Work ids: slug the works before writing anything else

Every file cross-references work ids (`<franchise-slug>/<work-slug>`), and ids
are immutable once merged - user progress references them. Draft the complete
`works.yaml` id list first, sanity-check the slugs (drop leading articles only
when the community does: `the-stand` keeps its "the"; be consistent within the
franchise), and only then write anything that points at them. Renaming a slug
halfway through poisons every file already written.

## The first-draft bibliography

Completeness beats depth: the franchise's default order is
publication-chronological over ALL published works and is *derived* from
`works.yaml`, so a missing work is a hole in the spine, while an entry with
just id/title/authorIds/published/canonTier and a one-line synopsis is fine.
Novels, collections, novellas, relevant nonfiction - all of it, tiered
honestly. Do not author the default order by hand; `orders.yaml` holds only
additional orders. Leave `externalIds` empty - the enrichment bot
(`scripts/enrich.py`) fills OpenLibrary ids and flags uncertain matches.
This is a first draft, and say so: the **`completeness-auditor`** skill will
verify it against primary sources and close it - your job is a spine it can
audit, with gaps flagged rather than papered over.

## Author entities

Authors are **global entities** in `content/authors/<slug>.yaml`, so the same
person resolves across franchises and name collisions. Franchises and works
reference `authorIds` / `withAuthorIds`; author-life events live on the author
entity (`lifeEvents`), never in the franchise's `events.yaml`.

- **Pen names**: record `pseudonyms` on the author and `publishedAs` on each
  work published under one. Pen-name works stay in the author's franchise and
  the default order; a pen name only gets its own franchise if it is a
  genuinely distinct brand (curator's call). Pen-name lore (a staged death, a
  reveal) is an event, not a data hack.
- **Multi-author volumes: record the relationship, never imply authorship.** A
  book containing one story by this author is not a book by this author, and
  bare `authorIds` silently drops other people's books into the derived order.
  Use `authorRole` (`author | co-author | contributor | editor`), name the
  piece in `contributionTitle`, and tier a contributor entry `apocrypha`. Same
  for books where this author wrote only an introduction.

## Series structure: be authoritative

`subseries` is a factual question with a findable answer, and one of the few
fields a reader notices being wrong. **Settle it - this is your call, not the
curator's**: publisher's own numbering first, then the author's stated
grouping, then settled community consensus. Emit the decision, record the
evidence in a `note:`, and escalate only when sources actively contradict each
other (then quote them). Two traps:

- **A recurring character is not a series.** Separately titled, separately
  marketed sequences that share a protagonist stay separate; where a thread
  genuinely continues under a new name, say so in a `note:` on the hinge work.
- **A collection containing a series novella is not part of the series.**
  Leave its `subseries` null; let a connection or character entry carry the
  link.

## Characters and connections

This skill owns them - no specialist skill exists for this layer.

- **Characters are connective tissue, not a wiki.** Add `characters.yaml` only
  for figures whose recurrence across works is part of how the franchise hangs
  together. An appearance whose *existence* is a reveal gets `spoilerAfter` on
  that appearance.
- **Connections are declared on the later work**, pointing back at the earlier
  one (the later work is the one whose reading is enriched); the app renders
  the edge both ways. Do not duplicate what `subseries` already threads -
  connections are for crossovers, sequels across subseries, and shared
  cosmology.
- **Chase the universe connections properly.** This is a headline feature:
  `connections` on works, `characters.yaml` with appearance lists,
  inter-franchise links where an author's universes touch. Gate reveals with
  `spoilerAfter` rather than dropping them; if the franchise genuinely has
  none, say so in the handoff instead of leaving it silently empty.

## Theme scaffolding

`theme.yaml`'s `palette` is free; **`displayFace` and `signature` are closed
sets**: `fraunces | spectral | sourceSerif` and `beam | thread | rule | none`.
Anything else is accepted, validated, and then **silently swapped** for
`fraunces`/`thread` at render - an invented value costs the wing its look
without failing anything (five of the first six wings shipped names that do
not exist; `validate.py` warns now). Pick from the implemented set or propose
a new value as an app change in the PR. Follow CONCEPT §6: palette + one
display face + one signature element, readability first, no genre costume.

## Scaffolding the other layers

A first thin pass at the remaining layers is allowed as scaffolding, but each
must be honestly marked for the specialist skill that owns it - a scaffold
slot that looks finished is worse than an empty one:

- **Bibliography closure** - `completeness-auditor` verifies and finalises the
  work list; flag your known gaps for it.
- **Aura and life events** - `press-archaeology` (the editorial bar is
  CURATION.md §6). Scaffold only well-known, sourced anchors.
- **Shared world events** - `world-events` owns `events/global.yaml`;
  **which of them reach this timeline** is `event-resonance`'s ruling.
- **Eras** - `eras`. Scaffold only eras you can actually source; any era whose
  label you did not receive carries `provenance: none`, which is exactly what
  triggers that skill. `eras: []` is fine.
- **Reading orders and entry paths** - `reading-orders` owns both `orders.yaml`
  and `startHere`. Scaffold only orders the publisher itself numbers and paths
  you have receipts for (a citable community recommendation); everything else
  is that skill's discovery work.
- **Achievements** - content, not app code: this wing's badges live in its
  `achievements.yaml` with ids prefixed `<slug>/`, using only the criteria
  kinds in SCHEMA.md (never invent one - propose it as an app change instead).
  Tie at least one to the aura where the franchise supports it; most wings
  correctly have none. `wing-audit` checks earnability.
- **Spoiler boundaries** - `spoiler-audit` owns `spoilerAfter` doctrine; tag
  what you know, never guess a boundary.
- **Imagery** - `visual-metadata` owns portraits, headers, covers and rights.
- **Editions and translated titles** - `editions`; never guess an ISBN, and a
  work's `title` is its original title, permanently.
- **Locales** - `translation` owns `content/i18n/`; `wing-audit` critiques
  the finished whole.

## Output schema

Abbreviated tree; full field-by-field reference in `docs/SCHEMA.md`.

```
content/
  authors/
    <author-slug>.yaml               # GLOBAL author entity: bio, pseudonyms, lifeEvents
  events/
    global.yaml                      # shared world/culture events (reach: global)
  achievements.yaml                  # global, franchise-agnostic badges
  franchises/
    <franchise-slug>/
      franchise.yaml                 # identity + features + startHere
      works.yaml                     # required; connections live on works
      eras.yaml
      events.yaml                    # franchise-specific events only
      orders.yaml                    # additional orders (default is derived)
      characters.yaml                # optional; recurring/crossover figures
      editions.yaml                  # optional; verified ISBNs only
      achievements.yaml              # optional; this wing's badges (data, not code)
      theme.yaml                     # branding preset (see CONCEPT §6)
```

**franchise.yaml**
```yaml
id: stephen-king
name: Stephen King
kind: author                       # author | shared-universe | series
description: One-line essence.
authorIds: [stephen-king]
themePreset: pulp-horror
```

**content/authors/&lt;slug&gt;.yaml** (one global file per author)
```yaml
id: stephen-king                   # global, stable; referenced by authorIds everywhere
name: Stephen King
aka: ["Steve King"]                # optional alternate names, for search
born: 1947-09-21
bio: Short factual bio, may use [[work:...|links]].
pseudonyms:
  - name: Richard Bachman
    note: When/why used; how it was revealed.
lifeEvents: []                     # author-life events; press-archaeology fills these
sources: ["https://..."]
```

**works.yaml**
```yaml
- id: stephen-king/carrie          # STABLE - never change
  title: Carrie
  authorIds: [stephen-king]
  published: 1974                  # YEAR ONLY, bare integer - never 1974-03-26
  subseries: null                  # e.g. "The Dark Tower" / "Mistborn: Era 1"
  canonTier: core                  # core | extended | apocrypha
  publishedAs: "Richard Bachman"   # optional; only when the cover name differs
  withAuthorIds: [peter-straub]    # optional; collaborator author ids (must exist)
  synopsis: Spoiler-free premise. May use [[work:...|links]].
  sources: ["https://..."]
```

**theme.yaml**
```yaml
preset: pulp-horror
palette: { bg: "#...", accent: "#...", ink: "#..." }
displayFace: fraunces              # fraunces | spectral | sourceSerif - closed set
signature: beam                    # beam | thread | rule | none - closed set
```

## Field notes

Only the lessons not already carried by CURATION.md or a specialist skill:

1. **Global vs franchise events: default to franchise.** Push an event to
   `events/global.yaml` only when it is genuinely author-agnostic AND likely
   to matter to several franchises. Check for an existing entry first; append
   at the end and never edit others' entries - parallel franchise PRs merge
   into this file, keep your diff append-only.
2. **Portugal-market awareness.** For Portuguese authors, the original
   Portuguese titles are the canonical `title` values; expect store coverage
   via Wook/Bertrand/FNAC rather than Amazon, and primary sources in
   Portuguese (publisher pages, the author's site, national press). Keep prose
   in English but never translate a title that has no published translation.
3. **`published` is a bare year** - see SCHEMA.md; the validator rejects full
   dates.

## Done means

The wing's structure exists and validates: slugs chosen deliberately, the
first-draft bibliography honest about its gaps, author entities global,
`subseries` settled with evidence, characters and connections mapped (or their
absence stated), theme drawn from the implemented sets, and every scaffolded
layer marked for its owning skill. The handoff states which capabilities the
scaffold activates, what was rejected, and what the specialists must close.
Canon is only canon after a curator merges it.
