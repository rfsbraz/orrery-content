# Karin Slaughter - editions handoff

## Coverage: 39/43

All 26 novels/standalones (Grant County 6, Will Trent 12, North Falls 1 of 2,
standalones 6) plus 14 of 17 short-fiction pieces. One edition per work, not
a US/UK pair - her US and UK printings mostly share the same English text, so
a second row would duplicate rather than describe a different object. The
one title-level difference (Beyond Reach / UK "Skin Privilege") already lives
as a note on the work itself.

## Source

`lookup.py karin-slaughter --author "Karin Slaughter" --json` (one call, ~40
requests) surfaced candidates for all 26 novels/standalones and 3 shorts
(Like a Charm, Cleaning the Gold, Last Breath, Martin Misunderstood). The
rest needed targeted fallback: OpenLibrary's `search.json`, the Library of
Congress SRU gateway, and Google Books page URLs already cited in
works.yaml's own sources. Every entry is corroborated by LOC or OpenLibrary,
most by both. `--verify-isbns karin-slaughter` passes: 39 editions, 0
suspect.

## LOC caught two wrong-but-close OpenLibrary numbers

Pretty Girls and The Kept Woman both had works.yaml coverSource records
carrying an ISBN that is not the book's actual first edition: LOC's CIP
record for each gives a different, correct number and doesn't list the
OpenLibrary candidate anywhere. Both are documented in the file header;
neither cover image needed to change, since `images.cover` and this file's
`isbn13` may point at different real printings of the same book.

## Deliberate absences (4), each checked not just unsearched

- **The Secrets We Hide**: unpublished. Its one pre-pub OpenLibrary record is
  attributed to a rights agency, not a publisher, with no second source.
- **Thorn in My Side**, **The Truth About Pretty Girls**: Amazon Kindle
  Single / Audible original (ASIN, not ISBN); no LOC or OpenLibrary record.
- **Short Story** (Koryta crossover): 2019 reissue is Kindle-only; its first
  appearance, the multi-author MatchUp anthology, would misattribute a
  dozen other authors' book to a single-story entry - same reasoning that
  keeps First Thrills: Volume 3 out for Cold, Cold Heart.

## Two things flagged, not fixed

- **Busted**: publisher record dates it 2013, a year after works.yaml's
  `published: 2012`. Plausible either way (paperback bonus for the 2013
  Unseen); left for whoever next reviews works.yaml.
- **Girl, Forgotten**'s edition is OpenLibrary-only - no LOC record resolves
  under its ISBN or an author-scoped title search. Noted in its entry.

## Shared ISBN, not a bug

Necessary Women and The Mean Time released as one paired ebook (Random
House, 2013) and correctly share isbn13 9781448149193.

## For translation

No pt-PT edition of any Slaughter work exists; this file is English-only.
Nothing here blocks the translation stage.

## Validation

`validate.py --slug karin-slaughter`: 0 errors, 0 warnings (four
pipeline-narration warnings from the first write were rephrased and are
gone). `--verify-isbns karin-slaughter`: 39 editions, 0 suspect. Commit
`05680c2` on `wing/karin-slaughter`, not pushed.
