---
description: Bring existing wings up to date with the world - new works, new life events, a death, corrected records, shifted framing, rotted sources - by discovering what changed since each was last curated and running only the stages that changed things need.
argument-hint: "<author or slug | --all> [--since YYYY-MM-DD] [--locales pt-PT,...]"
---

# /refresh

Bring **$ARGUMENTS** up to date with the world. With `--all`, sweep every wing.

## How this differs from `/author`

They share every stage and every skill. What differs is the question:

- **`/author`** is state-driven: *what does this wing need to be complete?* It
  looks at the wing and fills what is missing. One author at a time.
- **`/refresh`** is time-driven: *what changed since we last looked?* It looks
  at the world and carries the delta in. Naturally runs across the catalogue.

So this command owns **cadence and scope**. `/author` owns the pipeline, and
`docs/CURATION.md` owns the working contract. When they disagree, they are
stale - fix them, do not fork the rules here.

**Do not duplicate stages.** Everything that writes content is an existing
skill, invoked exactly as `/author` invokes it, at the model and effort in
`/author`'s stage table. The only skill unique to this command is
`whats-new`, and it writes nothing.

## Sweep first, then decide

1. **`python scripts/wing_freshness.py`** - the mechanical leads: per wing,
   whether the author is living, the newest published year, the newest dated
   aura entry, and when the wing last changed in git. Cheap, no judgement, and
   it is the whole reason this command can run over the catalogue without
   researching seven careers from scratch.
2. **Record the baselines**: `validate.py`, `i18n_coverage.py`,
   `event_density.py`, `aura_density.py`.
3. **Run `whats-new` per wing in scope.** It is the only stage that runs on
   every wing, it is read-only, and its output is a routed list. Wings run in
   parallel freely here: `whats-new` touches no files.
4. **Then run only what it routed to.** A wing whose report says nothing
   changed is *finished* - do not run stages on it to look thorough. That is
   the whole economy of this command.

`--since` overrides the discovered baseline; say in the report that it did.

## Ordering, when a wing does have changes

The dependency graph is `/author`'s and does not change:

`completeness-auditor` (settles the work list) -> `press-archaeology` /
`world-events` / `eras` (parallel, different files) -> `event-resonance` then
`reading-orders` (both write `franchise.yaml`, never paired) ->
`spoiler-audit` alone -> `visual-metadata` / `editions` (parallel) ->
`translation` per locale -> `wing-audit` if three or more layers moved.

Two orderings that matter more on a refresh than on a build:

- **A death routes to `press-archaeology` before `eras`.** The obituaries are
  the periodisation source, so running eras first wastes the one window where
  that material exists.
- **`translation` still runs last**, and on a refresh it is the stage most
  likely to be skipped by accident, because the English change looks small.
  A one-line synopsis correction still invalidates its overlay.

## Scope discipline

A refresh is not a re-audit. The failure mode here is not missing something -
it is **quietly rebuilding a wing that only needed one book adding**, which
burns budget and re-litigates settled curator decisions.

- **Do not re-open settled questions.** A contested date that a curator ruled
  on, an era they chose to keep, a tier they set: those are decided. Change
  them only if genuinely *new* evidence arrived, and then say so explicitly.
- **Do not re-run discovery that came up empty.** `whats-new` reads the wing's
  recorded negatives ("no published periodisation exists", "no
  author-recommended order was found") and only re-tests them where something
  plausibly changed - a death, a new critical work, a newly reachable archive.
  A documented negative nobody re-tests becomes folklore; a documented
  negative re-tested every month is waste.
- **One wing's refresh must not silently widen into a restructure.** If the
  honest finding is that the wing needs rebuilding, stop and say so rather
  than doing it under a refresh's name.

## Integration

Same as `/author`, and the same trap: **re-read every branch tip immediately
before final validation** rather than trusting an agent's completion notice.

1. Merge stage branches in pipeline order, `git merge-base --is-ancestor` on
   each.
2. `validate.py`, `i18n_coverage.py`, `event_density.py`, `aura_density.py` -
   no regressions, and read the warnings.
3. Build the app against the merged content and run its suite. The content
   validator cannot catch an app-side break, and it has repeatedly not.
4. **Run `node scripts/render-check.mjs` over the changed wings** (app repo),
   not a browser. On a refresh it catches the specific failure of a new work
   rendering with a cover URL nobody loaded, which is worse than no cover at
   all. See CURATION.md §5 for why this is a script and not a browser.
5. Delete `.orrery/`, then **open a pull request and stop.** `main` is
   protected; Rodrigo merges it. Never push to `main` or self-merge, and do
   not follow the change downstream - the submodule bump and deploy are
   automatic and not yours to watch or report on.

## Cadence

Sensible defaults, not rules: a **living, actively publishing author** repays
a look every few months; a **dead author with a closed bibliography** changes
only when scholarship or an estate does, so once or twice a year is plenty.
The wings that actually need attention are the ones `wing_freshness.py`
flags, which is why the sweep is step one and not an afterthought.

## Done means

Every wing in scope has a dated answer: either a routed list of what changed
and the stages that acted on it, or an explicit **"nothing changed, checked on
<date> against <sources>"** that the next pass can trust instead of
re-deriving. The catalogue's gates are green, the app builds, the changed
pages have been looked at in every locale, and no settled curator decision was
quietly reopened.
