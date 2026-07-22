---
name: editions
description: Record and audit concrete published editions - ISBNs, published titles, translators, publishers - in content/franchises/<slug>/editions.yaml. Use when adding editions for a franchise, verifying an ISBN, deciding which edition of several to record, or auditing existing edition data for bad check digits, wrong regions, or orphaned entries.
---

# editions

Fill and audit `content/franchises/<slug>/editions.yaml`: the layer that turns a
catalogue entry into **a book someone can buy**.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md) - the
prime directives, comment policy, gates, shared trap registry and verification
doctrine apply throughout and are not repeated here.

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

## Why this file is different

Every other layer describes a text. This one describes an object, which changes
the cost of being wrong in two directions:

**It is the buy button.** The app turns an ISBN into an exact-edition store
link, and those links carry the affiliate revenue that pays for the project. A
wrong ISBN does not degrade gracefully into a search box - it sends a reader to
a different book, or to nothing, with the site's name on it.

**It is how a non-English reader sees their own book.** A Portuguese reader
looking at *'Salem's Lot* should see *A Hora do Vampiro*, the object on their
shelf. The published title lives here and nowhere else.

A wrong synopsis is embarrassing. A wrong ISBN is a reader's money.

## The first rule: editions are facts about buyable objects

A work is abstract and permanent. An edition is a physical or digital thing
with a publisher, a year, and usually an ISBN, and it either exists or it does
not. So: **never invent one.** Not the ISBN, not the title, not the translator,
not the year. There is no acceptable interpolation. You cannot reason your way
from "Bertrand publishes King" to "therefore Bertrand published *Christine*" -
they did not, and the gap is in this catalogue for that reason.

**Shipping no `editions.yaml` at all is a completely legitimate outcome.** The
capability is `auto`: absent the file, the app falls back to search links and
Open Library covers, a supported path. An empty file is better than a padded
one, and six honest editions are worth more than sixty guessed.

## ISBN discipline

`scripts/validate.py` runs `valid_isbn13` on every `isbn13` and fails CI on a
bad check digit, because a number that fails its check digit is not an ISBN: it
is a transcription slip or an invention. Both point a reader at the wrong shelf.

### Checking a check digit by hand

ISBN-13 is EAN-13. Weight the first twelve digits 1, 3, 1, 3, ..., sum, and the
check digit is whatever takes that sum to the next multiple of ten.

Worked on `9789727595549` (*A Cor da Magia*, Temas e Debates 2003):

```
digit    9  7  8  9  7  2  7  5  9  5  5  4
weight   1  3  1  3  1  3  1  3  1  3  1  3
product  9 21  8 27  7  6  7 15  9 15  5 12   sum = 141
141 mod 10 = 1  ->  check digit = 10 - 1 = 9  ->  ...549  OK
```

When the sum is already a multiple of ten the check digit is `0`, not `10`.

### Converting an ISBN-10

Pre-2007 books, which is most of a national library's back catalogue, carry
ISBN-10s. Convert by dropping the ISBN-10 check digit, prefixing `978`, and
**recomputing the check digit from scratch** - the old one does not carry over.
An ISBN-10 ending in `X` (a check value of 10) converts like any other: the `X`
is discarded with the rest of the check digit and never appears in a 13-digit
number - `972-759-557-X` becomes `9789727595570` once recomputed.

### A national library can be wrong

The Discworld pass found `The Wee Free Men` recorded at the **Biblioteca
Nacional de Portugal** as `978-989-637-247-2`. That number fails its check
digit (the sum over the first twelve digits is 153, so the digit must be `7`,
not `2`); Wook lists `9789896372477` in both its ISBN and EAN fields, and the
same BNP record types the original title as "The wee free man", singular - a
second slip in one record. The agent recorded Wook's number, cited both
sources, and **wrote the discrepancy into a note**. Both halves of that
behaviour are required:

- **Never fudge a digit to make CI green.** If you cannot find a second source
  that agrees, the entry does not ship. A green build bought by editing a digit
  is worse than a missing edition, because it looks verified.
- **Never silently "correct" a source either.** Say which source you took the
  number from, which one disagreed, and why you believe the one you chose.

A catalogue record is evidence, not scripture. Authority ranks sources;
arithmetic is settled by the check digit.

### When there is no ISBN

Some real editions have none: pre-ISBN printings, book-club bindings, records
whose only identifier is a non-978 EAN. `isbn13` is optional. Record the
edition with publisher, year and title, omit the ISBN, and **say in the note
that it is deliberate** so a later audit does not read the gap as an oversight -
that explanation is a data decision log, exactly the kind of comment the
comment policy (CURATION §2) permits. Two entries already do this correctly:
Christie's 1977 Livros do Brasil *Autobiografia* and the 1987 Europa-America
*O Talismã*.

## Region-strict language codes

**This is the single most dangerous field in the file.**

`pt-PT` and `pt-BR` are different translations, by different translators, with
different titles, publishers and ISBNs (CURATION §4): *The Wheel of Time* in
Portugal is Bertrand's six-volume run; in Brazil it is Intrínseca's, which runs
further under other titles. Never substitutable - and the app scores a `pt-BR`
edition **below plain English** for a `pt-PT` reader, which is correct: a
Lisbon reader sent to a São Paulo edition gets a book they cannot buy locally
and a title nobody in their bookshop recognises. Mislabelling is therefore
worse than omitting.

**Check the registrant prefix on every entry you add. It is the fastest tell,
and a `pt-PT` edition whose ISBN starts `97885` is wrong every time:**

| Prefix | Country |
|---|---|
| `978-85`, `978-65` | **Brazil** |
| `978-972`, `978-989` | **Portugal** |
| `978-84` | Spain |
| `978-607`, `978-968` | Mexico |

**Open Library merges pt-BR and pt-PT under one work record** (§4) - live on
every Lusophone author and every translated English one, and `visual-metadata`
hits the same trap from the cover side. Treat any language metadata that says
bare `pt` as unverified.

The same discipline applies wherever region changes the book: `es-ES` vs
`es-MX`, and `en-GB` vs `en-US` where titles genuinely differ (*Philosopher's*
vs *Sorcerer's Stone*, *Murder Is Easy* vs *Easy to Kill*). Where it genuinely
does not, a bare code (`fr`, `de`, `it`) is right - do not invent regional
precision you did not verify either.

## Published titles

**A work's `title` is its original title, permanently.** The translated title
is a fact about a specific published edition and belongs on that edition.
Three load-bearing rules follow:

**1. Never translate a title yourself.** Not even an obvious one. A published
title is a commercial decision made by a publisher, and translating it yourself
fabricates a book. The catalogue is full of titles no translator would have
produced: *O Enigma das Cartas Anónimas* for *The Moving Finger*, *Os Cinco
Suspeitos* for *Five Little Pigs*, *Jogo Macabro* for *Dead Man's Folly*. The
Christie pass matched every one **by synopsis and series numbering**, not by
title, and wrote the non-literal pairs into the file header. Copy that method.

**2. Never put a title in a `content/i18n/` overlay.** The validator rejects
`title` in `works.yaml` and `editions.yaml` overlays with a message pointing
here. Editions are deliberately not overlaid: the i18n layer translates curated
prose, and a published title is not prose - it is a fact with an ISBN attached.
Overlaying it would let a translator invent a title with no book behind it, in
the one place where invention is unrecoverable. If a work has a Portuguese
title, prove it with an edition.

**3. Many books keep their original title, and that is data.** Bertrand
publishes *The Shining* in Portugal as **The Shining**; the earlier
Europa-America translation was *A Luz*. Seven King editions and one Discworld
edition here carry a `title` identical to the work title, all correct:
*Carrie*, *The Shining*, *Misery*, *Dolores Claiborne*, *Desperation*, *Billy
Summers*, *Holly*, *Mort*. Hybrids are equally real:
`"A Hora do Vampiro - 'Salem's Lot"` is what is printed on the cover. **Do not
normalise it**, do not strip the English half, do not "fix" a title that looks
redundant. Record what the jacket says.

Two mechanical rules: a `title` requires a `language` (validator-enforced; a
title with no locale is unusable), and **omit `title` entirely when the work is
already in that language.** The João Tordo file records thirty Portuguese
editions of Portuguese novels with no `title` field anywhere, which is right:
the work title *is* the published title, and repeating it would manufacture a
translation event that never happened. Publisher store styling ("As três
vidas" in sentence case) is house styling, not a different title.

## Coverage is honest, not complete

Portuguese runs of English-language series stop partway far more often than
they finish. The real coverage in this catalogue:

| Franchise | pt-PT editions | Works covered | Why it stops |
|---|---|---|---|
| Agatha Christie | 74 | 74/86 | Asa's ongoing programme; the gaps are the Westmacott novels and minor collections |
| Stephen King | 68 | 65/95 | Bertrand's rolling reissue programme |
| João Tordo | 30 | 22/26 | Writes in Portuguese; the gaps are non-Companhia short-form pieces |
| Discworld | 8 | 8/48 | Temas e Debates published books 1-7 in 2003-2005 and abandoned the series |
| Cosmere | 7 | 7/28 | Saída de Emergência did Mistborn Era 1 and stopped; Kathartika restarted in 2024 |
| Wheel of Time | 6 | 6/17 | Bertrand bought volumes 1-6 only; the run has not continued since 2023 |

**Discworld at 8 of 48 is not a failed research pass. It is the Portuguese
market.** Forty of those books have never been published in Portugal, and the
correct output for each is no entry at all, so the app shows the English title.

So: **report the real fraction and never invent an edition to close a gap.** A
missing edition is a fact about a market, often the most interesting fact on
the page - it tells a Portuguese reader that book 8 is read in English, and
padding the file destroys exactly that signal. Write the reason for a short run
into the file header, as the Wheel of Time and Discworld files both do:
"coverage is partial by fact, not by omission" saves the next agent a full
re-search.

## Which edition to record when several exist

**Default rule: the most recent in-print edition in that language** - the one a
reader can actually buy today, whose ISBN resolves in a shop. Tiebreaks, in
order:

1. **In print beats out of print.** A perfect first-edition ISBN that no shop
   stocks is a dead link.
2. **The complete text beats the abridged one.** See below.
3. **The trade edition beats the pocket/book-club reprint** where both are
   current - unless the pocket line is genuinely the flagship.
4. **The original publisher beats a licensee**, all else equal.

Recording **more than one edition per work is allowed and often right**: the
João Tordo file lists eight works with both a trade and a "Livro de Bolso"
pocket edition, and King has three works with two editions each. Do it when the
second edition is genuinely a different object a reader might want, not to
inflate a count; put the recommended one first and note what distinguishes the
others. **Out-of-print editions earn a slot when they are the only one**, as
with the 1987 Europa-America *O Talismã* - say so in the note, so nobody reads
the missing store link as a bug.

### The hard case: first publication and fullest text are different books

Sometimes the earliest edition and the best text are not the same object, and
the difference is not cosmetic:

- **Christie's *The Moving Finger*** was cut by roughly 9,000 words for its
  American edition, and that abridgement propagated into later reprints.
- **The American *Three Act Tragedy*** changes the murderer's motive outright.
  It is not a variant text; it is a different solution to the mystery.

**The schema cannot currently express this.** There is no `textVariant`,
`abridged`, or `firstPublication` field, and no way to mark one edition as the
definitive text and another as historically first - a real limitation, stated
here so nobody assumes the data models something it does not. Until it does:

1. **Record the complete text** as the edition, because that is the book you
   want a reader holding.
2. **Put the variance in the `note`**, naming what differs and which market
   carries the cut version. A note is prose the app shows; it is the only
   channel available.
3. If a franchise has several such cases, **flag it in the PR** as a schema gap
   with the examples attached. That is how a field gets added - by a curator
   seeing three real cases, not by an agent inventing a key the validator will
   reject.

Never silently pick one and drop the distinction. A reader who buys the
abridged *Moving Finger* on this site's recommendation was misled by omission.

## Sourcing

**Source ranking, work down it:**

1. **The publisher's own catalogue.** Authoritative on ISBN, year, format, page
   count and in-print status, and it does not disappear when a retailer
   delists. `penguinlivros.pt`, `saidadeemergencia.com`, `kathartika.pt` all
   served this catalogue well.
2. **National library records** - BNP/Porbase, and equivalents elsewhere.
   Essential for out-of-print and pre-ISBN books, which no shop lists. Verify
   the check digit anyway (see the Wee Free Men case).
3. **A major retailer's bibliographic block** - Wook, Bertrand, Fnac publish
   full per-product records. Usable as evidence for facts. **Never as a source
   of images** (see `visual-metadata`).
4. **The author's own site**, for their own bibliography.

**Negative-control every source before trusting a hit** (CURATION §4):
`wwnorton.com`'s per-ISBN pages return HTTP 200 on their own "Page Not Found",
so read the `<title>`, not the status code. Two neighbouring traps: OpenLibrary
ISBN lookups need `?default=false` (§4), and `knopfdoubleday.com`'s search
plants a `?blackhole=` link that bans anything following it - read a page's
links before walking them.

Know what a *legitimate* zero looks like too: **OpenLibrary holds no cover for
most non-anglophone ISBNs.** All six pt-PT ISBNs on the Palahniuk wing had
valid records and no cover image - the normal state, not a lookup failure.

**Cite the record permalink, not the front door** (§4). Every King edition
sourced to BNP cites the identical catalogue-homepage URL, which proves nothing
about any of the sixteen books; Cosmere's per-record `id.bnportugal.gov.pt`
permalinks are the model, and a re-runnable `?index=ISBN&term=...` query is the
acceptable floor.

### Portuguese verification

Wook, Bertrand, Fnac and Almedina defeat automated fetches, and the BNP
**ipac20** catalogue answers to a browser User-Agent (CURATION §4 carries the
correction and the "blocked the way we asked" lesson). The editions-specific
consequences:

- **Two independent sources agreeing is the working standard for an ISBN.**
  Publisher catalogues, author sites and library records, cross-checked.
- **Do not substitute a fetchable-but-unreliable portal.** The Tordo run tried
  `portaldaliteratura.com` because it was reachable, and found it attributes
  Bruno Vieira Amaral's *Toda a Gente Tem um Plano* to Tordo. Reachability is
  not a quality signal, and an aggregator with one visible error has others.
- **Some facts need a human with a browser, and that is an acceptable
  outcome.** Say so in the PR: name the specific books, the unverified fact,
  and the page a human should open. That is a useful deliverable. A guessed
  ISBN is not.

**Never scrape a retailer's jacket image, and a retailer image laundered
through a permitted host is still a retailer image** (§4). `coverUrl` is
optional and the app degrades by design; read the "Image rights" section of
`docs/SCHEMA.md` and the `visual-metadata` skill before writing any `coverUrl`,
and leave it null if in doubt.

## Auditing existing editions

Adding is half the job. Run these checks over any franchise you touch, and over
the whole catalogue periodically. Each has produced a real defect somewhere.

**1. Check digits.** Recompute every one. CI makes a red build the easy case;
the dangerous case is a valid-but-wrong number, which only a source cross-check
catches.

**2. Region mismatches.** Every `pt-PT` entry against the prefix table. One
`97885` in a Portuguese file is a reader sent abroad.

**3. Orphaned editions.** `workId` must resolve. Work ids are immutable by
policy, but a franchise restructure or a slug fix breaks the link, and an
orphaned edition is invisible in the app while sitting in the file looking
complete. The validator catches this one - run it.

**4. Works added later with no edition.** A completeness audit that adds twelve
works to `works.yaml` silently drops edition coverage. Recompute the fraction
after any works change and update the header comment; a stale "COVERAGE: 22 of
26" line is worse than none, because the next agent trusts it.

**5. Stale in-print claims.** Publishers delist; an edition recorded as current
in 2024 may be gone. Re-check the publisher page for the newest year in the
file when auditing, and note the check date.

**6. Duplicate ISBNs.** The same number on two entries means one is transcribed
wrong or an omnibus was split into two fake editions. The validator does not
check this across works; check it yourself.

**7. Titles that drifted.** An edition `title` should match the jacket, not the
work title translated after the fact. Spot-check any title that reads like a
literal translation of the English - the fingerprint of the error this skill
exists to prevent.

## Hard rules

- **Never guess an ISBN.** Not a digit, not a prefix, not a "probably the next
  one in the series".
- **Never translate a title.** Only ever record a title printed on a real cover.
- **Never tag a Brazilian edition as Portuguese**, or any edition with a region
  you did not verify.
- **Never edit a digit to make CI pass.** If the check digit fails, the number
  is wrong or the entry does not ship.
- **Editions are never overlaid by i18n.** Do not add `content/i18n/.../editions.yaml`;
  the validator forbids `title`, `isbn13`, `language` and `workId` in overlays
  precisely so a translation pass cannot invent a book.
- **Touch only `editions.yaml`.** Not `works.yaml` titles, not `externalIds`,
  not synopses. If you find an error in a work record, report it in the PR and
  leave it.

## Process

1. Read `docs/SCHEMA.md` (editions, language codes, published titles), the
   franchise's `works.yaml`, and any existing `editions.yaml`.
2. **Establish the publishing history before looking up a single ISBN**: which
   houses hold the rights in the target language, over what years, and where
   the run stops. That frame tells you whether a missing book is a research gap
   or a market fact.
3. Work through the publisher catalogue first, then national library records,
   then retailer bibliographic blocks. Open each record individually.
4. For each candidate: **verify the check digit, verify the prefix region,
   verify the title against the jacket, and match the work by synopsis rather
   than by title.**
5. Write the entries, led by a header comment stating the sources, the scope
   rules applied, the coverage fraction, and any non-literal title pairs - the
   Christie, Discworld and Wheel of Time headers are the model.
6. Run `python scripts/validate.py` until green, then re-check coverage against
   `works.yaml` and confirm no ISBN appears twice.
7. Write the PR body.

## Done means

A green `scripts/validate.py`; every ISBN check-digit verified **and** traced
to a named record you actually opened; every `language` confirmed against the
registrant prefix; every `title` copied from a jacket rather than translated; a
file header stating sources, scope and the honest coverage fraction; every
deliberate omission (no ISBN, out-of-print only, no edition at all) explained
in a note or comment where the next agent will find it; and a PR body that
reports coverage as n/total, names every fact a human with a browser still
needs to confirm, and lists every problem found in existing data and not fixed.

An `editions.yaml` with six honest entries ships. One with sixty entries and a
single guessed ISBN does not.
