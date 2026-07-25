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
