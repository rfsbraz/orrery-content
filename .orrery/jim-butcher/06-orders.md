---
stage: reading-orders
summary: "Added one curated order (the Dresden Files novels, series-filtered, one tie fixed); confirmed no startHere - no cross-series or single-series alternate-entry recommendation converges anywhere checked"
---

## Order added (1)

`jim-butcher/dresden-files-novels` - the eighteen Dresden Files novels, `type: curated`, `source: canon`. Two real contributions:

1. **Series isolation.** The default interleaves three unrelated series (Butcher: a Dresden/Alera crossover "would take a whole book" to even answer). A Dresden-only list is the single most commonly published Jim Butcher reading order in the wild (thealexandrian.net, markandrealexander.com, destructoid.com, bookseriesinorder.com and others publish it as its own artefact, never a whole-bibliography or Alera-only guide) - the Christie Poirot/Marple precedent, not the rejected Bromeliad/Johnny Maxwell case (no isolating demand exists for those).
2. **A real tie the default cannot fix.** Peace Talks and Battle Ground were one manuscript split into two books ten weeks apart (events.yaml), both published 2020. `published` is year-only by schema design, and the repo's own sort (`wing_digest.py`, `(published, id)`) would place "battle-ground" before "peace-talks" alphabetically - the wrong order for two halves of one story. The list fixes it explicitly.

Novels-only, matching Christie's precedent: the two collections and four standalone novellas are named as excluded in `debated`, not silently dropped. Sources: thealexandrian.net (dedicated Dresden-only guide, also confirms jim-butcher.com maintains an internal-chronology story list), jim-butcher.com/books/dresden (the author's site groups the three series as separate pages), Newsweek (Peace Talks/Battle Ground release dates, already used elsewhere in the wing).

Codex Alera and Cinder Spires: confirmed no order, per the existing scaffold rejection - Alera has no side material or same-year ties; Cinder Spires is too thin, and its one real tie (Warriorborn/The Olympian Affair, both 2023) is handled the way Pratchett's Bromeliad tie is (Diggers/Wings, both 1990) - a work-level note, not a full order. Added the equivalent tie-break note to `battle-ground` and `out-law` too (Twelve Months/Out Law, both 2026, Twelve Months first) as belt-and-suspenders for readers who never open orders.yaml.

## startHere: none, and the Dresden start-point question is closed

Confirmed the scaffold's rejection (no citable cross-series "which series first" recommendation) and closed the second question: whether the Dresden Files' own "first two books are weak" complaint converges on a citable alternate entry point. It does not.

- thealexandrian.net (a dedicated reading-order page) floats Summer Knight as a fallback for readers who bounce off book 1-2, then explicitly recommends against skipping.
- A Goodreads Q&A thread splits across Grave Peril, Summer Knight, Death Masks and Blood Rites as "where it gets good" - no two commenters agree, and one claims Butcher himself named a start point with no citation anywhere (checked; nothing datable found - fabrication risk, not used).
- Every dedicated reading-order page checked (jim-butcher.com, Destructoid, The Fantasy Review, BookSeriesInOrder) still starts new readers at Storm Front.

Scattered, disagreeing forum opinion is not a settled community practice under this skill's bar, and jim-butcher.com's own FAQ states the "22 case books + trilogy" plan but no start-point advice. Recorded the finding in franchise.yaml's comment (also fixed a stale "32 works" left from before completeness-auditor's pass, to 34).

## Spoiler-audit note

Nothing in the new order's prose needs a gate: it names a publishing-history fact (a manuscript split) and two short-fiction premises (Aftermath bridges two named novels; Backup is narrated by Thomas rather than Harry) at back-cover level, no plot reveals. No `spoilerAfter` needed.

## Validation

`validate.py --slug jim-butcher`: 1 error, the expected pre-existing `theme.art` gap. Zero new warnings, before and after. `wing_digest.py --for reading-orders` confirms the order resolves: 18 works, curated. No pt-PT overlay exists yet for this wing (translation hasn't started), so no i18n regression is possible; the order's prose and the extended work notes need pt-PT coverage once translation runs.

Commit: 2b347e5 on `wing/jim-butcher` (not pushed).
