# Karin Slaughter - eras handoff

## Decision: no eras. `eras: []`, documented rejection (the Flynn/Butcher outcome).

There is no received, sourced periodisation of Slaughter's career. What sources
periodise is her **series**, and a series is a shelf grouping (already carried by
each work's `subseries` and by the two curated orders), not a period of a career.
Turning "the Grant County series" into "the Grant County era (2001-2007)" would be
our own periodisation in a serif font - ladder rung 5, not permitted. Shipped
`content/franchises/karin-slaughter/eras.yaml` as a Flynn-style rejection block
ending in `[]`, recording the four framings that come close and why each fails.

## The four framings tested and rejected

1. **The author names a starting series, not a period.** Verified quote (WebFetch
   of the CrimeReads profile): "I got my start writing about small towns with
   Grant County." A series origin and a change of subject, given no name, no
   boundary, no claim of a phase. (I did *not* quote the search-snippet paraphrase
   "larger and more connected to Atlanta" - snippet, not a page read.)
2. **The two main series overlap, so no year cuts cleanly.** Grant County
   2001-2007, Will Trent from 2006. Triptych (WT #1, 2006) and Fractured (WT #2,
   2008) bracket Beyond Reach (GC #6, 2007). A "Grant County years / Will Trent
   era" split would place concurrent books in different eras and claim 2006-2007
   for two periods - the overlap the skill names as a bug. This is the basis the
   prompt flagged: the year-boundary scheme is rejected on the overlap.
3. **A third of the shelf is in no series.** Six standalones (Cop Town 2014
   through Girl, Forgotten 2022) plus the short fiction span the whole career and
   belong to neither series; a series-shaped era scheme would orphan or misfile
   them.
4. **No critic/obituary/publisher transition periodises the career.** She is
   alive and still publishing (North Falls 2025-2026), so no obituary exists.
   CrimeReads (fullest critical venue) describes a natural progression and names
   no phases; her site and Wikipedia are chronological. No Bachman-years-style
   publisher break: the 2000 William Morrow three-book deal still holds.

## Provenance / boundary verdicts

Per era: none defined, so nothing to cite. Reported as a single INVENTED-if-drawn
verdict on the only candidate shape (series-as-eras), with a separate boundary
verdict: even the label aside, the boundary is ours (rung 5) and would fall inside
a genuine 2006-2007 overlap. No orphaned works, because no spans exist - all 43
works sit outside any era by design (the digest's "outside every era: 43" is the
intended state, not a defect; validate.py raises no orphan warning without spans).

## Languages / sources

Anglophone (American) author, so English is the correct corpus - searched the
author's own words, CrimeReads, general career/retrospective queries, and the
publisher/reading-order sites. No source refused. Nothing periodises the career;
every hit periodises the *genre* (post-Gone-Girl domestic noir, unrelated) or
lists her *series*.

## Spoiler confirmation

There is no era prose, so nothing can render the Grant County spoiler full-bleed.
The one place the eras.yaml comment touches the transition names only the
publisher-marketed fact - "Sara Linton's story carrying from Grant County into the
Will Trent series from its third book ... a character bridge between two live
series." It does **not** state why she leaves Grant County or what happens to
Jeffrey Tolliver in Beyond Reach. The merge-causing event appears in no field or
comment I wrote. No publisher blurbs pulled.

## Validation / commit

`python scripts/validate.py --slug karin-slaughter`: clean except the expected
`theme.art` error (visual-language stage). No new warnings. eras.yaml parses as
`[]`. i18n unaffected (no era prose to translate).

Also corrected a stale franchise.yaml capabilities comment: events.yaml (added by
the press stage) now auto-activates river + companion, and eras.yaml is empty by
design. Commit `330742f` on `wing/karin-slaughter`, not pushed.
