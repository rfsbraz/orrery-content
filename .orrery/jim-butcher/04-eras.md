---
stage: eras
summary: "Eras confirmed rejected for jim-butcher: no received periodisation exists; eras: [] with strengthened evidence (series concurrency + full-bleed overlap). A thin honest eras layer is the right call here."
---

## Decision: eras: [] (rejection confirmed and strengthened)

The scaffold's documented rejection holds. I gave the overturn a genuine shot in
both shapes the task named and neither clears the bar; I then added evidence the
scaffold did not have. This is not a defect to close - it is the correct,
complete outcome for an author no one has periodised.

## Both candidate shapes, tested

**1. Per-series arcs (the Dresden internal shift).** The "case of the week"
early novels vs the arc-driven back half, with Changes (2010) as the pivot, is
genuinely and widely *described* - but it is a described evolution, not a
received periodisation with names a reader would recognise (King's "Golden
Decade", "Bachman years"). The tell is that the standing fandom question is
*whether* the series even divides into arcs and *where* (the recurring "ongoing
serial or story arcs?" discussions), and the Dresden Files fandom wiki carries
**no named arc divisions**. An open debate is the opposite of settled consensus
(rung 3 fails). The only structural framing anyone repeats is Butcher's own
FAQ plan: "25: 22 'case books'... capped with a double-length apocalyptic
trilogy" (https://www.jim-butcher.com/faq, fetched and confirmed) - a plan for a
series still being written, naming no years and no periods of the *published*
shelf. Rung 1 gives a plan, not a periodisation.

**2. Whole-career periodisation by publication chronology.** The task floated
early Dresden / a Codex Alera interlude / mature Dresden + Spires. This fails on
the *record itself*, not just on sourcing, which is the new evidence worth
carrying: **the three series are concurrent, not sequential.** A Dresden novel
appeared every year 2000-2014 while the six Codex Alera novels ran 2004-2009
alongside them; Cinder Spires (from 2015) overlaps the late Dresden run.
(Confirmed from the catalogue's own dates and corroborated externally - Butcher
wrote Dresden and Alera at the same time, which is why Dresden dropped to one
book a year from 2004.) There is no early/interlude/late sequence to draw.
"Codex Alera interlude" is factually wrong: it was never an interlude.

**Why even shape 1 can't render as a wing era.** An era is full-bleed across the
*wing's whole timeline*. Any "early Dresden 2000-2009" span would also swallow
the concurrent Codex Alera 2004-2009 - a Roman epic fantasy sharing neither
genre nor world - under one plate, and era membership is by year, so that
overlap is the exact bug the skill forbids, not a presentation nuisance.

## Sourcing for the rejection

- Butcher FAQ (rung 1): a whole-series *plan*, not a periodisation of published
  work. https://www.jim-butcher.com/faq
- Fandom (rung 3): no named periodisation; the community debates arc structure
  rather than sharing settled period names. No named divisions on the fandom
  wiki. The "case of the week -> escalating arc, Changes as pivot" evolution is
  real and widely described but unnamed.
- Critical/scholarly (rung 2): none. Living author, no obituary tier; the
  "career phases" pages that surface (nocloo.com, studyguides.com) are
  AI-generated summary, not criticism - citation-laundering bait, not sources.
- Publishing-historical (rung 4): the one clean fact (concurrent series) argues
  *against* a periodisation, not for one.

Languages searched: English only, correct here - press-archaeology already
established Butcher is covered almost entirely in English. Nothing refused me.

## What I changed

`eras.yaml` stays `[]`; I rewrote the rejection note to add the concurrency
evidence and the full-bleed overlap argument, corrected the plan figure to the
FAQ's exact "22 case books + trilogy", and kept it sanctuary-clean (data facts,
present tense, no process narration). No works file touched.

## Validation

`python scripts/validate.py --slug jim-butcher`: 1 error, the expected
pre-existing `theme.art` gap (visual-language's, not mine). **Zero warnings on
this wing.** Note for the record: `eras: []` produces **no** "work outside every
era" warnings - the validator treats an empty eras layer as the no-era state,
not as orphaning. Nothing is stranded. Commit: 76557db.

## For downstream

- **reading-orders**: no era layer exists to lean on; the derived publication
  order is the spine. The three concurrent series are the real structural fact
  about this wing.
- **spoiler-audit**: unaffected by this stage. The scaffold's flags on Twelve
  Months and Battle Ground still stand.
