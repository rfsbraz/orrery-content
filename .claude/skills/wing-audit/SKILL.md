---
name: wing-audit
description: Audit a completed franchise wing as a whole - the seams between layers no single agent can see, the content types no other skill owns (eras, theme, achievements, capabilities), density, staleness, and whether the reported numbers are true. Produces a prioritised findings report routed to the owning skills. Use as the final stage of /author, before a wing ships, or when a wing reports 100% on everything.
---

# wing-audit

Every other agent in this pipeline builds or checks one layer. This one asks the
question none of them can: **what is missing, stale, or quietly wrong across the
whole wing?**

Its output is not a fixed wing. Its output is **the next round of work**: a
prioritised list of findings, each routed to the skill that owns it.

Read `docs/SCHEMA.md` in full - you are auditing against the whole contract, not
one section of it. Read `.claude/commands/author.md`, because you are
its final stage and its gates are the promises you are testing. Read every skill
in `.claude/skills/`, because your job is precisely the **seams between them**
and anything you re-audit inside one of them is wasted effort.

This skill runs under `docs/CURATION.md`; the shared contract is stated there,
not repeated here.

## The principle this exists to enforce

The verification doctrine is CURATION §5: green CI proves well-formed YAML, not
true content, and artefacts outrank reports. This skill is that doctrine
applied to a whole wing at once - fetch the URL, read the rendered line,
re-derive every number with the repo's own scripts. What is wing-audit's own is
the map of where the doctrine bites: what the validator does not cover, and the
fields nobody reads.

### What the validator does not cover

Know this before you trust a green run. Verified against `scripts/validate.py`
at time of writing - **re-check it rather than trusting this list**, because the
gap is what you are hunting:

| Checked | Not checked |
|---|---|
| id prefixes, duplicates, every cross-reference | `theme.yaml` at all - the file is never opened |
| `features` keys and values | `eras[].period` format, coverage, or overlap |
| `startHere` paths, `fit` tags, order/work resolution | `globalEvents.include` / `exclude` ids |
| achievement `criteria` references | whether an achievement is *earnable* |
| enum discipline on tier, impact, scope, format | whether an image URL renders anything |
| i18n overlay ids resolve | whether prose is actually in the target language |

Anything in the right column is yours.

Two entries have since moved left and are now **warnings**, not silence:
`theme.yaml`'s `displayFace`/`signature` are checked against the values the app
implements, and every work is checked for falling outside all era spans. Warnings
are easy to scroll past - read them.

### The field nobody reads

Add one question to this audit that no validator can ask: **is anything writing
content the app never consumes?**

`coverFor()` did not read `work.images.cover` for months. The `Work` type did not
model it. So an entire curation stage - fetching, eyeballing and crediting a
cover for all 93 King works and 26 more elsewhere - produced a field that was
inert, while the app rendered a guessed ISBN URL instead. Every check was green
throughout, because inert data is well-formed data.

The check is cheap: for each content field this wing relies on, grep the app for
the code that reads it. `grep -rn "images\.cover\|images?.cover" lib/ components/`
returning nothing is the whole finding. Do this for anything newly added, and
spot-check the fields a wing leans on hardest.

## What you do not do

**You route editorial work; you do not do it.** A missing cover is not yours to
source, a mis-anchored `spoilerAfter` is not yours to re-anchor, a thin aura is
not yours to enrich. Doing another skill's job here means it gets done once,
badly, by the agent with the least context on it, and the owning skill never
learns the wing needed it.

You may fix **trivial mechanical** issues in place: a stale comment, a dangling
whitespace difference, a typo in a curator note. Anything with an editorial
judgement inside it goes into the report with an owner against it.

### Routing table

| Finding | Owner |
|---|---|
| missing or wrong work, wrong year, wrong `canonTier`, missing `subseries` / `withAuthorIds` / `authorRole` | `completeness-auditor` |
| thin or flat aura, missing dated facts, uncorrected received wisdom | `press-archaeology` |
| a shared event that should exist, or is mis-graded | `world-events` |
| a global event reaching a franchise it never touched, or missing one it did | `event-resonance` |
| unbounded reveal, mis-anchored or over-broad boundary, ungated sibling prose | `spoiler-audit` |
| missing cover / portrait / header, doubtful rights, dead image URL | `visual-metadata` |
| missing or wrong edition, ISBN, published title | the editions skill |
| an order, entry path, or `startHere` block that is wrong, stale, or missing | `reading-orders` |
| missing, partial, or wrong-register translation | the translation skill |
| eras, theme, achievements, capabilities | **you** - see below |
| the schema cannot express what the content needs | the curator |

Where a finding has no owner because no skill covers it, say so plainly. A gap
in the pipeline is a finding about the pipeline.

## 1. Cross-layer coherence

**The highest-value section. Spend most of your time here.** These are the
defects that exist *because* the work was split across agents, which means no
single agent can see them and no single validator checks for them.

The general shape: **a stage that ran after another stage invalidated its
output, and nobody re-ran the earlier one.** Check the git history for stage
order before you start - `git log --pretty='%h %ad %s' --reverse -- content/franchises/<slug>/`
tells you which stages ran and when, and any stage that ran *before* the
completeness audit is suspect by default.

Work through these deliberately:

**Works added late and never annotated.** The canonical failure: a completeness
audit adds works, and they land with no cover, no edition, no translation, and
were never spoiler-audited. This exact gap was live in this repo - 23 works
reached main unaudited. Take the set of works added by the last completeness
commit and check each one against every downstream layer. A work that exists in
`works.yaml` and nowhere else is not complete; it is a hole with a title.

**An order that predates the works it claims to cover.** A rationale calling
itself complete, an `orderedWorkIds` list assembled before the bibliography was
final, a `debated` note arguing about a placement that a date correction has
since settled. Compare the order's last-touched commit against `works.yaml`'s.

**Eras that no longer span the works.** A date correction moves a work outside
every era, or a new late work lands past the final era's close. Re-derive it:
parse every `period` and check where every `published` year lands (section 2
says which gaps count as findings).

**References that survived a rename.** `appearsIn[].workId`, `connections`,
`startHere.workIds`, `orderedWorkIds`, achievement `eraId` / `orderId`. The
validator catches a reference to an id that *does not exist*. It cannot catch a
reference that still resolves but now points at the wrong thing, which is what
happens when an id is reused rather than retired.

**`startHere` drift.** A path pointing at an order that has since been rewritten,
or a curated `workIds` list that no longer represents the wing after 20 works
were added. The wizard is the first thing a new reader touches; a stale path
there is the most expensive stale thing in the wing.

**Capability versus reality.** `river: auto` on a franchise with one event
lights up a River view with nothing in it. Every auto-activated capability
should be checked against the data that activates it, not just the flag.

**Prose that contradicts prose.** An era description naming a work the
completeness audit re-dated into a different era. A franchise description
claiming a scope the bibliography does not have. A `note:` on a work that
argues against a decision the wing has since taken.

**Translations that mirror a rewritten string.** Overlays merge field by field,
so an English rewrite that was not mirrored leaves the old string live for the
locale reader. Coverage counts entries, not freshness: an overlay can be 100%
covered and 100% stale. Diff the last prose commit against the last overlay
commit and spot-read the entries in between.

## 2. Content types with no other owner

Nobody else audits these. Give each a real pass.

### eras.yaml

- **Does every `period` parse?** The forms in use are `1974-1979`, `1980s`,
  `2020-present`. Nothing validates this, so a typo renders as an unlabelled
  band or breaks the strata walk silently.
- **Do works land where the eras claim them?** Re-derive it, do not eyeball it.
  Gaps between spans are not defects by default: the eras skill's provenance
  rule outranks tidiness, and a received periodisation is allowed to leave
  years uncovered. A gap is a finding only when a received era covers the year
  and the YAML does not, or when boundary-tightening orphaned a work outside
  every span (the validator warns on this - read the warnings). Never route
  "close the gap by tiling". Overlaps are still defects: two eras claiming the
  same year makes an ambiguous strata membership and an `era_reader`
  achievement that counts differently than it reads.
- **Do the boundaries mean anything editorially?** This is the judgement call and
  the one most often skipped. Eras are the wing's argument about how a body of
  work developed. Six eras that each start on a round decade are usually decades
  in costume, not periods - the tell is a description that says what got
  published rather than what changed. A real boundary can be named: a death, a
  sobriety, an accident, a form abandoned, a market that moved.
- **Does the era `title` earn its place?** It is rendered prose and it is
  translated, so a flat one costs twice.

### theme.yaml

Unvalidated end to end. `scripts/validate.py` never opens this file, so every
rule below is enforced by nothing but this audit.

- **Is `displayFace` in the app's curated set?** SCHEMA lists `fraunces`,
  `spectral`, `sourceSerif`. An unknown value does not error - the app falls
  back to the default, so the wing silently renders in a face nobody chose while
  the YAML documents an intent that never shipped. **Read the app's actual font
  registry, not just SCHEMA**, and if a franchise genuinely needs a new face,
  that is an app-side decision to propose, not a string to invent.
- **Is `signature` one of `beam`, `thread`, `rule`, `none`?** Same failure mode,
  same silence.
- **Does the palette suit *this* author?** All five keys (`bg`, `surface`, `ink`,
  `muted`, `accent`) present, and the result not simply another franchise's look
  with the accent hue rotated. Check the contrast between `ink` and `bg` and
  between `muted` and `surface` - the readability floor is non-negotiable and
  `muted` on `surface` is where it usually fails.
- **Is it a design system or genre costume?** One accent used sparingly, one
  display face, one signature. Three signature moves is none.

### achievements.yaml

- **Does every criteria reference resolve?** The validator does check
  `franchiseId`, `orderId` and `eraId`, so lean on it - but re-read the criteria
  against what it *means*, which the validator cannot.
- **Is any badge unearnable?** The real risk. `franchise_complete` on a wing
  that includes anthology contributions demands a reader finish books the author
  did not write. `era_reader` with `count: 5` against an era holding four works
  can never fire. `order_complete` against an order that grew after the badge
  was written moves the goalposts on readers mid-progress. Check every count
  against the live data.
- **Should this franchise have any at all?** Achievements are opt-in and most
  wings here have none. Absence is a legitimate state. Ask instead whether this
  wing has something *specific* worth marking - a real era, a real curated order,
  a genuinely hard completion. A wing whose only badges are "read 10 of these"
  and "read all of these" has generic badges, and generic badges are worse than
  none because they teach the reader the layer is decoration.
- **Is the id prefixed with the franchise slug?** Validated, but check the
  `description` says which franchise too - badges render in a shared cabinet.

### franchise.yaml capabilities

- **Is every `on` and `off` deliberate?** An explicit value overrides the app's
  detection, so it is a standing claim that must stay true. An `off` set while a
  layer was thin, left in place after the layer filled, is a feature the wing
  built and then hid from itself.
- **Has a franchise silently gained a half-empty feature?** The inverse and the
  more common one. `auto` means the capability lights up the moment the data
  appears, so a single connection added by an enrichment pass switches on a
  connections map with one edge in it, and a wing with two events gets a River
  view that is mostly empty sky. **The question is never "does the data exist"
  but "is there enough of it that the feature is worth entering".** Where the
  answer is no, the fix is either to enrich the layer (route it) or to set the
  capability `off` with a comment saying why and what would turn it back on.
- **Is `globalEvents` doing its job?** Nothing validates the `include` / `exclude`
  ids, and the absence of the block entirely is invisible. The default filter is
  arithmetic - the authors' lifetimes - so any global event inside that window
  reaches this wing whether or not it ever reached the author. Read the global
  list against the author and ask, per event, whether it belongs. Route the
  answers to `event-resonance`; the finding that the block was never written at
  all is yours.

## 3. Density and proportion

Re-derive, do not read a previous report.

- **`python scripts/event_density.py`.** The global layer against its budget:
  per-decade counts, the high-impact budget, and empty decades the catalogue
  publishes into. An empty decade is a `world-events` finding; an over-budget
  one is too.
- **Is the aura sparse and load-bearing?** Grade the wing's own events against
  the aura standard (CURATION §6): high recolors the text, med explains the
  shelf, low is texture of the times, fails all three does not ship. Count how
  many are `low` - a timeline that is mostly texture is a timeline nobody reads
  twice.
- **Is the wing proportionate to its size?** Compare event count against work
  count and span across the franchises in the repo. The largest wing having the
  thinnest aura is a finding, and it is the kind that only shows up when you look
  at all six at once.
- **Are spoiler boundaries neither absent nor blanketing?** Zero boundaries on a
  wing full of twist-driven fiction means the audit did not happen. Boundaries on
  most of the timeline means readers will click through them on reflex and be
  unprotected when a real one arrives. Both are `spoiler-audit` findings; the
  distribution is yours to measure.
- **Are covers, editions and translations proportionate to what exists?** Not to
  100 - to what the record actually holds. See the next section.

## 4. The honesty audit

**A wing reporting 100% on everything has usually hidden its awkward cases.**
CURATION §5 makes a suspicious number a reason to look harder, and §7 defines
the honest artefact; this is where the wing is held to both. If the wing's
reports name no missing covers, no unsettled dates, no archives that refused,
either it is unusually lucky or somebody padded, and padding is the more common
explanation.

So: **any suspiciously complete number gets a manual spot-check.** Not a re-read
of the number - a look at the artefact behind three or four random rows of it.

- A locale at full coverage: read three translated entries and confirm they are
  in the target language, in the right register, and current with the base prose.
- A cover on nearly every work: fetch several and **look at them**. A watermark
  passes every HTTP check ever written, and this repo has already shipped a pass
  where 4 of 6 available covers were retailer scrapes with the retailer's mark
  burned into the pixels.
- Every reference resolving: pick two and confirm they resolve to the *right*
  thing.
- A completeness audit reporting the bibliography closed: check two works the
  audit did not mention against a source it did not use.

Then require the reverse of a clean report. The wing's findings must name **what
is genuinely absent**, and classify every absence per CURATION §7: **absent** (a
finding, with an owner) or **not applicable** (not a deficiency). Do not confuse
them - the framework is opt-in per franchise and a sparse wing is a first-class
citizen. A franchise with no crossovers has no `connections` and is *complete*;
reporting it as 0% connections coverage invents a gap and invites somebody to
fabricate edges to close it. A Portuguese literary novelist with 20% cover
coverage has hit the realistic ceiling of open sources, and the typographic
fallback there is the primary rendering, not a degraded one. An author with one
pen name has one; an author with none is not missing anything.

The report's job is to make that distinction explicit for every low number it
carries, because the next agent will otherwise read every gap as work.

## 5. Staleness

Content rots in place, quietly, and nothing in CI has a clock.

- **Notes and comments referencing decisions since reversed.** A header comment
  calling `works.yaml` a first pass after the completeness audit closed it. A
  `debated` entry arguing a placement that a date correction settled. These read
  as current to every future agent and misdirect them. Comments like these are
  the one class you may fix in place, since correcting a statement of fact
  carries no editorial judgement - but say in the report that you did.
- **`confidence: low` never revisited.** Whoever set it was flagging work to
  come back to. Check whether it was, and whether the source that would settle it
  has since become available.
- **Curator questions raised in old PRs and never answered.** Read the PR bodies
  of the stages that built this wing. The pipeline collects decisions that are
  the curator's to make; the ones that were never made are still open and are
  invisible in the content. Surface them.
- **Anything an agent flagged as its own weakest decision.** Agents that name
  their weak points are doing the job right. Those flags are not resolved by
  being merged, and quietly ratifying them is how a guess becomes canon.
- **Sources that have moved.** Spot-check a handful of `sources:` URLs. A dead
  citation is a fact with nothing behind it.

## Hard rules

- **Never fix an editorial issue that belongs to another skill. Route it.**
  Trivial mechanical fixes only, and list them.
- **Never report a number you did not re-derive yourself** (CURATION §5). Run
  the script. Count the rows. A number inherited from another agent's report is
  that agent's claim, not your finding.
- **Distinguish absent from not applicable** (CURATION §7), for every gap you
  report.
- **Verify the validator's coverage rather than trusting the table above.** The
  gap between what CI checks and what the schema promises is where the defects
  live, and it moves every time somebody hardens the validator.
- **Report the ones that came back clean**, with what you checked. "Every OL
  cover is a `/b/id/` URL, so `?default=false` does not apply" stops the next
  auditor re-opening it.
- **`validate.py` green before you report**, so nothing in your findings is
  confused with something you broke.

## Process

1. **Establish the baseline.** Run `validate.py`, `i18n_coverage.py` and
   `event_density.py` yourself and keep the numbers. Every claim below is
   measured against these, not against a previous report.
2. **Read the wing's history.** `git log --reverse` over the franchise directory.
   Which stages ran, in what order, and what ran before the work list closed.
3. **Read the wing.** Every file in `content/franchises/<slug>/`, the author
   entities its works reference, its locale overlays, and `events/global.yaml`.
4. **Walk the seams** (section 1), starting from the set of works added last.
5. **Audit the orphan types** (section 2): eras, theme, achievements,
   capabilities. Nobody else will.
6. **Measure density and proportion** (section 3), across franchises as well as
   within this one.
7. **Spot-check every suspiciously complete number** (section 4), by artefact,
   and classify every gap absent or not applicable.
8. **Sweep for staleness** (section 5), including the PR bodies.
9. **Prioritise and route.** Sort into blocking / next round / cleanup, and put
   an owner against every finding.

## Output

A prioritised findings report, in the PR body. Four buckets, in this order, each
finding carrying **what you checked, what you found, and who owns it**:

**Blocking** - wrong or misleading content that reaches a reader. A false fact, an
unprotected reveal, an image that renders nothing, a badge nobody can earn, prose
that contradicts the data beside it. These ship harm; they are not next-round work.

**Missing** - real gaps with an owner and a next action. The works with no cover,
the layer never enriched, the stage that never ran.

**Stale** - true once. Reversed decisions still documented as current, unanswered
curator questions, unrevisited `confidence: low`, dead sources.

**Checked and clean** - what you verified that came back fine, with the basis.
This is not padding: it is what stops the next audit repeating your expensive
half, and it is the only part of the report that proves the rest was earned.

Then two short lists:

- **Not applicable, not absent** - every low or zero number that is a correct
  state for this wing, so nobody closes it by inventing data.
- **The curator's call** - the findings that are genuinely a judgement nobody in
  the pipeline should make alone.

## Done means

The wing has a report a curator can act on without re-deriving anything: every
finding measured from the artefact rather than from another agent's summary,
sorted by whether it harms a reader now or merely costs work later, and routed to
the skill that owns it. The orphan layers - eras, theme, achievements,
capabilities - have had a real pass rather than a mention. Every suspiciously
complete number has been spot-checked against the thing it counts. Every gap is
explicitly marked absent or not applicable, so the next round closes the real
ones and leaves the sparse wing sparse.

**And the report names what is genuinely missing.** An audit that finds nothing
on a wing six agents just worked over has not audited it.
