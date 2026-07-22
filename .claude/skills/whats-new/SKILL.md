---
name: whats-new
description: Establish what has changed about an author since the wing was last curated - new works, new life events, a death, corrected records, shifted critical framing, rotted sources - and route each finding to the stage that owns it. Use as the first stage of a refresh pass, or when a wing has not been looked at in a while.
---

# whats-new

Every other stage asks *"is this wing right?"* This one asks a different
question: **"what has happened since we last looked?"**

A wing is curated at a moment. The author then keeps publishing, wins things,
gives interviews, changes publishers, and eventually dies. Sources rot,
editions go out of print, and the critical record moves. Nothing in this repo
notices on its own, so a wing that was excellent eighteen months ago is now
quietly, invisibly out of date - and it looks exactly like a wing that is
current.

This skill runs under `docs/CURATION.md`; the shared contract is stated there,
not repeated here.

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

## You produce leads, not content

**Write nothing into `content/`.** Like `wing-audit`, this stage's output is
the next round of work, routed to the skill that owns it. If you research a
new work properly and write it yourself, you have done
`completeness-auditor`'s job with less of its discipline, and the owning skill
never learns the wing needed it.

The one thing you may fix in place is a **dead source URL** where you can find
the same document at a new address: swapping a rotted link for an archived
copy of the same page is mechanical, carries no editorial judgement, and is
worth doing while you have it open. Say so in the report.

## Bounding the search

You are not re-auditing the career. Establish a floor and search forward from
it:

- **`python scripts/wing_freshness.py`** gives you, per wing: whether the
  author is living, the most recent published year on the shelf, the most
  recent dated aura entry, and when the wing last changed in git. Start there.
- **The shelf's latest year** is the floor for new works. The bibliography
  below it was audited by `completeness-auditor`; your question is only what
  has landed since, plus anything announced that has now appeared.
- **The aura's latest year** is a separate and usually *earlier* floor. Press
  work goes stale faster than bibliography: a wing can have every book and no
  context for the last decade of them.
- **Git, not a field.** When a wing was last touched comes from
  `git log -1 --format=%cs -- content/franchises/<slug>/`. Do not add a
  `lastReviewed:` key to the content; that is process metadata in a data file
  and the comment policy exists to keep it out.

Where commit messages name a stage (`content(press): ...`), you can date that
stage specifically. Where they name only the wing, fall back to the wing's
last touch and say which you used - an unstated assumption about your own
baseline is exactly the kind of thing that reads as evidence later.

## What actually changes between passes

Ranked by how often it matters.

**1. New works.** The common case, and two shapes: books published since the
last pass, and books that were *announced* then and have landed since. Check
the publisher's forthcoming list as well as the record, because an announced
title is frequently listed under a working title that later changed.

**2. The aura has fallen behind the shelf.** Usually the real finding. New
books arrive and nobody re-runs the press pass, so the last five years of a
career sit against blank ground. `scripts/aura_density.py` names the dark
runs; this stage's job is to notice the *newest* one, which is the one a
reader hits at the end of the walk.

**3. A death.** The highest-consequence single event, and it changes the wing
in four separate ways that are easy to do partially:

- `died` must be set on the author entity. The app closes the global-event
  lifetime window at death, so leaving it unset renders decades of world
  events on a page whose author was not alive for them.
- **Obituaries are the best periodisation document that will ever exist for
  this author** (see the `eras` skill's ladder, rung 2). A death is therefore
  the single best moment to revisit eras, and the window is short: a great
  deal gets said carefully, once, and then never again.
- Posthumous publication starts, and it dates by publication while belonging
  to a working life that ended - the `eras` skill's genuinely-outside case.
- The estate begins making decisions about what "complete" means, which is a
  `completeness-auditor` scope question.

**4. The record corrected itself.** A contested date settled, a bibliography
updated, a first-publication claim revised. Re-check anything the wing carries
as `confidence: low` or flags in a `note:` as unresolved - that is a list of
questions somebody already wrote down for you.

**5. Received framing shifted.** A new critical study periodises the career, a
community order consolidated, the author published their own "where to start",
or a term entered common use. This is what turns an honest
`provenance: none` era or an unsourced entry path into a sourced one, and it
is the only way those debts ever get paid. Check the wing for them explicitly.

**6. The catalogue's span extended.** If the author now publishes into a
decade `events/global.yaml` leaves empty, that is a `world-events` question -
and then an `event-resonance` one, because a new shared event does not
automatically belong on this author's page.

**7. Sources rotted.** Dead links, delisted editions, moved covers. Cheap to
detect, and a citation behind a dead link is a fact with nothing under it.

## What does not count as new

- **A reprint, reissue or new edition of an existing work.** That is
  `editions` work at most, never a new entry in `works.yaml`.
- **An adaptation.** A film, a series, a game: not a work by this author.
- **Anniversary coverage.** Recycled facts, no new information, and the trap
  registry already warns about it.
- **A prize longlisting**, unless the wing's aura genuinely turns on it.

## Report

Route every finding. The report is the whole deliverable:

| Finding | Owner |
|---|---|
| new or announced-and-now-published works, corrected dates, scope questions | `completeness-auditor` |
| new life events, new press, a death, corrections to received wisdom | `press-archaeology` |
| a death, or newly published periodisation | `eras` (after the press pass) |
| a newly published author or community reading order, a new entry path | `reading-orders` |
| the catalogue span extended into an empty decade | `world-events`, then `event-resonance` |
| new works with no cover, portrait now available | `visual-metadata` |
| new works with no edition, delisted editions | `editions` |
| any new or changed prose | `spoiler-audit`, then `translation` |
| nothing changed | say so plainly - see below |

**"Nothing has changed" is a real and valuable result.** A wing whose author
published nothing, did nothing newsworthy and whose sources all still resolve
is *current*, and saying so with the date and what you checked stops the next
pass re-running the same searches. Record what you searched and the floor you
searched from, so the finding is verifiable rather than a shrug.

**State your baseline explicitly.** Every claim in this report is relative to
a date, and a report that does not say which date is not checkable.

## Done means

A routed list a curator or an orchestrator can act on without repeating your
search: per wing, the baseline you worked from, what changed under each of the
headings above, what you confirmed had *not* changed, the sources you checked,
and any link you repaired in place. Plus, for a death, the four consequences
above named individually rather than as one line - it is the finding most
often done halfway.
