---
stage: completeness-auditor
summary: "Audited jim-butcher: added 2 missing novellas (32 -> 34 works), verified Codex Alera 2-5 and Twelve Months against primary sources, defused a Storm Front dating trap, flagged 3 co-edited anthologies for curator scope"
---

## Works added

- **jim-butcher/the-law** ("The Law", 2022, apocrypha). A real gap: an
  Audible-exclusive novella (Butcher narrating) with a limited Subterranean
  Press print run, standalone, never inside an anthology - exactly the shape
  of the Backup/Warriorborn entries already in the file, just missed. Sources:
  jim-butcher.com's own 2022 announcement, Goodreads, ISFDB. Retailers
  disagree on its numbered slot (Goodreads #17.2, Amazon 17.5, ISFDB 17.7);
  recorded the disagreement in a note rather than picking one.
- **jim-butcher/out-law** ("Out Law", 2026, apocrypha). Published by Podium,
  May 5 2026 (208pp, ISBN 979-8347030026), set during Twelve Months per
  Library Journal's review. Same standalone-novella shape as The Law. Sources:
  jim-butcher.com's 2026 post, Library Journal, ISFDB.

Both were invisible to the scaffold's Wikipedia/jim-butcher.com sweep because
neither has a Wikipedia article and jim-butcher.com files them as blog posts,
not book pages - ISFDB's chapbook listing is what surfaced them.

## Corrections

- **Storm Front dating trap defused, no change.** ISFDB's title record dates a
  Buzzy Multimedia audio edition to 1997 - three years before Storm Front even
  had a print publisher. That edition's own Audible listing carries a 2002
  phonogram copyright, which cannot postdate the actual release; 2000 (Roc) is
  confirmed as first publication. Added a note on the entry so the next
  auditor who hits that ISFDB record doesn't re-litigate it.
- **Codex Alera books 2-5, verified, no change.** Wikipedia's Jim Butcher
  bibliography table is built from citations to jim-butcher.com's own
  contemporaneous press releases ("Furies of Calderon is available for
  presale", "Cursor's Fury Hits the Shelves", etc.), not just secondary
  summary - this clears the primary-source bar the scaffold left open.
  Academ's Fury 2005, Cursor's Fury 2006, Captain's Fury 2007, Princeps' Fury
  2008 all confirmed correct.
- **Twelve Months, verified, no change.** Real, correctly titled, January 20
  2026 per both jim-butcher.com's own release-date listing and Wikipedia.

## Considered and rejected

- **Third Cinder Spires novel**: re-checked risingshadow.net and
  jim-butcher.com; still no title, no confirmed date beyond a retailer
  placeholder year. Does not clear the `forthcoming` sourcing bar. Stays
  uncatalogued, per the scaffold's original call.
- **"Mirror Mirror" (Dresden #19)**: a new discovery, not in the scaffold
  handoff. jim-butcher.com's own site names it and shows a 42% progress
  indicator, but gives no release date. Same rule as the Cinder Spires book:
  not catalogued until a sourced date exists.
- **Anthology-only short fiction** ("Fugitive" 2023, "Little Things" 2022,
  "Mister Petty" 2026, "Monsters" 2019, "Small Problems" 2017 in Larry
  Correia's Monster Hunter International anthologies, and the microfiction
  "Year of Dresden" pieces): all confirmed anthology-only or free web
  fiction via Wikipedia's Dresden short-fiction article and ISFDB. Correctly
  excluded per the file's existing rule.
- **A foreword for "Mystic" (2024), an introduction for Paranormal Payback
  (2026), and a 2004 Stargate nonfiction essay**: single contributions to
  other people's books, well below even the anthology-story bar. Rejected,
  no escalation needed.

## Flagged for the curator, not decided here

Butcher has **co-edited three multi-author anthologies with Kerrie Hughes**
(confirmed via ISFDB's editor credits): Shadowed Souls (2016), Heroic Hearts
(2022), Paranormal Payback (2026) - each containing one of his own Dresden
stories, and two of them (Shadowed Souls, Paranormal Payback) also his own
foreword/introduction. This is squarely the `authorRole: editor` case the
schema describes and the scope question CURATION.md reserves for the curator
(multi-author anthology, editor role). Left uncatalogued pending that call;
all three titles, years and his own contribution are sourced above so no
re-research is needed either way.

## Housekeeping

Fixed the works.yaml line-4 comment-policy warning (the word "completeness"
tripped the pipeline-vocabulary scanner even though it was a data statement,
not process narration); reworded without the trigger word.

## Validation

`python scripts/validate.py --slug jim-butcher`: 0 errors beyond the expected
pre-existing `theme.art` gap, 0 warnings (the one pre-existing warning is
fixed). `aura_density.py jim-butcher`: unchanged shape, still routes to
press-archaeology, not this stage's job. `i18n_coverage.py`: no regression
(no translation exists yet for this wing).

**Work count: 32 -> 34.**
