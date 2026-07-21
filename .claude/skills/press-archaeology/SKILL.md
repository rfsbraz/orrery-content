---
name: press-archaeology
description: Dig contemporary press, interviews, obituaries, prize coverage and trade reporting for the specific, dated, sourced facts that make an author's aura real - the things a bibliography cannot tell you. Use when enriching an author's lifeEvents or a franchise's events.yaml, or when a franchise reads accurate but flat.
---

# press-archaeology

Read what was **written at the time** about an author, and bring back the handful
of dated, sourced facts that change how their books read.

This skill runs under `docs/CURATION.md`, the shared contract for every
curation stage; its rules are not repeated here.

Every other agent in this pipeline works from records: bibliographies, catalogues,
library metadata, cover databases. Records tell you *what exists*. They cannot
tell you that a book was written in a hospital bed, that a publisher dropped the
author two months before the novel that made them, that two writers stopped
speaking, or that the thing everyone repeats about a famous book is a story the
author later denied. That lives in interviews, contemporary reviews, obituaries,
prize coverage and trade reporting, and this skill is how it gets in.

Read `docs/SCHEMA.md` (authors, `lifeEvents`, events) first. The **aura
editorial standard** (`docs/CURATION.md` §6) is the bar. This skill is about
*sourcing*, not about lowering it.

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

## Output

Two things, and keep them separate.

**1. Content changes** - the facts that earned a place, emitted as YAML into the
right file: `content/authors/<id>.yaml` (`lifeEvents`) for the author's own life,
`content/franchises/<slug>/events.yaml` for things that belong to the franchise,
and nothing into `content/events/global.yaml` (that file is the `world-events`
skill's, and its bar is higher).

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
