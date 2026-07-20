---
name: press-archaeology
description: Dig contemporary press, interviews, obituaries, prize coverage and trade reporting for the specific, dated, sourced facts that make an author's aura real - the things a bibliography cannot tell you. Use when enriching an author's lifeEvents or a franchise's events.yaml, or when a franchise reads accurate but flat.
---

# press-archaeology

Read what was **written at the time** about an author, and bring back the handful
of dated, sourced facts that change how their books read.

Every other agent in this pipeline works from records: bibliographies, catalogues,
library metadata, cover databases. Records tell you *what exists*. They cannot
tell you that a book was written in a hospital bed, that a publisher dropped the
author two months before the novel that made them, that two writers stopped
speaking, or that the thing everyone repeats about a famous book is a story the
author later denied. That lives in interviews, contemporary reviews, obituaries,
prize coverage and trade reporting, and this skill is how it gets in.

Read `docs/SCHEMA.md` (authors, `lifeEvents`, events) and the **aura editorial
standard** in the `franchise-research` skill first. That standard is the bar.
This skill is about *sourcing*, not about lowering it.

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

## Sourcing rules, and they are strict

- **Two independent sources for anything about a living person's health,
  finances, family, addiction, or legal trouble.** One source is a rumour with a
  URL. This is not pedantry: these are real people, several of them alive, and a
  sourced-once claim about someone's drinking or divorce is not something a
  reading-order site should be publishing.
- **Never launder a citation.** If Wikipedia says it and cites a newspaper, cite
  the newspaper *after reading it*. Citing the source you did not open is how
  errors propagate with false authority.
- **Date everything.** An undated fact cannot be placed on a timeline, which
  makes it useless here regardless of how good it is.
- **Distinguish claim from fact.** "King has said he has no memory of writing
  *Cujo*" is reportable and true. "King does not remember writing *Cujo*" asserts
  something you cannot know. Attribute in the prose when the evidence is an
  author's own account.
- **Paywalls and dead links.** If you cannot read it, you cannot cite it. Prefer
  an archived copy; if none exists, drop the fact rather than trusting a snippet.
- **Anniversary and listicle content is not a source.** "10 things you didn't
  know about X" recycles errors. Go to what it recycled.

## Living authors, and restraint

Most of this catalogue's authors are alive. Two consequences:

- **Ask whether the author put it in public themselves.** An illness discussed in
  an interview is fair; an illness inferred from a cancelled tour is not.
- **Distress is not content.** Include a hard fact only when it genuinely changes
  how the books read, which is the same test as everything else in the aura.
  Where it does, write it plainly and without appetite. Where it does not, leave
  it out, even when it is true and well sourced.

For the recently dead, the obituary window is a gift: a great deal gets said
carefully, once, and then never revisited.

## Density: this is an enrichment pass, not a biography

The aura's job is to be sparse and load-bearing. A franchise that gains twenty
life events has been made worse, not better.

| Scope | Target |
|---|---|
| `lifeEvents` per author, total | roughly 6-12 across a career |
| New facts per press run | **3-8 that survive the aura standard** |
| Corrections to existing content | as many as you find, always report them |

If you come back with two excellent facts and one correction, that is a good run.
If you come back with thirty, you have written a Wikipedia article and the
curator has to do your editing for you.

## Output

Two things, and keep them separate.

**1. Content changes** - the facts that earned a place, emitted as YAML into the
right file: `content/authors/<id>.yaml` (`lifeEvents`) for the author's own life,
`content/franchises/<slug>/events.yaml` for things that belong to the franchise,
and nothing into `content/events/global.yaml` (that file is the `world-events`
skill's, and its bar is higher).

**2. The findings report** - in the PR body, and this is half the deliverable:
- each fact added, with its source and why it passes the aura standard
- **each correction**, with the wrong version, the right version, and the
  evidence. Flag it loudly if the wrong version is currently live in our content.
- **facts you found and rejected**, with the reason. This stops the next agent
  re-researching the same dead ends.
- **what the record does not contain.** For sparse or non-English authors this is
  the most useful paragraph in the report: say which archives you could reach,
  which blocked you, and what a human with a library card could find that you
  could not.

## Hard rules

- **Never fabricate.** Not a date, not a quote, not a publication. A plausible
  invented fact is the worst possible output of this skill, because it is exactly
  the kind of thing nobody downstream will think to check.
- **Never fabricate a source URL.** Fetch it. If the fetch fails, say so.
- **Uncertainty goes in a `note:`, not into confident prose.** "Sources disagree
  on whether X" is publishable; silently picking one is not.
- **Spoiler-check every entry.** A life event can spoil a book (a real death
  inside a novel's frame, the fate a memoir gives away). Use `spoilerAfter`.
- **Stable ids are permanent.** Adding an event never renames an existing one.
- **Translations exist.** New prose leaves `content/i18n/<locale>/` incomplete.
  Run `python scripts/i18n_coverage.py` and either fill the gap or report it.
- No em dashes. Quote YAML values containing colons, apostrophes, or `?`.
- `python scripts/validate.py` green before you finish.

## Done means

A PR whose body a curator can act on without repeating your research: every fact
sourced and dated, every correction evidenced, every rejection explained, and an
honest account of what the record would not give you. Plus green validation and
no translation regression.

The measure of a good run is not how much you found. It is whether a reader who
already knew this author learns something true.
