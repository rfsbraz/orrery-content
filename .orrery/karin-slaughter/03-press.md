# Karin Slaughter - press archaeology handoff

## Events added: 11 (3 author lifeEvents, 8 franchise events)

Impact split: 2 high, 8 med, 1 low.

**Author lifeEvents** (`content/authors/karin-slaughter.yaml`):
- `karin-slaughter-childhood-macabre` (1971, low) - the autopsy-photo-on-the-
  lunchbox anecdote, father's love of horror films, the Jonesboro library.
  Sources: Atlanta Magazine 2012 profile, Wikipedia.
- `karin-slaughter-agent-and-first-deal-2000` (2000, **high**) - the
  unpublished antebellum-South novel, agent Victoria Sanders' redirect from
  historical fiction to thriller, the three-book "high six figures" deal from
  William Morrow at 29 (Variety: "Morrow, Slaughter Ink Killer Book Deal").
  Sources: Atlanta Magazine 2012 (agent Sanders quoted directly), Wikipedia.
- `karin-slaughter-save-the-libraries-2010` (2010-09-10, med) - the ALA
  meeting that prompted it, the Sept 10 2010 AJC op-ed, DeKalb County pilot,
  $300k+ raised. This resolves the scaffold's flagged gap: the founding now
  has a sourced day-precision date. Sources: savethelibraries.com,
  karinslaughter.com, Wikipedia (three independent sources).

**Franchise events** (`content/franchises/karin-slaughter/events.yaml`):
- Blindsighted's post-9/11 launch tour (2001-09-17, med)
- Grant County's small-town texture drawn from real Georgia childhood
  (2003, low)
- Will Trent's dyslexia origin, in Slaughter's own words (2006/2012, **high**)
- Criminal's dual timeline as "The Help for policewomen" (2012, med)
- Cop Town's Ian Fleming Steel Dagger win, judges quoted (2015-09, med)
- False Witness written deliberately during COVID (2021-07, med)
- Pieces of Her's #1 Netflix debut, 227.5M hours (2022-03-04, med)
- Will Trent's ABC premiere (2023-01-03, med)

## A correction made silently

Atlanta Magazine's 2012 profile frames Blindsighted as coming out "the day
after 9/11." Kirkus and Publishers Weekly both independently give its pub
date as September 17, 2001 - six days after, not one. The event below uses
the verified date and describes the tour timing accurately rather than
repeating the magazine's looser framing.

## Rejected, and why

- **Slaughter's sister's dyslexia** as inspiration for Will Trent's: stated
  in the same Atlanta Magazine profile, but no second source corroborates it,
  and it is a health/family fact about a private third party. Only the safe
  half - Slaughter's own on-the-record explanation of the character choice,
  from a different single-author interview - made it into the Will Trent
  dyslexia event.
- Slaughter's "significant other," alluded to but not named in the same
  profile: she says explicitly she protects her home life's privacy. That
  settles it under the skill's own test.
- Cop Town's Edgar nomination alongside its Steel Dagger win: same book, same
  year, second award - would have padded rather than added.
- 2025 Georgia Author of the Year and Library Reads Hall of Fame: real, but
  tied to no specific book and recolor nothing.
- The Good Daughter's Peacock adaptation: announced, not yet aired, nothing
  to date an event to yet.
- A 2003 Bookreporter interview previewing Indelible's Lena Adams arc: used
  only for its spoiler-free half (the hometown-texture event); the rest
  previews a book two entries ahead and wasn't worth the risk for no gain.

## Density

Before: 0 wing-authored aura entries (10 catalogue-wide global events reached
the wing on their own). After: 21 total (11 new + 10 global), 0.49 per work,
up from an entirely dark 25-year span. Longest remaining dark run: 4 years
(2016-2019, covering The Kept Woman, Last Breath and The Good Daughter) -
below the 5-year threshold the skill flags as needing another look, and
bounded on both sides by Criminal (2012)/Cop Town (2015) and False Witness
(2021)/Pieces of Her Netflix (2022).

## Spoiler confirmation

The Grant County spoiler (what happens to Jeffrey Tolliver in Beyond Reach)
is **not stated in any rendered field** I touched. The one event that
touches the crossover territory - none of the eight, in fact - was
deliberately not written: the bare fact that Sara Linton's story continues
into Will Trent is already carried in `franchise.yaml`'s description and
`characters.yaml`'s appearsIn notes, and adding a ninth event to restate it
would have been padding, not a new sourced fact. Nothing added here goes
further than that existing, already-safe statement.

## Validation

`python scripts/validate.py --slug karin-slaughter` - clean except the
expected `theme.art` error (visual-language stage territory). Commit
`794fadf` on `wing/karin-slaughter`, not pushed.
