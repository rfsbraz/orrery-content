---
name: translation
description: Translate Orrery's curated prose into a locale via overlay files keyed by stable id - covering what may and may never be overlaid, region-strict locales like pt-PT, register, and the coverage gates that catch prose which never reaches the reader. Use when writing or reviewing content/i18n/<locale>/, when English prose changes and invalidates its translation, or when adding a new locale.
---

# translation

Write and review the overlays under `content/i18n/<locale>/`. Read the
**Translations** section of `docs/SCHEMA.md` in full first: it is the contract.
This skill is the judgement the schema cannot encode - what a good translation
is, and the specific ways translation work has silently failed here before.

This skill runs under `docs/CURATION.md`; the shared contract is stated there,
not repeated here.

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

## The overlay model

`content/i18n/<locale>/` mirrors the content tree file for file. Nothing is
copied wholesale: an overlay entry carries the **stable id** plus **only the
fields being translated**, and the engine merges base and overlay **field by
field**.

```yaml
# content/i18n/pt-PT/franchises/stephen-king/works.yaml
- id: stephen-king/carrie
  synopsis: "Uma rapariga com poderes telecinéticos vinga-se de forma catastrófica na noite do baile."
```

Two consequences worth internalising, because they shape how you work:

- **Partial coverage degrades per field, never per page.** A franchise with a
  translated description and untranslated synopses renders the description in
  Portuguese and the synopses in English. It does not break and it does not go
  blank. So translating the highest-value prose first is a legitimate strategy,
  not a half-finished job.
- **Nested id-bearing lists merge by id**, not by position. An author's
  `lifeEvents` and a franchise's `startHere.paths` each carry their own id, and
  a translation restates only prose inside them - never `workIds`, `orderId`,
  `fit`, dates, or impact. Position is not identity: reordering the base list
  must not silently re-point a translation.

```yaml
- id: stephen-king
  description: "..."
  startHere:
    paths:
      - id: essentials
        title: "Os essenciais"
        description: "..."
        note: "..."
```

## What must never go in an overlay

The validator rejects `id`, `sources`, `isbn13`, `language`, `workId`
everywhere, and `title` inside `works.yaml` and `editions.yaml`. The first five
are obvious once stated - identifiers and source URLs are not prose. The title
rule looks arbitrary and is the most important one here.

> **A published title is edition data, not translation.**

A work's `title` is its **original** title and never changes. If a Portuguese
edition of a work exists, that edition carries its published Portuguese title in
`editions.yaml`, with the ISBN of a book someone can actually buy. If no
Portuguese edition exists, the work simply **has no Portuguese title**, and the
app shows the original. Translating the title in an overlay would invent a book
that does not exist and send a completionist reader after it - the one failure a
catalogue like this can never afford.

This is why **editions are deliberately not overlaid at all**. An edition is a
set of facts about a physical object. There is nothing in it to translate.

The mirror of the rule: era titles, event titles, nested `lifeEvent` titles and
`startHere` path titles **are** curated prose written by the curator, and are
translated like any other prose. `name` is a proper noun everywhere except on an
order, where it is a curated label a reader reads.

Where a work genuinely has no published translation, say so in a comment rather
than leaving the next translator to rediscover it:

```yaml
# Flight or Fright has no Portuguese edition, so the English title stands.
```

Keep the inline references intact. Translate the display text after the pipe and
never the id: `[[work:stephen-king/the-stand|A Dança da Morte]]`.

## Region-strict locales

`pt-PT` is not `pt-BR`. They are different translations, by different
translators, with different titles and different ISBNs. Tagging a Brazilian
edition `pt-PT` sends a Lisbon reader to a book they cannot buy. The same
applies to `en-GB` versus `en-US` wherever titles genuinely differ. Where region
is irrelevant to books, a bare code (`fr`, `de`, `it`) is fine.

Prose has the same split, and it is what actually catches a bad translation in
review. Discriminators for pt-PT:

**Never - these read as Brazilian instantly:**

| Wrong (pt-BR) | Right (pt-PT) |
|---|---|
| está lendo, vai chegando | está a ler, vai chegar |
| quadrinhos | banda desenhada |
| roteiro | argumento |
| beisebol | basebol |
| tela | ecrã |
| ônibus | autocarro |
| banheiro | casa de banho |
| celular | telemóvel |
| arquivo (a file) | ficheiro |

Progressive gerund constructions are the loudest tell. `estar` + gerund is
Brazilian; European Portuguese uses `estar a` + infinitive. Note that adverbial
gerunds are perfectly correct in pt-PT ("levando cada juramento ao ponto de
rutura"), so grep for the auxiliary, not for `-ndo`.

One trap runs the other way: **`rapariga` is neutral and ordinary in Portugal
and a slur in Brazil.** Region-correct is not the same as globally safe, which
is exactly why the locale carries its region.

**The positive form of the same rule.** Avoiding Brazilianisms only gets you
prose that is not wrong. Aim for the idiom a native would actually reach for.
The Carnation Revolution entry in `events/global.yaml` says the Estado Novo
subjected every book and newspaper to the **"lápis azul"** - the real censor's
blue pencil, the phrase a Portuguese reader grew up with. A correct translation
would have said "censura prévia" and been fine. "Lápis azul" is the difference
between prose that was *written* and prose that was *converted*.

## Register, not just correctness

Match the length and tone of the entries around it. A synopsis that balloons to
twice the English is a rewrite, not a translation - and it will look wrong on
the page, where entries sit next to each other and the eye reads the ragged one
as a mistake.

Terse base prose stays terse. Curatorial dryness stays dry. If the English says
something in nine words, needing twenty-five in Portuguese usually means you
have explained rather than translated.

## Neutrality survives translation

A global event's description must read correctly under **every** author's page,
in Portuguese too. The neutrality that `world-events` enforces on the English is
easy to lose in translation, because the translator has one franchise in front
of them and writes for it.

The related trap: where an entry is anchored to a UK or US event, the Portuguese
must not quietly imply it happened in Portugal. The Lady Chatterley verdict was
a London jury and a limit on what an English-language novel could describe; a
Portuguese reader must not come away thinking it changed Portuguese law. Name
the place when the place is load-bearing.

## Coverage is a gate, not a report

CURATION §3 owns the numbers: record `i18n_coverage.py` before starting, no
regression after, and an English rewrite is fixed on both sides in the same
commit. The translation-side consequence: a commit that improves an English
synopsis and leaves the Portuguese saying the old thing has not improved
anything - it has introduced a contradiction only a bilingual reader will find.

### The gate is narrower than it looks - do not read "complete" as "translated"

The script counts a file as covered when the fields **it knows about** are
present. It has reported a confident **58/58 fully covered** while, on that same
build:

- **era `themes` were untranslated on every single wing.** The overlay carries
  `title` and `description`, the script is satisfied, and the reader sees
  `insomnia and dissociation · performed masculinity` in English under a
  Portuguese era title. Translate `themes`; they are prose.
- **all 11 achievement badges rendered in English**, and not because nobody
  translated them: `listAchievements()` takes no locale and never consults the
  overlay, so they are *untranslatable* until the app changes. Not your bug to
  fix, but do not let a green number tell you it is not happening.
- **labels rendered from app code** - the derived order's name
  ("Complete, in publication order"), a hardcoded `entering` on the era plate -
  are invisible to a content coverage script by construction.

So: **100% from this script is a floor, not a finish.** Open the rendered page in
your locale and read it before you claim the wing is done. Every one of the above
was obvious on sight and invisible to every check we had.

## The traps that actually happened

Each of these passed CI.

**1. Green CI, invisible prose.** Author `lifeEvents` could be written nested
under the author entry or flat as sibling entries. Both shapes validated. The
loader only merged the nested shape, so **three of six author files rendered in
English while passing every check**. The loader now accepts both. The lesson
outlives the bug: **a validator proves shape, not delivery.** Nothing in a
schema check tells you a reader saw the string.

**2. Counting the wrong thing.** The coverage script once counted only
top-level fields and reported a confident 48/48 while five franchises had
visibly English `startHere` prose on the page. A metric that is wrong in the
reassuring direction is worse than no metric, because it ends the
investigation. The script now counts nested prose; when you extend the schema
with a new prose-bearing structure, extend `count()` in the same commit.

**3. Content that belongs to no franchise.** Translation work gets split by
franchise, because that is how the content is shaped. Everything that belongs to
**no** franchise then has no owner: the shared `content/events/global.yaml`, the
co-author bios, the character rosters, the home page's author descriptions. All
of it sat in English long after the locale was called done, because every
translator had been handed a franchise. This failure is precisely why
`i18n_coverage.py` exists - it walks the base tree, not the franchise list.

**4. Account-only surfaces.** A sweep of the live site misses everything behind
sign-in, because the sweeper is not signed in. Progress pages, reading lists,
achievement text and settings all need an authenticated pass.

**5. Static `metadata` cannot reach a locale.** A Next.js `export const
metadata` object is evaluated without a request, so it cannot know the reader's
locale and will ship English titles and descriptions to every locale forever.
Any localised page needs `generateMetadata` instead. Nothing in the content repo
can detect this; you have to look at the route.

**6. The live sweep and the source scan see different things.** They are not
redundant and neither alone is sufficient:

| | catches | misses |
|---|---|---|
| **Live sweep** (read the rendered pages) | prose that fails to reach the reader - overlay merge bugs, unresolved ids, loader shape bugs | strings that were never added to the catalogue at all |
| **Source scan** (grep the content and app) | strings that never entered the catalogue - hardcoded UI text, missing overlay entries | prose that is present in source but silently not merged |

Run both.

## Verification

Check the **rendered output**, not the report. Open the pages in the target
locale - a franchise page, an author page, the home page, and at least one
account-only surface - and read them. The coverage script tells you a file
exists and has entries; it cannot tell you the reader saw them, and trap 1 is
exactly that gap.

State plainly what you checked and how. Claims and green validators are not
evidence (CURATION §5); a quoted line of Portuguese from a rendered page is.

## Adding a new locale

1. **Region from day one.** Decide `pt-PT` versus `pt-BR`, `en-GB` versus
   `en-US`, at creation. Retrofitting a region onto a bare code means auditing
   every string already written for which variety it was written in, and that
   audit is far more expensive than the decision.
2. **Content side:** create `content/i18n/<locale>/` mirroring the base tree.
   Partial is fine - start with franchise descriptions, era descriptions,
   high-impact event descriptions, then synopses. `i18n_coverage.py` picks up
   the new locale automatically.
3. **App side:** add the locale to the list in `lib/i18n/config.ts`, wire its
   route segment, and add its `hreflang` alternates so search engines and
   language switchers can see it. A locale with content and no routing is
   invisible; a locale with routing and no `hreflang` is invisible to search.
4. **Editions:** check whether published editions exist in that market and add
   them to `editions.yaml`. This is what gives the locale real titles instead of
   original-language fallbacks - and it is content work, not translation work.
5. Run `python scripts/validate.py` and `python scripts/i18n_coverage.py`, then
   render and read a page.

## Hard rules

- **Never translate a published title.** No `title` in `works.yaml` or
  `editions.yaml`. If a translated title exists, it belongs to a real edition.
- **Never touch ids**, slugs, `sources` URLs, `isbn13`, `language`, or `workId`.
  An overlay id that does not resolve is a CI error, by design.
- **Never restate structure** in a nested translation - no `workIds`,
  `orderId`, `fit`, dates, or impact.
- **Diacritics are content, not decoration.** `instituições`, not
  `instituicoes`. Proofread the rendered text, not the diff.

## Done means

A PR whose body states: the **coverage number before and after** with the
command output, and an explicit statement that it did not regress; **which
surfaces were rendered and read** in the target locale, including at least one
account-only page, with a quoted line as evidence; every **English string
changed alongside its translation**, named; every place a **title was left in
the base language** and why (no published edition, or the title is identical in
that market); any **region-discriminator call** that was close enough to be
worth flagging for a native reviewer; and any prose the overlay model **could
not express**, so the gap is visible rather than quietly absent.
