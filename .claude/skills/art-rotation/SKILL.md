---
name: art-rotation
description: Grade a wing's whole timeline into a paced visual sequence - assign every event, life event and era plate an `organisation` (plus illustration_type, images_required, modifier) so the river reads with rhythm instead of a flat run of identical cells. Use as a stage of /author after visual-language, and whenever a wing's events were added or changed without a rotation pass. Gates on `art_rotation.py --check`.
---

# art-rotation

Every event in a wing carries an `organisation` - one of the sixteen river cells
in `docs/LAYOUT.md` - and it decides how that moment is laid out and, later, what
art it gets. **Unset, it defaults to `beside`.** So a wing that never had this
pass renders as a flat wall of identical two-up cells: `art_rotation.py --check`
reports `beside 9/9 OVER THE CAP` and a pacing contour of `=========`, a plateau.
That monotony is the exact failure this stage exists to remove.

Your job: read the wing's whole timeline and give each entry an organisation that
(1) **fits what the moment is** and (2) **paces the sequence**, so the contour
reads loud/mid/quiet with its ruptures spaced out.

Read first: `docs/LAYOUT.md` (the sixteen organisations, their intent, the
pacing rules and the gutter) and `docs/VISUAL.md` §3b (the illustration types).
This skill runs under `docs/CURATION.md`.

## Cheap tools before expensive habits (this stage pays for its own calls)

Every tool call re-sends your whole context, so what a stage costs is roughly
its context multiplied by how many calls it makes. One wing's editions stage
made 144 sequential fetches; the pages were not the expense, fetching them one
at a time was. Three habits, before you start:

- **Editions and visual-metadata: reach for `scripts/metadata/lookup.py` FIRST.**
  For those two stages the whole fetching half is already one tool call:
  `python scripts/metadata/lookup.py <slug> --author "<name>"` sweeps the
  registered providers and prints a TSV of edition and cover candidates for the
  entire wing (`--verify-isbns` checks an existing `editions.yaml`,
  `--check-covers` HEADs every cover, `--markets no,en,pt` widens the search,
  `--json` when something parses it). Measured on the Jo Nesbo wing it replaced
  ~360 sequential fetches (~880k tokens, 57 min) with ~40 HTTP requests inside
  one call. It does **not** replace the stage's judgement - which market, is
  this an omnibus, is this a title-page scan - and every real catch on the wings
  built so far was one of those, not a lookup. So run it, then judge the table.
  A source it does not cover yet is one provider class in
  `scripts/metadata/providers.py`; add it there rather than hand-fetching around
  it. The rest of this section still applies to the verification fetches the
  table sends you back for.
- **Every other stage: fetch in batches, not one by one.** `python scripts/fetch.py URL [URL...]`
  takes many URLs in a single call, caches to `.cache/fetch/` (so a URL an
  earlier stage already paid for is free), sends the browser User-Agent that
  portoeditora.pt, infopedia.pt, observador.pt and the BNP catalogue require,
  and prints a bounded extract rather than a whole page. Use `--grep 'ISBN|1a ed'`
  to pull just what you need, `--check` for link sweeps, `--max-chars` to tighten.
  Collect the URLs you want, then make one call. **web.archive.org rate-limits
  and starts refusing connections at the default 6 workers** - pass
  `--workers 2` for archive-heavy batches rather than losing the batch.
- **Orient with the digest before reading the wing.**
  `python scripts/wing_digest.py <slug> --for <your stage>` renders a finished
  wing in ~2.4KB where the YAML is ~98KB, and answers "which works still lack a
  cover, an edition, a synopsis, an era" directly (`--missing cover`). Then read
  in full the entries you are actually going to edit - the digest orients, it
  never substitutes for reading what you edit.
- **Scope every check to your own wing.** You are building one author; a report
  covering nine buries your own numbers, costs context for nothing, and tempts
  you to tune against a neighbour's figures or "fix" a wing nobody asked you to
  touch. Pass the slug:
  `validate.py --slug <slug>` (checking stays catalogue-wide - a broken
  reference crosses wings - only the warning list narrows). This one is
  measured and still gets missed: one wing build ran eleven catalogue-wide
  validations where ten could have been scoped, each re-reading 40+ untouched
  wings to prove one file parses,
  `aura_density.py <slug>`, `wing_digest.py <slug>`, `asset_audit.py <slug>`,
  `stage_plan.py <slug>`. `event_density.py` has no slug on purpose: it measures
  the shared `global.yaml` budget, which is catalogue-wide by nature.
- **Build the URL instead of searching for it.** Publisher product pages and
  catalogue records follow patterns. A search whose only output is a URL you
  could have constructed costs thousands of tokens for nothing. Search when you
  need to discover *that* something exists; fetch when you know where it is.

None of this licenses thinner research. It buys the same evidence for less, so
that the budget goes on judgement instead of on transport.

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

## The two questions per entry

**Does it fit?** Match the organisation to the moment, not the other way round:

- **loud** (rare, earned - a moment the reader should stop at): `immersion` (a
  total stop - a death, a rupture), `full-bleed-vista` (a wide landmark place or
  a breath), `chapter-gate` (a hard reset - usually an era boundary), `mosaic`
  (public noise, a crowd).
- **mid** (the workhorses - most events): `beside`, `strip`, `medallion`,
  `diptych`, `split-counterpoint`, `layered-stack`, `artifact-spread` (a
  document), `floating-object` (a single symbolic object).
- **quiet** (the device is restraint): `passage` (compressed time, a montage of
  years), `interlude` (an emptiness, an absence), `marginalia` (a footnote-scale
  aside), `epigraph` (the author's own words, no artwork - needs a sourced
  `quote`; capped 2-3/wing).

**Does it pace?** The whole wing is one composition, not a queue of independent
choices (writing them one at a time is what produced the seven-elevenths-tables
monotony on an early wing). `art_rotation.py --check <slug>` is the gate and it
enforces:

- **No two loud cells touching** - a rupture earns its weight from the quiet
  around it.
- **No plateau**: no five-or-more consecutive cells at the same intensity
  (loud/mid/quiet), however varied the organisations inside it.
- **No two loud cells in one screenful** (it measures viewport shares, not event
  counts - two ruptures a few events apart still land on one screen).
- **Organisation caps**: `beside` at most 6, and the loud/quiet specials capped
  per `docs/LAYOUT.md` (`immersion`, `epigraph`). Vary the mid cells too so the
  same one does not run.

Read its output as a contour (`#` loud, `=` mid, `.` quiet). You are shaping that
line into the rhythm of a life: mostly mid, a few earned ruptures, quiet where
the moment is an absence or a compressed stretch.

## Also set the rest of the grammar

Alongside `organisation`, set on each entry the fields the art pipeline reads
(`docs/LAYOUT.md`, `docs/VISUAL.md`):

- **`illustration_type`** - the subject register (VISUAL §3b): what the drawing
  depicts. Vary it across the wing (a cap of ~a third on any one type - the
  "avoid repetition" rule).
- **`images_required`** - 1 unless the organisation needs more (`diptych` 2,
  `split-counterpoint` 2, etc., per LAYOUT.md).
- **`modifier`** - an optional composition twist (`breakout`, `pull-focus`,
  `fold-reveal`, `anchor-with-satellites`, `branch`) where it earns its place.

**The orrery motif is NOT yours.** It is universal and added per-image at prompt
time (`docs/VISUAL.md` §1a), never graded here and never a `theme.art` field.

## Footprint and gate

You write `organisation`/`illustration_type`/`images_required`/`modifier` onto:
`events.yaml` (franchise events), `content/authors/<id>.yaml` (author
`lifeEvents`), and `eras.yaml` (era plates). You touch nothing else.

Gate: **`python scripts/art_rotation.py --check <slug>` reports 0
organisation-rotation problems AND 0 pacing problems**, and
`python scripts/validate.py` is GREEN. A wing with any plateau, adjacent loud,
or over-cap organisation is not finished, however good each single choice.

`art_rotation --check` has a *third*, separate axis - **composition** ("N assets
with no issue at all") - which counts the GitHub art issues, populated later by
`/asset-prompt`, not by you. On a freshly built wing no issues exist yet, so that
axis stays flagged and the tool's exit code stays 1 even when your two axes are
clean. That is expected and not yours to fix; drive the organisation-rotation and
pacing counts to zero, read those two lines specifically, and do not chase the
composition line.

Hand off the contour you achieved and any moment whose organisation was a genuine
judgement call.
