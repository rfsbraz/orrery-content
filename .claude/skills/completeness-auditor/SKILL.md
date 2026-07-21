---
name: completeness-auditor
description: Audit a franchise's bibliography against primary sources for missing works, wrong first-publication dates, inconsistent tiering, and missing series or collaboration links. Use before anything annotates works, since it changes how many works exist.
---

# completeness-auditor

Verify that `works.yaml` says what the record says: every work present, every
date the date of **first publication**, every tier and series link consistent.

This skill runs under `docs/CURATION.md`, the shared contract for every
curation stage; its rules are not repeated here.

Orrery's default reading order is **derived from this file**. A missing book is
not a gap in a list, it is a hole in the spine of the franchise, and it makes the
site quietly wrong for the completionists it exists for. A wrong year silently
reorders someone's walk.

**Run this before any stage that annotates works** (covers, editions,
translation, spoilers). It changes how many works exist, and everything
downstream keys off that list.

## The dating rule

**`published` is the year of first publication anywhere, in any edition, in the
original language.** Ahead of: the trade edition, the US or UK edition, the
collected edition, the revised edition, the edition that happens to carry an
ISBN.

This matters because **catalogues and retail metadata record the edition that
sold, not the edition that came first.** That is a systematic bias, not an
occasional typo. Two confirmed instances:

- *The Eyes of the Dragon* sat at 1987 (Viking trade). It was first published in
  **1984**, a 1,250-copy Philtrum Press limited edition.
- *The Moving Finger* sat at 1943 (Collins Crime Club, UK). Dodd, Mead published
  it in the **US in July 1942**, eleven months earlier.

Where first publication was a limited edition, a serialisation, or a different
market, **keep the earlier year and record the fuller story in a `note:`**, so
the next auditor inherits a decision instead of re-litigating it.

### Serialisation

**A serial counts as first publication only if the complete work appeared, and
only when it finished** (not when it began).

Requiring the complete text is not pedantry, it is the difference between three
corrections and thirteen. A live trap: **Wikipedia's phrase "the first true
publication" does not mean unabridged.** It uses that exact phrase for one
Christie serial while elsewhere calling that same serial abridged. So require a
**positive statement of completeness** or an earlier book edition. Silence about
abridgement is not evidence of completeness.

Roughly ten Christie titles currently sit in exactly that silence, flagged and
unchanged in `works.yaml`. **They must be settled together**, since a rule that
promotes one promotes all ten, and they need a proper serialisation bibliography
rather than an encyclopedia.

### Collections and fix-ups

Dated by the **collection**, not by the earliest magazine appearance of a
constituent story, or the shelf scatters. A fix-up novel is the work, even where
its parts ran separately years earlier.

### When a prior edition is a different work

Judge whether it is another edition or another book. *New Spring* is dated by the
2004 **novel**, not the 1998 novella: the novel roughly quadruples it. Record the
distinction in a `note:` where a catalogue will keep disagreeing with you.

## The audit

1. **Missing works.** Novels, collections, novellas, nonfiction, screenplays
   published as books. The long tail is where the gaps live, but not only there:
   one audit found *Elevation*, a solo novel from a year the file already
   covered. Assume nothing is too obvious to be missing.
2. **Wrong years**, per the dating rule above.
3. **Inconsistent `canonTier`.**
4. **Missing `subseries`** on works that belong to a named thread.
5. **Missing `withAuthorIds`**, and `authorRole` where the author did not write
   the whole book (see the schema: a contributor entry must be `apocrypha`).

### canonTier records the kind of publication, never your confidence

`core` is the spine, `extended` is genuinely theirs but off it, `apocrypha` is
contributions, limited or unfinished works, and periodical pieces.

**Uncertainty goes in a `note:` or `confidence:`, never in the tier.** A work
parked in `extended` because nobody verified it tells every downstream reader
something false about its status. One audit found five real novels sitting in
`extended` for precisely that reason.

## Language follows the author

For a non-anglophone writer, the **publisher's own catalogue and the national
library are the standard**, and an English-only sweep will report a thin
bibliography that is simply wrong. It is also how you find the books nobody else
lists: one audit found a Tordo essay collection missing from the catalogue
because it was published by a foundation rather than his usual publisher, and
appeared only on his own site.

**Check the trap registry (`docs/CURATION.md` §4) before writing off a
Portuguese source** - it records which catalogues block automated fetches and
which only looked blocked (BNP's ipac20 catalogue answers a browser
User-Agent). Where verification ends up resting on the publisher's catalogue,
the author's own bibliography and the press cross-checked against each other,
**say so in the report**, and name any fact resting on a single source so a
human with a browser can settle it.

## Hard rules

- **Report every reorder.** For each corrected date, say whether it moves the
  work's position in the derived order and name the works it now sits between.
  That list is what the curator actually needs.
- **Do not manufacture changes.** Checking 179 works and correcting three is a
  good run.

## What is the curator's call, not yours

Emit a decision where the record supports one. Escalate only these:

- **A correction that reorders the derived reading order.**
- **Scope**: multi-author anthologies, books where this author is secondary,
  unfinished or unpublished works, announced-but-unreleased titles.
- **Series labelling** where two names are both genuinely correct (a recurring
  character spanning two separately-marketed sequences does **not** merge them;
  see the series rule in `franchise-research`).
- **A contested date you could not resolve.** Flag it. Getting a famous novel
  wrong in either direction is worse than saying you do not know.

## Done means

A PR whose body reports: works before and after; every work **added** with its
source; every **correction** with its evidence and whether it reorders; what you
found and deliberately **did not** add, and why; contested cases left alone; and
inconsistencies flagged but not changed.

The rejections and the flags are as much the deliverable as the additions. A wing
whose gaps are documented is in better shape than one whose gaps are invisible.
