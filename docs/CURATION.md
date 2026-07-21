# CURATION.md - the house rules for every curation stage

Every skill in `.claude/skills/` runs under these rules. They are stated once,
here, and each skill adds only the judgement specific to its layer. When a rule
here and a skill disagree, the skill is stale - fix the skill.

`docs/SCHEMA.md` is the data contract (what the fields mean, what validates).
This file is the working contract (how curation work is done, verified, and
reported). Read both before any stage.

## 1. The prime directives

**Never fabricate.** Not a book, a date, a quote, an ISBN, a URL, a licence, a
consensus, or a source. Every non-obvious claim carries a source URL you
actually opened. Uncertainty goes in a `note:` or stays out - a plausible
invented fact is the worst output a curation stage can produce, because it is
exactly what nobody downstream will think to check. Finding nothing is a valid,
reportable result.

**Ids are permanent.** Work, era, event, order, character, achievement and
`startHere` path ids are referenced by user progress, achievements, i18n
overlays and cross-references. Rename prose freely; never an id. Choose slugs
deliberately the first time (lowercase, hyphenated, accents stripped; titles
keep their accents).

**Received, not invented.** Wherever a stage makes an editorial claim a reader
will take as established - an era, a reading order, an entry path, a "widely
recommended" - the claim must be received from outside this repo (the author,
the publisher record, criticism, settled community practice), cited. If the
only source is our own reading, it is our opinion in a serif font, and it does
not ship. Fewer, or none, beats coined. The site reports the conversation about
a writer; it does not join it.

**Empty is a supported state.** The framework is opt-in per franchise: no
`editions.yaml`, no orders, no `startHere`, `eras: []`, a bare cover slot - all
of these are complete, correct outcomes that the app degrades for by design.
Never pad a layer to make a wing look fuller. A gap that is documented is
content; a slot filled to close a report is a lie.

## 2. YAML mechanics

- **No em dashes.** Regular dashes, commas, parentheses, or separate sentences.
- **Quote defensively.** Any value containing a colon, an apostrophe, or a `?`
  breaks unquoted somewhere. Quote every URL (they contain `?`, `:`, commas);
  in flow sequences a bare `?x=y` query string parses as a mapping key.
- **Inline references** use `[[work:id|text]]` / `[[author:id|text]]` /
  `[[character:id|text]]` and must resolve; `validate.py` fails on dangling
  ones. Translate the display text after the pipe, never the id.
- **Never commit binaries.** Images are referenced by URL.

### The comment policy: YAML is a data source of truth, not a journal

A comment in a content file may carry **facts about the data** and nothing
else:

- **Sources and citations** - where a value came from, which record was read.
- **Data decision logs** - why this date and not the other, which source
  disagreed and why one was chosen, why a slot is deliberately empty and what
  was checked, a known weakness in a value (a contested boundary, a
  single-source fact), a trap defused for the next reader ("an unrelated early
  story shares this title").
- **Schema-adjacent guidance that travels with the data** - "append-only file,
  parallel PRs merge here".

A comment may **never** carry process or coordination:

- No stage narration ("stage 3 never ran", "the first pass could not", "ran as
  a second pass", "recommended for the next run").
- No pipeline vocabulary about the work itself: which agent produced it, what
  was skipped, what budget ran out, what another stage should do next.
- No status journaling ("as of this run", "still pending", "TODO for the
  curator" - open questions go to the PR body and the curator's list, not the
  file).

The test: **would the comment still be true and useful if the pipeline had
never existed and a human had typed the file by hand?** "No usable cover
exists: checked OL by title and by the author's 611-work sweep" passes. "The
visual-metadata stage could not run this session" fails.

Where process context matters, it lives in the right channel: **handoffs**
(`.orrery/`, deleted before merge) for stage-to-stage coordination, **PR
bodies** for the durable record of what was done and rejected, **git history**
for when and in what order.

`validate.py` warns on pipeline vocabulary inside content comments. The
warning is a question, not a verdict - but answer it before merging.

## 3. Gates: run before, run after, no regressions

Record the numbers **before** starting; every claim of progress is measured
against them.

- `python scripts/validate.py` - green before any stage reports done.
  Pre-existing warnings on other franchises are not yours; new warnings are.
- `python scripts/i18n_coverage.py` - **no regression** against the starting
  number. A stage that adds prose and leaves a locale partial has shipped a
  regression, not a feature.
- `python scripts/event_density.py` - whenever `events/global.yaml` changes.

**English prose changes invalidate translations.** Overlays merge field by
field, so a rewritten base string leaves the old translation live for the
locale reader. A spoiler fix, a date correction, or a rewrite that lands in
one language has not landed.

**The unit that must be consistent is the merge, not every commit.** Fix both
sides in the same commit when you are editing prose directly. But the pipeline
deliberately runs `translation` LAST, because translation copies whatever the
earlier stages settled - so on a stage branch the English necessarily lands
some commits before its overlay, and that is correct rather than a violation.
The rule these two together produce:

> **No merge to `main` may leave base prose and its overlay out of sync.**
> Intermediate commits on a working branch may; the branch tip may not.

A branch built this way is only correct as a whole and must not be split into
per-stage PRs at those boundaries.

## 4. The shared trap registry

Each of these has produced a real defect in this repo. Do not rediscover them.

**Sources and lookups**

- **Negative-control every source before trusting a hit.** Ask it about an
  identifier you invented; if the fabrication comes back looking like a hit,
  every real hit is worthless (`wwnorton.com/books/<isbn>` returns HTTP 200 on
  its own "Page Not Found" page).
- **Never launder a citation.** If an encyclopedia cites a newspaper, cite the
  newspaper after reading it. Wikipedia's **section headings are not a
  periodisation**, its phrasing is not a source's phrasing, and a
  search-result snippet is not a page you read.
- **"Blocked" sometimes means "blocked the way we asked."** Worth one cheap
  retest (a browser User-Agent, a different endpoint) before accepting a zero:
  BNP's ipac20 catalogue serves plain HTML to a browser UA while
  porbase.bnportugal.gov.pt genuinely is a JS app. A documented negative
  nobody retests becomes folklore.
- **Paywalled or dead means uncitable.** Prefer an archived copy; otherwise
  drop the fact.
- **Anniversary listicles and aggregators are not sources.** Go to what they
  recycled. Reachability is not a quality signal.

**OpenLibrary**

- **`?default=false` on ISBN cover lookups**, or a missing cover returns HTTP
  200 with a blank placeholder. (Does not apply to `/b/id/` URLs.)
- Cover URLs answer with **302s that look like failures** until followed to
  the CDN.
- **OL merges pt-BR and pt-PT under one work record** - covers and ISBNs
  cross-contaminate on every Lusophone author. Check the registrant prefix:
  `978-85`/`978-65` Brazil, `978-972`/`978-989` Portugal.
- OL accepts user uploads: **retailer scrapes with watermarks burned in pass
  every HTTP check.** Look at every image. A retailer jacket does not become
  usable by being laundered through a permitted host - the rule is about the
  asset, not the hostname.
- OL work records lie in specific ways: omnibuses, adaptations by other
  authors, translated titles, junk `first_publish_year`. Verify the work
  before using its cover or id.

**Portuguese-market work**

- `pt-PT` and `pt-BR` are **different translations, titles, translators,
  publishers and ISBNs**. Never tag one as the other; mislabelling is worse
  than omitting.
- Wook, Bertrand, Fnac and Almedina block automated fetches. Verification
  rests on publisher catalogues, the national library and the press,
  cross-checked. Two independent sources agreeing is the working standard for
  an ISBN.
- Cite the **record permalink**, not the catalogue homepage.

## 5. Verification doctrine: artefacts, not reports

**Green CI means well-formed YAML. It does not mean the content is true, and
it does not mean a reader saw it.** Real things that passed every check here:
prose that validated but never reached the reader; a coverage script reporting
100% while pages were visibly English; a `spoilerAfter` the engine ignores; a
scripted edit that silently no-op'd while reporting success; covers fetched
and eyeballed into a field the app never read.

So:

- **Check the artefact.** Fetch the URL, open the image, read the rendered
  line, re-derive the number with the repo's own scripts. An agent's summary
  of its own work is a claim, not evidence - including your own.
- **A check must fail before you trust it.** Falsify guards in both
  directions: make the validator fire on the broken case and go quiet on the
  fixed one. A check that only ever produces reassuring output is not a check.
- **Assert before scripted edits.** A `replace` whose target has drifted
  no-ops silently and reports success. Verify the target exists first and the
  change landed after.
- **A suspiciously complete number is a reason to look harder.** A stage
  reporting 100% on everything has usually hidden its awkward cases. Spot-check
  the artefact behind a few random rows.
- **When you rely on a field, grep the app for the code that reads it.**
  Content that validates, renders and is simply never consumed fails nothing
  and does nothing. Inert data is the most dangerous shape on this list.
- **Coverage scripts count what they know.** `i18n_coverage.py` has reported
  full coverage over untranslated era themes and untranslatable achievement
  labels. A number is evidence about the fields the script counts, nothing
  else.
- **Re-verify convenience data from upstream stages.** A fact handed down a
  handoff is a lead, not a source.
- **A "nothing changed" result still gets diffed.** The only proof a no-op was
  honest rather than lazy is the diff showing it.

## 6. The aura editorial standard

The admission test for every event, life event, and aura fact: **does it pass
through the author into the page?** It earns a slot only if knowing it changes
how a reader reads. The impact taxonomy, in editorial terms:

- **high = recolors the text.** After learning it, the same sentences read
  differently. The app renders these as full-bleed interruptions - imagine
  each one breaking the page and ask if it deserves to.
- **med = explains the shelf.** Why the catalogue is shaped the way it is.
- **low = texture of the times.** The weather, kept sparse.
- Fails all three: it does not ship. Every noise event cheapens the real
  anchors.

What changes a reading, ranked - spend effort at the top:

1. **The author's inner weather** - illness, addiction, grief, recovery, fear.
   Most high-impact slots come from here. Write it with care: factual, humane,
   never ghoulish. **Distress is not content** - include a hard fact only when
   it genuinely changes how the books read, and for living people ask whether
   the author put it in public themselves.
2. **Origin stories that are actually true** - verified, dated, in the
   author's own words. Verify the famous ones; many are later inventions.
3. **World events, rarely but decisively** - only where a book *answers* the
   event. Roughly one world event in twenty is aura-worthy.
4. **Feuds and reception ruptures** - only with a mark on the canon.
5. **Industry context** - medium impact at most, never anchors.
6. **Trivia** - cut, unless it secretly belongs to tier 1 or 2.

Density: the aura's job is to be sparse and load-bearing. Approximately 6-12
`lifeEvents` across a career; a wing that gains twenty events has been made
worse. Ten well-chosen anchors beat forty items. **Two independent sources for
anything about a living person's health, finances, family, addiction or legal
trouble** - one source is a rumour with a URL.

## 7. The deliverable doctrine

The report is half the work. Every stage's PR body (or handoff summary)
carries:

- what was **added or changed**, each with its evidence;
- what was **rejected**, with reasons - rejections stop the next agent
  re-researching dead ends and are as much the deliverable as additions;
- what the record **would not give** - archives that refused, facts resting on
  a single source, the specific page a human with a browser should open;
- every **correction** to received wisdom, flagged loudly if the wrong version
  is currently live;
- open questions for the curator - **decisions, not menus**: emit a ruling
  where the record supports one, escalate only what is genuinely the
  curator's call (ordering changes, scope, naming where two labels are both
  right, rights judgement calls, and anything you name as your own weakest
  decision).

**The honest artefact of a complete wing includes the covers that do not
exist, the dates the record will not settle, and the archives that would not
open.** Distinguish *absent* (the record has it, we do not - a finding with an
owner) from *not applicable* (it does not exist to be had - not a deficiency),
so the next round closes real gaps and leaves sparse wings sparse.
