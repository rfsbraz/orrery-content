---
name: press-archaeology
description: Dig contemporary press, interviews, obituaries, prize coverage and trade reporting for the specific, dated, sourced facts that make an author's aura real - the things a bibliography cannot tell you. Use when enriching an author's lifeEvents or a franchise's events.yaml, or when a franchise reads accurate but flat.
---

# press-archaeology

Read what was **written at the time** about an author, and bring back the handful
of dated, sourced facts that change how their books read.

This skill runs under `docs/CURATION.md`, the shared contract for every
curation stage; its rules are not repeated here.

## Cheap tools before expensive habits (this stage pays for its own calls)

Every tool call re-sends your whole context, so what a stage costs is roughly
its context multiplied by how many calls it makes. One wing's editions stage
made 144 sequential fetches; the pages were not the expense, fetching them one
at a time was. Three habits, before you start:

- **Editions and visual-metadata: reach for `scripts/metadata/lookup.py` FIRST.**
  For those two stages the whole fetching half is already one tool call:
  `python scripts/metadata/lookup.py <slug> --author "<name>"` sweeps the
  registered providers and prints a TSV of edition and cover candidates for the
  entire wing (`--verify-isbns` checks an existing `editions.yaml`,
  `--check-covers` HEADs every cover, `--markets no,en,pt` widens the search,
  `--json` when something parses it). Measured on the Jo Nesbo wing it replaced
  ~360 sequential fetches (~880k tokens, 57 min) with ~40 HTTP requests inside
  one call. It does **not** replace the stage's judgement - which market, is
  this an omnibus, is this a title-page scan - and every real catch on the wings
  built so far was one of those, not a lookup. So run it, then judge the table.
  A source it does not cover yet is one provider class in
  `scripts/metadata/providers.py`; add it there rather than hand-fetching around
  it. The rest of this section still applies to the verification fetches the
  table sends you back for.
- **Every other stage: fetch in batches, not one by one.** `python scripts/fetch.py URL [URL...]`
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
  reference crosses wings - only the warning list narrows). This one is
  measured and still gets missed: one wing build ran eleven catalogue-wide
  validations where ten could have been scoped, each re-reading 40+ untouched
  wings to prove one file parses,
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

## The one event that is not a press fact: the birth

**Every author's timeline opens with their birth, and this stage owes it.** The
first `lifeEvent` is dated to the author's `born` date, titled with the place
("Born in Providence, Rhode Island", "Born in Oslo, raised in Molde"), and
carries the childhood geography that follows it - where they were born, where
they were actually raised, and what that place later became in the books.

It is not in the ranking below, and that is exactly why it kept going missing:
the ranking is a *press* ranking, a birth is not press, so an agent working the
list correctly skipped it and six wings opened mid-career - one on a second
marriage, one on selling package tours. `validate.py` warns when an author with
`lifeEvents` has none dated to `born`. Grade it `low`; a birth is a floor, not
a rupture. `full-bleed-vista` is its natural organisation (docs/LAYOUT.md lists
"birthplace" as its first use), unless the next cell is loud - two loud cells
cannot touch, so `beside` with a `place-portrait` is the quiet alternative.

## What you are looking for

Ranked by how much they change a reading. Spend your effort at the top.

1. **The inner weather.** Illness, addiction, grief, money terror, a marriage
   ending, a breakdown, a recovery. The conditions the writing happened under.
   These recolor sentences.
2. **Origin stories that are actually true.** Where a book came from, in the
   author's own words, with a date and a venue. Verify the famous ones: a
   startling number of "how I wrote it" anecdotes are later inventions or
   journalist embroidery.
3. **Career ruptures.** Rejected, dropped, bankrupted, sued, banned, filmed,
   suddenly rich. The events that visibly change what the author writes next.
   **A pen name is one of these, checked separately from everything else
   here.** `franchise-research` records `pseudonyms` with a `note` explaining
   why one exists; that note is not an event, and this stage owes the dated
   one. For every entry with a real adoption motive or a reveal, check
   whether either end has its own `lifeEvent` - not whether the pseudonym is
   *mentioned* somewhere, whether the moment is dated and sourced. This
   shipped wrong twice in the same audit: Richard Bachman had a 1985
   unmasking event but nothing dated the 1977 adoption and its actual motive
   (testing whether success was talent or luck), and Mary Westmacott had no
   dated event on either end - worse, the note's own exposure year was
   simply wrong (1949, corrected to 1946 against the Christie estate's own
   site) and nothing near it was ever checked closely enough to catch it. A
   pseudonym with no real story - a shared house name, a boyhood byline -
   does not need this: if the note states only what happened (which books,
   which years) with no stated motive and no reveal, it stays a note.
4. **Reception at the time, where it differs from reception now.** A book savaged
   on publication and canonised later, or the reverse, tells a reader something
   the current blurb never will.
5. **Feuds and alliances, but only with a mark on the canon.** A quarrel matters
   if it changed a book, a pen name, a publisher, or a dedication. Otherwise it
   is gossip.
6. **Corrections.** Places where the received story is wrong. These are among the
   most valuable things you can bring back, and nobody else in the pipeline is
   looking for them.

## Where to look

Prefer sources that were **contemporary to the event**, then sources with
editorial accountability, then everything else.

- **Newspaper and magazine archives** - the paper of record for the author's
  country, plus the literary press. Interviews at publication time are the
  richest single vein.
- **Obituaries**, for dead authors. A good obituary is a researched, fact-checked
  life in one document, and it will name the turning points for you.
- **Prize coverage** - shortlist and award reporting is dated, specific, and
  usually quotes the author.
- **Trade press** (Publishers Weekly, The Bookseller, and national equivalents)
  for the career mechanics: advances, deals, moves between publishers, print runs.
- **The author's own words** - collected interviews, memoirs, forewords, letters.
  Treat these as primary but not neutral: authors curate themselves.
- **National broadcasters and cultural institutions**, especially outside English.

**Language follows the author.** For a Portuguese novelist the useful record is
Portuguese: Público, Expresso, Observador, RTP, and the national library. For a
Japanese or Brazilian or Nigerian author, likewise. An anglophone search on a
non-anglophone author returns a thin, distorted picture and you must not mistake
that thinness for a quiet life. This is the single most common failure of this
skill.

## Sourcing rules, the press-specific ones

The general sourcing law is CURATION §4 and §6 - two independent sources for
anything about a living person's health, finances, family, addiction or legal
trouble; never launder a citation; paywalled or dead means uncitable;
listicles are not sources. On top of it:

- **A rejection note names the source and the bar it failed, never the claim.**
  You handle the categories most likely to fail the two-source test, so you are
  the stage most likely to write a rejection note - and everything here is
  public, comments and PR bodies and git history alike. Holding a claim out of
  the data and then explaining the rejection in the claim's own words publishes
  it anyway, under our name, permanently. Write "a single first-person telling,
  held out under the two-source bar, and not to be added from that source
  alone"; the next pass needs nothing more than that to leave it alone. A
  self-disclosure is not an exemption. See CURATION §6 - this rule exists
  because this stage broke it.
- **Distinguish claim from fact.** "King has said he has no memory of writing
  *Cujo*" is reportable and true. "King does not remember writing *Cujo*" asserts
  something you cannot know. Attribute in the prose when the evidence is an
  author's own account.
- **Spoiler-check every entry.** A life event can spoil a book (a real death
  inside a novel's frame, the fate a memoir gives away). Use `spoilerAfter`.

## Living authors, and restraint

Most of this catalogue's authors are alive. The test that decides the hard
cases: **ask whether the author put it in public themselves.** An illness
discussed in an interview is fair; an illness inferred from a cancelled tour is
not. And distress is not content (CURATION §6): where a hard fact earns its
place, write it plainly and without appetite; where it does not, leave it out,
even when it is true and well sourced.

For the recently dead, the obituary window is a gift: a great deal gets said
carefully, once, and then never revisited.

## Interviews and articles: promotion is not a moment

An interview or feature is a **source**, not automatically a **subject**. Every
origin story already in this catalogue came from one - Bryndza's "if I didn't
do it soon, I never would" pivot into crime, the Kate Bush *50 Words for Snow*
seed for *The Girl in the Ice*, Rowling's Guardian disclosure. That's not new.
What's worth naming explicitly is the bar, because authors do press for every
book, and a wing over-mined for coverage produces exactly what this stage
exists to prevent: entries that are really just publicity with a date on them.

**An interview or article earns its own aura entry only when it is the origin
or first disclosure of something that reshapes how a specific work or era is
understood** - a stated inspiration named nowhere else, a revealed
writing-process fact, a correction to the received story (item 6 above), a
controversy that measurably changed reception. Never because the author *did*
press for a book; every book on the shelf has press.

**The test: if you removed the interview, would the fact still be knowable
some other way** (jacket copy, a plot summary, common knowledge)? If yes, it
isn't aura, it's promotion - it belongs in `sources:` on whatever entry it's
supporting, not as an entry of its own. If the fact only exists because the
author said it in that specific piece, and it changes a reading, it clears
the bar.

**Hold the line with a test, not a count.** Don't cap interview-sourced
entries at some number per wing - a wing with three genuine disclosures and a
wing that force-fits three mediocre ones to hit a quota look identical by
count alone. Apply the same test to the tenth candidate as the first.

## Density: sparse, but never dark

The aura's job is to be sparse and load-bearing. A franchise that gains twenty
trivia items has been made worse, not better. But **sparse is not the same as
absent**, and the second failure is the one this catalogue actually has.

**Scale the budget to the career, not to a fixed number.** An absolute
"6-12 per author" cap was the old rule, and applied to a fifty-year, ninety-
five-book career it produced a wing with nine aura entries and a
**twenty-one-year stretch of books with no context at all**. Use instead:

| Scope | Target |
|---|---|
| aura entries per work (franchise events + lifeEvents) | **roughly 1 per 3-4 works**, as a floor to aim at |
| `lifeEvents` per decade of active career | 2-4 |
| New facts per press run | **3-8 that survive the aura standard** |
| Corrections to existing content | as many as you find, always report them |

**The distribution matters more than the count.** Aura entries gravitate to
biographical drama - the accident, the death, the lawsuit - because that is
what the record shouts about. Those cluster on a handful of years and leave
the working middle of a career silent, which is exactly where a reader is
walking the most books. A wing can hit its ratio and still be wrong.

Run `python scripts/aura_density.py` before and after. It reports each wing's
ratio and its **longest run of consecutive publishing years with no aura at
all**. Treat a dark run of five or more years as a question, not a verdict,
and answer it one of two ways:

- **Nobody looked.** Usually the truth. Go and research that period
  specifically rather than adding more around the peaks you already have.
- **The period was genuinely quiet** - steady work, no turning points. That
  is a real finding: record it in the report so the next pass does not
  re-search the same silence, and leave the years empty.

What you must not do is close a gap by promoting trivia. A thin decade filled
with award seasons and sales milestones is worse than an honest silence,
because it teaches readers the aura is decoration. If the only way to light a
decade is to lower the bar, leave it dark and say so.

If you come back with two excellent facts and one correction, that is a good
run. If you come back with thirty, you have written a Wikipedia article and
the curator has to do your editing for you.

**The tool reports only the single worst dark run, never every one over the
line.** Closing the window it names can expose a second, third or fourth one
that was there the whole time, sitting just under the reported figure. Confirmed
on haruki-murakami: `stage_plan.py` flagged one 12-year run; closing it
revealed the wing actually had four separate stretches of five years or more.
Closing all four in the same pass (not just the one named) turned three
expensive later follow-ups into zero. Before calling this stage done, scan the
whole span yourself rather than re-running the tool once and trusting its
single number - remove your own additions one at a time and re-check if you
are not sure whether a second gap is hiding behind the one you just closed.

## Output

Two things, and keep them separate.

**1. Content changes** - the facts that earned a place, emitted as YAML into the
right file: `content/authors/<id>.yaml` (`lifeEvents`) for the author's own life,
`content/franchises/<slug>/events.yaml` for things that belong to the franchise,
and nothing into `content/events/global.yaml` (that file is the `world-events`
skill's, and its bar is higher).

**Leave `organisation`, `illustration_type` and `images_required` unset.**
Those three fields are `art-rotation`'s exclusive footprint (`.claude/commands/
author.md`'s file-footprint table), and the pipeline's own safety property
depends on an unrotated entry looking unrotated - `LAYOUT.md` defaults an unset
`organisation` to a flat `beside`, which is precisely the visible signal that
tells a later pass "this has not been graded yet." A plausible-looking value
filled in here defeats that signal: it ships something that *reads* as rotated
without ever having been checked against the wing's finished art law (which
does not exist yet when you run) or the wing's full timeline (which is still
being written). Confirmed live on a real wing: every one of ten events this
stage created shipped with all three fields pre-filled, and `art-rotation`
only actually touched two of them - the other eight were never truly graded,
they just looked like they had been. If a fact's likely pacing is worth
flagging, say so in the findings report's prose, not in the content fields.

**2. The findings report** - the deliverable doctrine (CURATION §7) applied to
press work: each fact added, with its source and why it passes the aura
standard; each correction, with the wrong version, the right version and the
evidence; the facts found and **rejected**, with reasons; and **what the record
does not contain**. For sparse or non-English authors that last part is the most
useful paragraph in the report: say which archives you could reach, which
blocked you, and what a human with a library card could find that you could not.

## Done means

A PR whose body a curator can act on without repeating your research: every fact
sourced and dated, every correction evidenced, every rejection explained, and an
honest account of what the record would not give you.

The measure of a good run is not how much you found. It is whether a reader who
already knew this author learns something true.
