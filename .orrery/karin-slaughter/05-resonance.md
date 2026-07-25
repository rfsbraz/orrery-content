# Karin Slaughter - event resonance handoff

## Decision: 0 included, 10 excluded

No `world-events` stage ran for this wing (her 2001-2026 span has no empty
decade), so this was purely the editorial layer: which of the ten global
events reaching her lifetime (born 1971, living) actually resonate.

## Excluded, and why

- `sept-11-2001` - Blindsighted's real six-days-later launch (postponement
  offered, she flew anyway, "just me and the stewardess") is already told,
  with better sourcing, by the press stage's own
  `karin-slaughter-blindsighted-post-911-tour-2001`. Including the generic
  global entry too would put two markers on the same six-day window.
- `covid-19-pandemic-2020` - same shape: False Witness's deliberate pandemic
  setting, in her own words about polling other novelists, is already told
  by `karin-slaughter-false-witness-pandemic-2021`.
- `financial-crisis-2008` - Undone and Broken publish either side of it; no
  book is plotted around the crash.
- `chain-bookshop-1982`, `online-bookselling-1995`,
  `ebook-and-self-publishing-2007` - no sourced bookselling/publishing-format
  story for this wing; traditionally published by William Morrow/HarperCollins
  throughout.
- `prestige-fantasy-adaptation-2011` - wrong genre (she writes crime fiction);
  her own two screen adaptations (Pieces of Her, Will Trent) are already
  franchise events and cover that ground properly.
- `booktok-2020` - no documented BookTok-driven surge for any title here.
- `carnation-revolution-1974`, `portugal-bailout-2011` - both Portugal-specific;
  she's American, no bearing found.

## Included: none

Zero included is an honest result here, not an oversight: the two events
with a real, sourced connection to her work (9/11, COVID) both already have
a more specific, better-sourced franchise event carrying that exact story,
so admitting the generic global entry alongside them would be redundant
duplication on the same date range rather than new signal. This is the same
call the Gillian Flynn and Tana French wings made on the identical pair.

## Validation

`python scripts/validate.py --slug karin-slaughter` - clean except the
expected `theme.art` error (visual-language stage territory). No new
warnings. Commit `e1bce42` on `wing/karin-slaughter`, not pushed.

`franchise.yaml` left clean for `reading-orders`, which writes it next -
only the `globalEvents` block was touched; `startHere`, capabilities
comment and sources are untouched.
