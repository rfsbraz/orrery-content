---
name: completeness-auditor
description: Audit a franchise's bibliography against primary sources for missing works, wrong first-publication dates, inconsistent tiering, and missing series or collaboration links. Use before anything annotates works, since it changes how many works exist.
---

# completeness-auditor

Verify that `works.yaml` says what the record says: every work present, every
date the date of **first publication**, every tier and series link consistent.

This skill runs under `docs/CURATION.md`, the shared contract for every
curation stage; its rules are not repeated here.

## Cheap tools before expensive habits (this stage pays for its own calls)

Every tool call re-sends your whole context, so what a stage costs is roughly
its context multiplied by how many calls it makes. One wing's editions stage
made 144 sequential fetches; the pages were not the expense, fetching them one
at a time was. Three habits, before you start:

- **Fetch in batches, not one by one.** `python scripts/fetch.py URL [URL...]`
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
  reference crosses wings - only the warning list narrows),
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
