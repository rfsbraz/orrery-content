# Karin Slaughter - scaffold handoff

## Identity check

Confirmed against karinslaughter.com and Wikipedia (which agree throughout):
American crime writer, born January 6, 1971, Covington, Georgia, raised in
Lake Spivey. Not a namesake mixup.

## Structure: 36 works across 3 subseries + standalones + short fiction

Grouping follows the publisher's own site exactly (it labels every book
"Grant County #N" / "Will Trent #N" / "North Falls #N" or files it under
Standalone Novels).

**Grant County** (core, verified, complete, 2001-2007): blindsighted,
kisscut, a-faint-cold-fear, indelible, faithless, beyond-reach (UK title
"Skin Privilege").

**Will Trent** (core, verified, ongoing, 2006-2024, 12 books): triptych,
fractured, undone (international title "Genesis"), broken, fallen, criminal,
unseen, the-kept-woman, the-last-widow, the-silent-wife, after-that-night,
this-is-why-we-lied.

**North Falls** (core, verified, new, 2025-2026): we-are-all-guilty-here
(published, 2025); the-secrets-we-hide (`forthcoming: 2026-08-11`, US date -
a UK edition released 2026-06-18, already past, so it may be reviewable
before the US date; noted, not resolved).

**Standalones** (core, verified, 6): cop-town, pretty-girls,
the-good-daughter, pieces-of-her, false-witness, girl-forgotten (a genuine
sequel to pieces-of-her via Andrea Oliver/Cooper - `connections` set, both
still tiered standalone per the publisher).

**Short fiction** (10, tiered apocrypha/extended, thinner sourcing):
like-a-charm (2004, contributor - multi-author anthology, wrote the opening
and closing chapters), martin-misunderstood (2008), thorn-in-my-side (2011),
the-unremarkable-heart-and-other-stories (2011 print date; audio edition adds
a 2016 story and one previously unpublished - both facts recorded, not
resolved), snatched + busted (2012, Will Trent, paperback-exclusive bonus
shorts, `connections` to their host novels), blonde-hair-blue-eyes (2015,
prequel to pretty-girls) and last-breath (2017, prequel to the-good-daughter,
both `connections`-linked), cold-cold-heart (2016), cleaning-the-gold (2019,
co-written with Lee Child, Will Trent/Jack Reacher crossover - **no
withAuthorIds set: Lee Child has no author entity in this catalogue yet**).

## THE SARA LINTON MERGE POINT (read before touching this wing)

Sara Linton is Grant County's coroner and its emotional center across all six
novels. She is also, per the publisher's own marketing copy, the character
who "joins the Will Trent series," first appearing there in **Undone**
(Will Trent #3, 2009) and **Broken** (#4, 2010). That much - the bare fact of
the crossover - is stated openly by the publisher and is safe; it is on the
franchise description and in characters.yaml.

**What is not written anywhere in this scaffold** is *why* she leaves
Heartsdale: Jeffrey Tolliver, Grant County's police chief and her ex-husband,
dies in **Beyond Reach** (Grant County #6, the last book of that series) -
confirmed via web search, not memory, since this is exactly the kind of fact
a prior pass got wrong elsewhere in this catalogue. Every synopsis for Undone
and Broken was written to be true without depending on that fact, and
Jeffrey's characters.yaml entry lists his six Grant County appearances
plainly with `spoilerAfter: karin-slaughter/beyond-reach` on the final one
and no revealing note. **Publisher back-cover copy for Broken itself already
spoils this** ("that man's widow, Dr. Sara Linton") - a live example of why
this wing needs real spoiler discipline, not just care in this file.

A publication-order quirk worth flagging: **Triptych** (Will Trent #1, 2006)
published *before* Beyond Reach (2007), but Sara does not appear in Will
Trent's world until book 3. So the hazard is specifically Undone onward, not
"Will Trent" as a whole - Triptych and Fractured are spoiler-neutral.

## Left thin, deliberately

No eras.yaml (no sourced periodization found), no events.yaml or
lifeEvents (both anchors found - the three-month first draft, Save the
Libraries - lack a sourced day-precision date), no editions.yaml, no
achievements.yaml, no startHere, and `globalEvents` left unassessed. Two
order.yaml entries exist (Grant County and Will Trent each in their own
publication order); no combined order was attempted since no spoiler
boundary exists yet to route one safely around.

## Validation

`validate.py --slug karin-slaughter` is clean except the expected missing
`theme.art` error. Commit: `16d73f8`, on `wing/karin-slaughter`, not pushed.
