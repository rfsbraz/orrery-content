# Karin Slaughter - spoiler-audit handoff

Full re-read of every rendered field: all 43 synopses, 8 franchise events,
3 author lifeEvents, 10 excluded global events, 7 character entries, both
order rationales, all 4 startHere paths and their notes, the franchise
description, and the (empty) eras block. The protected item is the Grant
County finale event, referenced only obliquely below.

## Leaks found and fixed (both in works.yaml synopses - ungated, rewrite the only remedy)

1. **Undone (Will Trent #3, the hinge book).** Its synopsis placed Sara in
   Atlanta "rebuilding her life after tragedy in rural Grant County" - the
   exact "left her small town after tragedy" pattern the skill names as a
   leak: it tells any reader, before they touch Grant County, that the
   series ends badly for Sara, disclosing the shape of the finale without
   naming it. Rewritten to "now living in Atlanta" - the crossover into
   Atlanta is publisher-marketed and safe; the causal "after tragedy" clause
   is gone. This was the real leak.

2. **Unseen (Will Trent #7).** Synopsis called Sara "the woman he loves,"
   the Sara/Will relationship vector the brief flags (a paired-off Sara
   implies her Grant County situation resolved). Rewritten to name her
   plainly with no romantic framing. Precautionary and loosenable: the
   Will/Sara romance is central Will Trent marketing, so a curator may
   restore it; it is cut here only because it costs Unseen nothing and the
   wing's stakes favour caution.

## Boundary confirmed (not changed)

`characters.yaml` -> `jeffrey-tolliver` -> appearsIn `beyond-reach` carries
`spoilerAfter: karin-slaughter/beyond-reach`. Correct field (a character
appearance is one of the three gated types), correct anchor (the book whose
first read the fact damages, which is also where it is revealed), target
resolves. Swept the whole entity per the Randall Flagg rule: the ungated
description ("Sara Linton's ex-husband ... open the franchise"), the 1993
prequel note, and the introduction note all describe him alive and state
nothing of his fate. No sibling prose defeats the gate. He is correctly
absent from every Will Trent row.

Note for the curator (loosenable, not a defect): the shield renders "Hidden
until you finish Beyond Reach" on his final row while his five earlier Grant
County rows show plainly. His presence in the finale is not itself secret
(he is the series' police chief), so the shield faintly signals that his
last appearance is spoiler-sensitive. Kept because removing the wing's one
deliberate boundary is a curator's call and the signal is far weaker than
any statement of the fact.

## Subtler vectors checked and cleared

- **This Is Why We Lied (#12)**: "honeymoon" reveals a Sara/Will marriage,
  but not the finale event (they were already divorced at series start), and
  it is the book's own premise. Kept.
- **Broken (#4)**: "needs his help more than ever" - vague case-difficulty,
  states no widowhood; its own back cover spoils this, ours does not. Kept.
- **After That Night (#11)**: "a violent attack upended her own life" is
  Sara's own backstory, revealed in book 1, not the finale. Kept.
- **connections**: broken->beyond-reach (revisits Grant County; discloses no
  event), plus the prequel/sequel links - none leak the finale.
- **Sara Linton entry**: ungated description says only that her story
  "continues into the Will Trent series" (publisher-stated); appearsIn notes
  safe.
- Franchise description, both order rationales, all startHere notes: each
  states only the reading-order consequence and warns readers off spoiling
  Grant County's ending without stating what it is.
- eras.yaml is `[]`; its comment is stripped at parse and states nothing.

## Validation

`python scripts/validate.py --slug karin-slaughter`: clean but for the
expected `theme.art` error (visual-language stage). No new warnings.
spoilerAfter target resolves. No pt-PT overlay exists for this wing, so the
rewrites invalidate no translation.

## Verdict

The Grant County finale event appears in no rendered field. With Undone
corrected, the ending is unspoilable through this wing's rendered content.
