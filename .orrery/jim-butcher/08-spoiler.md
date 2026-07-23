---
stage: spoiler-audit
summary: "One load-bearing leak fixed by rewrite (Thomas = Harry's half-brother, the Blood Rites twist, leaked in 3 ungated places); one landmine note added (Ghost Story vs Changes' death). Zero spoilerAfter: the only gated entities carry no plot spoilers."
---

## The shape of this wing's spoiler surface

The engine gates exactly three things (verified in `lib/content/types.ts`:
`AuraEvent`, `CharacterAppearance` - `Work` has no `spoilerAfter`). This wing
has **no characters.yaml and no connections**, and every event/lifeEvent is
publishing history or origin story (bestseller debut, Cinder Spires deal,
manuscript split, the writing-class bet). None spoils plot; all correctly
`null`. So the whole real spoiler surface is **ungated prose** - synopses and
one order rationale - where the only lever is the words. No `spoilerAfter` set
anywhere, correctly.

## The one real leak (load-bearing, identity reveal), fixed by rewrite

**Thomas is Harry's half-brother** is the climax of *Blood Rites* (book 6).
Verified against publisher copy: Blood Rites' own jacket calls Thomas a
"vampire acquaintance" and teases only "a shocking revelation... that will
change his life forever" - it deliberately withholds the tie. Our Blood Rites
synopsis already mirrors that ("a family revelation"), correctly. But the tie
was stated openly in three ungated places that render to every reader:

- **White Night synopsis** ("a suspect he refuses to believe: his own
  half-brother") -> rewritten to "the one suspect he cannot bring himself to
  believe guilty: someone he loves." Faithful to White Night's own jacket hook,
  minus the relationship.
- **Backup synopsis** ("Harry's vampire half-brother Thomas") -> "Thomas, the
  White Court vampire who moves through Harry's world with loyalties of his
  own." Keeps the novella's real hook (a Thomas-POV story) without the tie.
- **orders.yaml rationale** ("Backup ... narrated by Harry's half-brother
  Thomas") -> "narrated by Thomas, the White Court vampire."

Curator notes (unrendered) added to White Night and Backup recording the reason.

## Judgement call, flagged as loosenable

The White Night rewrite is the debatable one. White Night's *own* back-cover
copy names "his half brother, Thomas" plainly, so a reader reaching book 9 in
order already knows it - only an out-of-order browser is exposed. Since
synopses cannot be gated and the loss (Blood Rites' twist) is unrecoverable,
the asymmetry says withhold. **A curator may reasonably restore White Night's
wording as series-furniture by book 9; Backup and the rationale should stay
rewritten.**

## Landmine disarmed (not a live leak)

Ghost Story's synopsis was already careful ("changed by the end of his last
case") and does *not* leak. But its publisher blurb opens "Harry Dresden ...
had been murdered" - i.e. it trades *Changes'* ending to sell itself. Added a
curator `note:` so an enrichment pass pulling the blurb wholesale does not
ship the Changes death. Changes' own jacket withholds the death; the inverse
publisher test says a later book's blurb does not license spoiling an earlier.

## Considered, deliberately NOT gated or changed

- **Cold Days** ("Bound now to serve Mab") - the Winter Knight mantle is the
  book's irreducible premise and on its own jacket; states no death. Left.
- **Twelve Months** ("after the battle against the Last Titan") - the Titan war
  is Battle Ground's own premise; its real spoiler (a major death) is in no
  synopsis. Left.
- **Proven Guilty** ("Newly a Warden") - a back-cover-level status change,
  incidental. Left.
- **Codex Alera** (Tavi-parentage never stated; "First Lord's Fury" is the real
  title) and **Cinder Spires** (no internal reveal leaked) - both clean.

## Validation / translation

`validate.py --slug jim-butcher`: OK, all references resolve (the two note
`[[work:]]` links included), 0 jim-butcher warnings. No pt-PT overlay exists
for this wing, so nothing to mirror; when translation runs it **must preserve
these omissions** - the rewritten synopses and the two new notes carry the
protection, and a literal translation of an older draft would re-leak.
