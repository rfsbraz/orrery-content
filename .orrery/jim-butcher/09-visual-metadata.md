---
stage: visual-metadata
summary: "Cover coverage 32/34 (Open Library), portrait sourced (Wikimedia Commons), no franchise header by deliberate choice."
---

## Covers: 32/34, all Open Library, all eyeballed

Resolved every work to an Open Library work id via author-scoped title search
(`search.json?title=...&author=Jim+Butcher`), picking the highest-`edition_count`
record each time to avoid the omnibus/wrong-work trap, then verified via
`editions.json` wherever more than one candidate existed. Fetched every cover
with `?default=false`, built a labelled contact sheet, and looked at all of
them (twice, at two resolutions, after the first pass caught a false read).

Two swaps the sheet caught that a status-code check would have missed:
- **Grave Peril**: Open Library's representative cover (1697925) is an
  MP3-CD audiobook jacket. Swapped to 10076655, a print paperback cover from
  the same work record.
- **The Olympian Affair**: the default cover (14242378) is an early
  text-only placeholder with no illustration. Swapped to 14596463, the
  Cinder Spires-branded jacket from a later edition of the same work.

One swap driven by an image that was not a cover at all:
- **Small Favor**: the print edition's only OL cover (8047953) is a scan of
  the book's title page, not its jacket. Swapped to the audio edition's cover
  art (10189928), which is a real illustrated jacket.

## Two honest absences

- **The Law** (2022 Audible novella): Open Library's only record
  (OL45587260W) carries no cover image, and no other edition exists.
- **Backup** (2008 Subterranean Press novelette): three cover ids exist
  across its two OL work records. Two are scans of the title page, not the
  jacket. The third is the real Mike Mignola cover art, but the scanned copy
  has a library discard sticker printed over the illustration. No clean scan
  of the jacket exists anywhere in Open Library.

Both are commented in place in `works.yaml` explaining what was checked.

All 32 cover URLs are unique (checked programmatically); none repeats.

## Portrait: sourced

Jim Butcher, Wikimedia Commons, `File:Jim_Butcher_by_Gage_Skidmore.jpg`,
CC BY-SA 3.0, credited to Gage Skidmore. Convention head-and-shoulders shot,
already portrait-oriented (2917x3760), no rights ambiguity (Skidmore's
convention photography is reliably and correctly licensed on Commons).

## Franchise header: left bare, by choice

No real-world photo represents all three series. Chicago (the natural fit
for the palette) is only the Dresden Files' setting; Codex Alera's Alera and
the Cinder Spires' steampunk world have no real-world equivalent. Picking a
Chicago image would privilege one of three series the wing's own
`signature: none` decision already declined to visually unify. Documented in
`franchise.yaml` as a comment next to the same reasoning `theme.yaml` already
carries. Brandon Sanderson's wing (also multi-series) ships with no header
either, so this is a precedented outcome, not a gap.

## For editions/translation

- No `editions.yaml` exists for this wing yet; the `editions` stage will need
  its own ISBN-level research. Several works here (Small Favor, Backup) have
  print jackets on Open Library that are unusable (title pages, a library
  sticker) - worth carrying into that stage rather than re-discovering.
- No pt-PT overlay exists, so nothing to mirror for these fields.

## Validation

`python scripts/validate.py --slug jim-butcher`: clean, 0 errors.
`python scripts/asset_audit.py jim-butcher`: `portrait 1/1 covers 32/34`.

Commit: 4385c1b.
