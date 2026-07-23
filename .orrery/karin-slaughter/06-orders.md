# Karin Slaughter - reading orders handoff

## The merge, resolved without a new combined order

The default (all works, strict publication year) already sequences the
merge safely: every Grant County novel publishes by 2007, and Sara Linton
does not appear in Will Trent until Undone (2009, #3). Triptych (2006) and
Fractured (2008) sit chronologically among Grant County's run but involve
no Sara material, so they carry zero spoiler risk regardless of position.
No combined GC+WT order was authored: a hand-written subset of the default
would add no information the default doesn't already give for free, and
there is no genuine intra-year tie inside it to justify one (the schema's
one licensed exception to "never hand-write the default"). Confirmed
karinslaughter.com's own Book FAQ does not offer a combined order either -
it points to the two series' separate pages, nothing more (a fetched
secondary-site claim that she'd "suggested a combined order on her website"
turned out false on checking the primary source directly; not used).

## Orders (2, both pre-existing, both edited)

- **`karin-slaughter/grant-county-in-order`** (curated, unchanged scope/list).
  Added one sentence pointing forward to Undone, safe under the existing
  publisher-stated crossover fact.
- **`karin-slaughter/will-trent-in-order`** (curated, unchanged scope/list).
  Added the one warning this wing needed: from Undone (#3), Sara Linton
  joins the cast, read Grant County first if you plan to, so its ending
  isn't spoiled out of order. This was the actual gap - the order read a
  reader straight through the merge with no warning at all before this pass.

## startHere: 4 paths added (none existed)

1. **`everything-in-order`** (completionist/complete) - `orderId: default`.
   States the default's own timing keeps Grant County's ending intact
   before Will Trent continues, no invented order needed.
2. **`grant-county-first`** (new/arc) - `orderId: grant-county-in-order`.
   SOURCED: tlbranson.com ("I'd read Grant County before the later Will
   Trent books if you care about Sara Linton's full character arc") and
   nextbookintheseries.com ("Option A - Most Rewarding: Read all 6 Grant
   County novels in order, Begin Will Trent from Book 1"), both fetched and
   quoted verbatim in the sourcing comment.
3. **`will-trent-taste`** (new/taste) - `workIds: [triptych, fractured]`.
   DERIVED, per the brief's explicit carve-out: Sara's first WT appearance
   at Undone (#3) is sourced (characters.yaml); "Will Trent works standalone
   and is many readers' TV-driven entry point" is sourced (nextbookinthe
   series, tlbranson); bounding the safe taste at exactly 2 books is this
   catalogue's own derivation from combining those two facts, not a
   sentence any guide states. This is the path doing the actual spoiler
   protection at the wizard level.
4. **`continue-into-will-trent`** (returning/arc) - `orderId:
   will-trent-in-order`. SOURCED: same nextbookintheseries Option A quote.
   Safe by construction (a reader who's read Grant County has no spoiler
   exposure left).

Fit coverage: new+taste and completionist+complete both covered; no
padding, no invented cell.

## Startthere's basis for startHere, restated plainly

The startHere wizard cannot recommend a full Will Trent read (the existing
12-book order) to a `new` reader, because that order runs straight through
the spoiler at Undone with only a prose warning, not a structural gate. So
`new` readers only ever get `will-trent-taste` (2 safe books) or
`grant-county-first` (the whole safe series); the full Will Trent order is
offered only to `returning` readers who've already cleared Grant County.
This is deliberate, not an oversight - it is the mechanism that keeps the
constraint in the brief ("no recommended path sends a reader into Sara's
Will Trent material before Grant County is finished") true.

## Spoiler-audit confirmation

Every line of new prose (order rationales, path titles/descriptions/notes,
sourcing comments) states only: the bare fact of the crossover (already
publisher-marketed, already on franchise.yaml's description), the book ids
where it starts (Undone, #3), and the reading-order consequence. Nothing
written states what happens to Jeffrey Tolliver in Beyond Reach, why Sara
leaves Heartsdale, or anything about her emotional state beyond "her story
continues." No publisher blurbs were pulled (Broken's back-cover copy,
which does spoil this, was not quoted anywhere).

## Validation

`python scripts/validate.py --slug karin-slaughter` - clean except the
expected pre-existing `theme.art` error. No new warnings anywhere in the
catalogue (`validate.py` run unscoped and grepped for `karin`). i18n
coverage unchanged: the wing is still entirely MISSING from pt-PT (was
already fully untranslated before this stage; translation runs last in the
pipeline by design, so this is not a regression). Commit `0cefe9a` on
`wing/karin-slaughter`, not pushed.
