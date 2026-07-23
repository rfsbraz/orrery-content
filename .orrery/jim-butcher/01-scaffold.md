---
stage: franchise-research
summary: "Scaffolded jim-butcher: 32 works across three subseries, author entity, theme (no art)"
---

## What was created

- `content/authors/jim-butcher.yaml`: global entity, born 1971-10-26, 4 lifeEvents
  (birth; the Deborah Chester writing-exercise origin of Storm Front; the 2000
  debut; the Lost-Roman-Legion-and-Pokemon bet origin of Codex Alera). All four
  are well-corroborated and verified.
- `content/franchises/jim-butcher/franchise.yaml`: kind author, themePreset
  streetlamp-noir, globalEvents ruled (1 include, 8 exclude, each with reasoning).
  No `startHere`.
- `works.yaml`: 32 works.
  - **The Dresden Files** (22): 18 novels (storm-front 2000 through
    twelve-months 2026, verified against Wikipedia + jim-butcher.com), Side
    Jobs (2010, extended) and Brief Cases (2018, extended) as collections,
    Working for Bigfoot (2015, apocrypha, folded into Brief Cases) and Backup
    (2008, apocrypha, folded into Side Jobs).
  - **Codex Alera** (6): furies-of-calderon 2004 through first-lords-fury
    2009. Complete, verified. Book 1 and book 6 each checked against their own
    Wikipedia article; books 2-5 rest on the author-page bibliography table
    plus well-established secondary summaries rather than a dedicated article
    (none exists for those four) - flagged for completeness-auditor to verify
    against a primary source per book.
  - **The Cinder Spires** (3, ongoing): the-aeronauts-windlass 2015,
    warriorborn 2023 (novella, book 1.5, apocrypha), the-olympian-affair 2023.
    A third novel is confirmed announced for 2026 with no title or date yet
    (jim-butcher.com, risingshadow.net) - not catalogued; not enough is known
    to satisfy the `forthcoming` field's sourcing bar.
  - **Other** (1): the-darkest-hours (2006, apocrypha), a licensed Spider-Man
    tie-in, subseries null.
- `eras.yaml`, `orders.yaml`: both `[]`, each with a rejection note. Butcher's
  own stated "20-25 case files then a final trilogy" shape is a plan for
  unwritten books, not a periodisation of the published shelf - recorded as a
  rejection in eras.yaml, not claimed as an era.
- `events.yaml`: 1 entry (the Peace Talks/Battle Ground manuscript split,
  2020, well-sourced including a direct Butcher quote).
- `theme.yaml`: palette/displayFace(spectral)/signature(none, deliberately -
  see file)/notes only. **No `art:` block** - see below.
- No `characters.yaml`: searched specifically for crossover between the three
  series (interviews, forums); Butcher has said on record a Dresden/Alera
  crossover "would take a whole book" to even answer. Confirmed no shared
  universe or cast. Nothing to thread.
- No `achievements.yaml`: none earned at this stage.

## Capabilities activated

River/companion/wizard/hall/editions left `auto` (framework default).
`connections` also left `auto` rather than forced `off` - there is genuinely
nothing to map (see above), so it will simply render nothing, which is the
honest state, not a broken one.

## Validation status - one known, expected failure

`python scripts/validate.py --slug jim-butcher` fails with exactly one error:
**no `art:` block on theme.yaml.** This is not an oversight: the task and the
`visual-language` skill both assign that block to a later stage
("Do not touch palette/preset/displayFace/signature/notes. They are set at
scaffold" - visual-language/SKILL.md), and this scaffold deliberately left it
unset. Flagging for whoever reads this next: the documented stage-1 gate in
`.claude/commands/author.md` ("Gate: validator green") is currently
inconsistent with `validate.py`'s hard requirement for `art:`, since no
scaffold-only stage can produce that block itself without overstepping into
visual-language's territory. Every other check is clean (0 other errors, 1
pre-existing-pattern warning shared with brandon-sanderson's works.yaml).

## What is thin, and who owns it

- Bibliography completeness (especially Codex Alera books 2-5's per-book
  sourcing, and the short-fiction/anthology tail deliberately left off the
  spine) - `completeness-auditor`.
- Aura depth: 4 author lifeEvents, 1 franchise event. The 2014-2020 writing
  gap's real cause (reported personal hardship) needs two independent
  sources on a living person and was deliberately left uncarried -
  `press-archaeology`.
- Eras: none claimed; genuinely open - `eras`.
- Reading orders/startHere: none found citable - `reading-orders`.
- `theme.art`, portraits, covers, editions - `visual-language`,
  `visual-metadata`, `editions` respectively.
- Spoiler boundaries: no `spoilerAfter` set anywhere. Twelve Months and
  Battle Ground especially need one - `spoiler-audit`.
- pt-PT translation: not started.
