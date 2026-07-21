---
name: eras
description: Establish and audit the provenance of a franchise's creative eras - the named periods the app renders as full-bleed "ENTERING <title>" plates. Enforces that an era is received from the author, critics, fandom or the publishing record rather than coined by us, and that its boundaries are sourced too. Use when writing, renaming, re-cutting or auditing content/franchises/<slug>/eras.yaml.
---

# eras

An era is the largest editorial claim Orrery makes. The app renders it as a
full-bleed plate reading **"ENTERING <title>"**, in a serif face, across the
reader's whole screen. Nothing about that presentation says "our reading of it".
A reader takes it as a received term, the way they take "the Golden Age of
detective fiction" or "the Blue Period" as received terms.

So the standard is not "is this a defensible way to group the books". It is:

> **Can you point at someone outside this repo who periodises this author's
> career this way?**

If the only source is our own reading, it is not an era. It is our opinion in a
serif font.

This skill runs under `docs/CURATION.md`, the shared contract for every
curation stage; its rules are not repeated here. Read `docs/SCHEMA.md` (eras)
and the **aura editorial standard** (`docs/CURATION.md` §6) first. This skill
governs one file: `content/franchises/<slug>/eras.yaml`.

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

## 1. An era is received, not coined

The test above is the whole skill in one line. Everything below is how to apply
it.

Two failure modes look identical in the YAML and are very different in kind:

- **An invented label.** We named a real period something nobody calls it.
  Recoverable: find the received name, or fall back to a neutral one.
- **An invented periodisation.** Nobody divides this career here at all; the
  shape itself is ours. Not recoverable by renaming. See rule 4.

A third is worse than either: **a critical verdict the site is not entitled to
make.** "Psychological Maturity" says the earlier books were immature. "The
Postwar Plateau" says the work flattened. Those are positions in a live critical
argument, asserted by a site that has no standing in it. Orrery **reports the
conversation about a writer; it does not join it.**

## 2. The legitimacy ladder

Strongest first. Work down it and stop at the first rung that holds.

### Rung 1 - the author's own framing

The author naming their own period. Pratchett calling his diagnosis **"The
Embuggerance"**, capitalised, as a proper noun. Sanderson's **"unpublished
works"** for the trunk novels. Tordo's **"trilogia dos lugares sem nome"** on his
own site. A writer talking about "my Bachman years".

**Evidence required:** the author's own words, quoted, with the URL. Quote them
in the era description too - it is the best sentence you will get.

**Watch the scope shift.** Pratchett's word names *his illness*, not a body of
work. Using it as the name of a creative period is a small editorial move on top
of a received term. That may be the right call, but say so rather than pretending
the period name is his.

### Rung 2 - critical or scholarly consensus

Published criticism, retrospectives, obituaries, academic work, reference works,
major-press career pieces.

**Obituaries are the best single document in this tier.** An obituary is a
researched periodisation of a whole life, written by someone who had to decide
what the phases were. Look for them first when an author is dead. (Be warned:
they often turn out to be chronological rather than periodising. The Guardian's
1976 Christie piece names no phases at all. A negative result from an obituary is
a strong signal that no critical periodisation exists.)

**Evidence required:** a URL you have fetched and read, and the sentence that
carries the periodisation. A book title counts and is often the cleanest citation
available: Joseph Reino's *Stephen King: The First Decade, Carrie to Pet
Sematary* (Twayne, 1988) and Tony Magistrale's *Stephen King: The Second Decade,
Danse Macabre to The Dark Half* (Twayne, 1992) periodise in their subtitles, with
the boundary works named. That is a citation, not an inference.

### Rung 3 - settled fandom consensus

Real, and sometimes the only tier available for genre work. The Wheel of Time
**"slog"** is the model: fans named a period the critics never did, and the name
stuck.

**Evidence required: breadth, not existence.** One forum post is one person. Tell
the difference like this:

- **Settled**: independent sources use the term *without introducing it*, as
  common knowledge. It has a name a reader would recognise. Sources disagree
  about its *edges* while agreeing it exists - that argument is itself proof the
  thing is real.
- **Not settled**: you found it once. Or every use is someone proposing it. Or
  it is one blogger's three-phase scheme. A personal blog positing "formative /
  mature / late" is one reader's opinion with a URL.

Cite **two or three independent uses** and say in the PR that this is what you
are doing, because a fandom term has no origin document to point at.

### Rung 4 - publishing-historical fact

"The Bachman years". The Doubleday run. The Gollancz years. An author transition.
The founding of a company, a rebrand, a move between publishers.

Defensible **because it is a fact about the record rather than a verdict on the
books.** Nobody has to agree with you that the period is a period; they only have
to agree the contract changed. This rung is the safety net when rungs 1 to 3 come
up empty, and it is under-used.

**Evidence required:** the bibliographic or corporate fact, sourced.

**The trap is fit, not truth.** A true publishing fact can still be a bad era.
Colin Smythe published the first *five Pratchett novels*, but only *two* of them
were Discworld - so "The Colin Smythe Years" would slice a 41-book series at book
2 and be perfectly accurate and useless. Check what the fact actually covers
before you name a period after it.

### Rung 5 - our own periodisation

**Not permitted as an era.** If the shape is real but unnamed, go to rule 4.

## 3. Neutral over evaluative

Prefer descriptive labels anchored in fact over verdicts:

| Prefer | Over |
|---|---|
| the Bachman years | the golden decade |
| the post-accident novels | psychological maturity |
| the Dragonsteel era | the long apprenticeship |
| the Trilogia dos Lugares Sem Nome | the metaphysician |

Where a genuinely received term **is** evaluative - "the Golden Age of detective
fiction", "the slog" - it may be used **because it is received**. That is the
whole licence. But then the description must **attribute it, not assert it**:

- Wrong: "Her imperial phase, and the genre's."
- Right: "The decade critics place at the centre of what they call the Golden
  Age of detective fiction."

The rule, in one line:

> **The site reports the received framing. It does not issue one.**

A flat title is a smaller failure than a false verdict. If the only honest label
is dull, ship the dull one.

## 4. Fewer eras, or none, beats invented ones

**A franchise with no received periodisation should ship `eras: []`.** That is a
complete, correct bundle. The app simply never sets `eraStart`, the reader walks
an unbroken timeline, and nothing is lost except a decoration we were not
entitled to.

**Gaps between eras are legitimate.** Consensus covers some periods and not
others. A sourced era for the 1980s and a sourced era for the 2010s, with nothing
in between, is an honest picture of a career that was periodised twice. **Do not
tile the span for the sake of tiling.** An era invented to fill a hole is worse
than the hole, because the hole is honest.

> **This deliberately overrides the `wing-audit` skill's "era coverage gaps"
> finding**, which treats uncovered years as a defect and instructs the auditor
> to check that "the spans cover the works, without gaps". That instruction is
> now wrong and this skill supersedes it. The reasoning: coverage is a tidiness
> property, provenance is a truth property, and **provenance outranks tidiness.**
> A wing-audit finding of "year 1993 has no era" is not a defect to close. It is
> only a defect if a *received* era covers 1993 and we failed to record it. An
> auditor who closes a coverage gap by inventing an era has made the wing worse
> while making the report greener.

**Overlaps are still a bug.** A work cannot be in two eras: era membership is
computed from the year, achievements count works per era, and an overlap makes
`era_reader` count differently than the page reads. Two eras claiming 2013 is a
defect regardless of how well sourced both are - re-cut one boundary.

The decision, in order:

1. Is it received? Ship it.
2. Is the shape real but the name ours? Rename it (rule 3), keep it.
3. Is the shape ours? Recommend removal. Do not tile around it.

## 5. Boundaries need provenance too

A sourced label on an invented boundary is still an invented era. Ask separately:

> **Why does this era end in 1989?**

If the answer is "because the next one starts in 1990", the boundary is ours.

**Decade-shaped eras are a smell.** `1980-1989`, `1990-1999`, `2010-2019` almost
always mean we rounded. Check whether the source actually periodises that way, or
whether we took a real term and filed it into a decade. Two real cases:

- **The Golden Age of detective fiction** is a genuinely received term, and every
  source spans it across **the interwar years, roughly 1920-1939**. Assigning it
  to `1930-1939` tells the reader that *The Murder of Roger Ackroyd* (1926) was
  not Golden Age, which contradicts every source that uses the term. **The label
  is received and the boundary is invented.** That combination is easy to miss
  because the citation checks out.
- **The Wheel of Time "slog"** is agreed by fandom to end at *Crossroads of
  Twilight* (2003), because *Knife of Dreams* (2005) is the book readers point to
  as the recovery *from* it. An era running the slog to 2005 contradicts the
  consensus it borrows its legitimacy from.

**A boundary you can name is a boundary you can source.** Deaths, diagnoses,
accidents, a pen name unmasked, a publisher changed, a company founded, a
series finished, a form abandoned. If you cannot name the event, do not draw
the line.

Where the received label and the sourced boundary disagree and you cannot fix
both, **keep the label, attribute it, and flag the boundary in the PR.** Do not
silently re-cut a period to make a citation fit.

### Tightening a span orphans whatever fell in the slack

This is the failure mode of doing this job *well*, so read it twice. Replacing a
rounded decade with a defensible range is the right instinct - but the works
that sat in the rounding do not move with it. They fall outside every era, and
the app renders them with `era: null`: no era plate, excluded from `era_reader`
achievements, floating on the River with no context. **Nothing errors.**

A single pass that re-sourced six wings' boundaries orphaned **nine works**,
including three major Stephen King novels stranded in a 1979-1980 gap between
"the Doubleday years" (ending 1978) and Magistrale's second decade (starting
1981). Both boundaries were correctly sourced. The gap between them was nobody's
decision.

`scripts/validate.py` now **warns** for every work outside all era spans. It is a
warning rather than an error because some orphans are legitimate - a posthumous
release or a companion volume genuinely sits outside the creative eras - so the
warning is a question, not a verdict. Answer it for each one:

- **Interior gap** (the author was working, the eras just do not meet): close it.
  Extend a span if the source tolerates it, or add a transitional era with
  `provenance` set honestly and a `note` saying what it bridges.
- **Genuinely outside** (posthumous, companion, a form the eras do not cover):
  leave it, and record why in the era file so the next pass does not "fix" it.

**Run the validator before and after your change and compare the warning list.**
Any name that appears which was not there before is a work you orphaned, and
closing that gap is part of your job, not the next agent's.

## 6. Language follows the author

For a non-anglophone writer, **consensus must be sought in that language's
criticism.** For João Tordo that means Portuguese critics, the Portuguese press
(Público, Expresso, Observador, JL, Diário de Notícias, Visão), Portuguese
publisher pages, and his own Portuguese-language interviews and site.

> **An English-language search finding nothing is not evidence that no consensus
> exists.** It is evidence that you searched the wrong corpus.

State in the PR which languages you searched, per question. "Not found in English"
is not a finding about a Portuguese novelist.

Two corollaries:

- **The received form may be the foreign-language one.** "A Trilogia dos Lugares
  Sem Nome" is what the author and his publisher call it. That is the era's name.
  A translation we invent is a coinage again. Ship the received form and gloss it
  in the description.
- **Foreign-language sources are frequently unreachable** (the trap registry,
  `docs/CURATION.md` §4, records which, and what is worth retesting). Blocked is
  not absent: say which sources refused you, so nobody reads your gap as a
  conclusion.

## 7. Sourcing mechanics

Every era carries `sources` with at least one URL that **uses or supports the
periodisation** - not the author's homepage, not a page about one of the books.
A source that proves the books exist does not source the era.

```yaml
- id: the-embuggerance
  title: The Embuggerance
  period: "2007-2015"
  themes: [mortality, tolerance and personhood, dictated late style]
  provenance: author            # author | critical | fandom | publishing
  description: >
    Written after the 2007 Alzheimer's diagnosis Pratchett himself called
    "the embuggerance", latterly by dictation.
  sources:
    - https://discworld.com/the-embuggerance/
```

- **`provenance`** records which rung of the ladder the era stands on. It is not
  yet rendered and not yet validated, but it makes the claim auditable and stops
  the next agent re-deriving your research.
- **Citation laundering (`docs/CURATION.md` §4) has already bitten this file:**
  a research pass attributed the phrase "experimental period" to Britannica's
  Christie article. The article contains no such phrase and names no phase of
  her career. The citation looked perfect.
- **Where a term is widely used but hard to pin to one origin** (every fandom
  term), cite **two or three separate uses** and say in the PR that this is what
  you are doing and why. That is honest sourcing, not a weaker citation.
- **A `note:`** is where a known weakness lives: a contested date, a label we
  could not source, a boundary we rounded. A flagged weakness is content. An
  unflagged one is a defect.

## 8. Changing an existing era

- **Renaming a `title` is fine.** It is prose.
- **Changing an `id` is not.** Achievement `criteria.eraId` and the i18n overlays
  key off it, and `validate.py` resolves eraId inside achievement criteria. A
  renamed id breaks both. Ids are permanent even when the title they were derived
  from is gone - `the-golden-decade` can hold an era titled "The Second Decade".
- **Any title or description change invalidates the pt-PT overlay.** Fix both
  sides in the same commit (`docs/CURATION.md` §3); do not regress the baseline.
- **Renaming an era can strand an achievement.** `stephen-king/golden-decade` is
  named "Into the Golden Decade" and its description quotes the era title. Rename
  the era and the badge is describing something that no longer exists. Grep for
  the old title across `content/` before you finish.
- **Re-cutting a `period` changes which works fall in the era**, and therefore
  what an `era_reader` achievement counts. Check the badge's `count` still fits.

## 9. Auditing an existing wing

Classify every era into exactly one of three verdicts:

| Verdict | Meaning | Action |
|---|---|---|
| **RECEIVED** | someone outside the repo periodises it this way | cite it, add `sources` and `provenance` |
| **REAL SHAPE, WRONG NAME** | the period is defensible, the label is ours | rename to the received or a neutral term (rule 3) |
| **INVENTED** | no consensus that this is a period at all | recommend removal or merging |

**Fix what you can source. Do not quietly delete what you cannot.** Removing an
era changes what a reader sees on a full-bleed plate; that is a curator's call,
not an auditor's. List it in the PR with your recommendation and a `note:` in the
file, and let them decide.

The one thing you **do** fix without asking: an **evaluative verdict you cannot
attribute**. Leaving "Psychological Maturity" on screen while the PR discusses it
means shipping the harm for another cycle. Replace it with the flattest neutral
label that makes no claim, flag it, and recommend removal.

Report the boundary verdict **separately** from the label verdict. They fail
independently, and an era can have a perfect citation and a fabricated span.

## Hard rules

The prime directives, gates and trap registry are `docs/CURATION.md` §1-§5,
not repeated here. The one worth restating in this skill's terms: **"some
critics say" with no citation is exactly the failure this skill exists to
end.** Finding nothing is a valid, useful, reportable result.

## Done means

`eras.yaml` in which **every era carries a `sources` URL that supports its
periodisation**, and a PR whose body states, per era: the verdict (RECEIVED /
REAL SHAPE WRONG NAME / INVENTED), the rung of the ladder it stands on, the
source found or the fact that none was, a **separate** verdict on its boundary,
and - for anything left unsourced - an explicit recommendation for the curator
rather than a silent deletion. Where a franchise turned out to have no received
periodisation, `eras: []` and a sentence saying so is the correct, complete
outcome. State which languages you searched and which sources refused you.
