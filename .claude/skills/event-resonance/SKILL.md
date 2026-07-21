---
name: event-resonance
description: Decide which global events actually belong on a specific author's timeline, and why. Judges resonance per franchise rather than assuming a global event reaches every author. Use after world-events changes the shared layer, or when adding a franchise whose span overlaps events it may not have felt.
---

# event-resonance

Decide, for one franchise, **which of the shared global events actually reached
this author's page** - and be able to say what each one meant to them.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md); the aura
editorial standard is its §6. Read `.claude/skills/world-events/SKILL.md`
first: that skill decides whether an event belongs in the catalogue at all,
this one whether it belongs on *your author*. They are different questions and
the second one has never been asked.

## The problem this exists to fix

`reach: global` was being read as "every franchise renders this". It should mean
"any franchise *could*". The difference was visible and embarrassing:

> João Tordo was born in 1975. His page opened in **1910**, and walked the
> reader through the First and Second World Wars before reaching his first
> novel in 2004.

The events were correctly curated. They were simply being shown to an author
they could not possibly have touched.

## What the engine already does for free

**Do not spend judgement on arithmetic.** The app now filters global events to
the span of the authors' lifetimes: an event is the weather a writer wrote in,
and nobody wrote in weather that predates them. A dead author's window closes at
death; where a franchise has several authors, the window stays open while any of
them is living. That rule alone fixed the world wars for Tordo, Sanderson, King
and Pratchett, kept both wars for Christie, costs no curation, and never needs
re-running when a franchise is added.

**Your job is the residue: the events that overlap the author's life but may
still not belong, and the rare event outside it that does.**

## The test

For each candidate, try to write **one sentence saying what this event meant for
this author's work.** Not for the world. Not for literature. For these books.

- If the sentence is specific and true, the event stays.
- If you find yourself writing "this shaped the era in which they wrote", that
  is the sound of a sentence with nothing in it. Exclude.
- If the honest sentence is "they lived through it and it never reached the
  page", exclude. Living through something is not resonance.

This is the same admission test as the aura standard - *does it pass through the
author into the page?* - applied one author at a time.

### Worked example, and the live case

`financial-crisis-2008` currently renders on **every** franchise. The
`world-events` curation itself called it "the weakest entry in the file" and
graded it `low`, on the grounds that almost nothing in the catalogue answers it.
That is exactly the shape of an event that survives the arithmetic gate and
fails the resonance test nearly everywhere. Rule on it per author rather than
inheriting it by default.

Compare `carnation-revolution-1974`: decisive for a Portuguese author, texture
at best for the other five. Same event, different answer per franchise. That is
the whole point of this skill.

## The two directions, and the asymmetry between them

**`exclude`** - overlaps the lifetime, never reached the page. This is most of
your work and the bar is low: if you cannot write the sentence, exclude it. An
absent event costs a reader nothing. A page cluttered with events that mean
nothing to this author teaches them that the aura is decoration, and then they
stop reading the ones that matter. **Clutter is not neutral, it is corrosive.**

**`include`** - outside the lifetime, but the author genuinely writes out of it.
The bar here is high, because you are overriding a defensible default. Use it
when the event created the conditions the author's work exists inside and the
books show it. A real candidate: `fantasy-paperback-boom-1965` predates Brandon
Sanderson (born 1975), but it created the commercial category epic fantasy is
written into, and his career is unimaginable without it. Inheritance of that kind
is legitimate. "It was historically important" is not.

When you `include`, say in the note what the author does with the inheritance.

## Output

Write the decision into the **franchise's own file**, never into
`content/events/global.yaml`. The global file must stay franchise-agnostic; the
judgement belongs where the author knowledge is.

```yaml
# content/franchises/<slug>/franchise.yaml
globalEvents:
  exclude:
    - financial-crisis-2008     # lived through it; no book answers it
  include:
    - fantasy-paperback-boom-1965  # predates him; created the category he writes in
```

Keep the note on the line short and specific. It is the evidence for a decision
a future curator will otherwise re-litigate from scratch.

## Hard rules

- **Never edit `global.yaml`.** Adding, removing or re-grading a shared event is
  the `world-events` skill's job and its bar is higher. If an event is wrong for
  *everyone*, say so in the PR and let that skill handle it.
- **Never fabricate a resonance** (CURATION §1). If you cannot evidence the
  link between the event and the work, there is no link.
- **Rule per author, not per franchise-shaped-guess.** A shared universe with
  two authors born 27 years apart does not have one answer.
- **Silence is a decision too.** An event you neither include nor exclude
  inherits the arithmetic default. Say in the PR which events you considered and
  left to the default, so the next agent knows the ground was covered.
- **Do not use this to fix a bad event.** If an entry is badly written or
  wrongly graded, that is a `world-events` fix, not an exclusion list.

## Done means

A PR whose body lists, for this franchise: every global event **kept** with its
one-sentence resonance, every event **excluded** with the reason, every
**include** override with what the author does with the inheritance, and the
events left to the default. A run that excludes three events and keeps two,
with five sentences a reader would recognise as true, is a good run. A run
that keeps everything has not made a decision, it has just agreed with the
machine.
