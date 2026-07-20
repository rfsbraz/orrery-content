---
name: spoiler-audit
description: Audit a franchise's content for spoilers and set spoilerAfter boundaries correctly - classifying load-bearing reveals, anchoring each boundary on the work it actually damages, and rewriting prose spoiler-free wherever that beats redacting. Use when adding or reviewing a franchise bundle, when a curator reports a spoiler, or before a wing ships to readers.
---

# spoiler-audit

Orrery's premise is that context makes reading better. The spoiler engine is
what keeps that promise honest: content carries boundaries, and a fact is
revealed only once the reader has passed the work that makes it safe.

Read `docs/SCHEMA.md` ("Spoilers") and `lib/spoilers/index.ts` in the app before
starting. The schema tells you what the field means; the app tells you what it
actually does, and the gap between them is where spoilers ship.

## The asymmetry decides everything

**A false negative is unrecoverable. A false positive is annoying.**

You cannot un-spoil a reader. If you shield something that did not need it, a
curator loosens it later and nobody was harmed. If you leave a twist in the
open, someone's first read of a book is gone permanently, and the site that did
it was the one promising to protect them.

So when the judgement is genuinely balanced, **redact, and say in the PR that
you were unsure** so a curator can loosen it deliberately.

But the asymmetry is a tiebreaker, not a licence. A wing that greys out half
its timeline fails a different way: readers stop trusting the shields, start
clicking through them reflexively, and the protection is worth nothing. Redact
on a genuine tie, not on every unexamined doubt. The way out of most ties is
not the gate - it is a better sentence (see *Rewrite before redact*).

## First: what actually has a gate

`spoilerAfter` exists on exactly three things. Everything else in the schema is
**ungated prose that ships to every reader, signed in or not**:

| Field | Gated? |
|---|---|
| `events[].spoilerAfter` (franchise + `global.yaml`) | **yes** |
| `authors[].lifeEvents[].spoilerAfter` | **yes** |
| `characters[].appearsIn[].spoilerAfter` | **yes** |
| `works[].synopsis` | no |
| `works[].connections` | no |
| `characters[].description`, `characters[].aka` | no |
| `orders[].rationale`, `orders[].debated` | no |
| `eras[].description` | no |
| `franchise.description`, `startHere[].description`, `startHere[].note` | no |

Two consequences, and both have shipped real spoilers:

1. **In ungated fields, rewriting is the only tool.** There is no boundary to
   set. If the sentence cannot be written safely, it does not go in.
2. **Ungated prose sitting above a gated item defeats the gate.** A character
   `description` that states the reveal makes the carefully-gated `appearsIn`
   below it pointless. **Audit the whole entity, not the field with the
   boundary on it.** This is the single most common real failure.

## Load-bearing or incidental

Not all spoilers are equal. Grade before you act.

**Load-bearing** - the thing the book spends itself buying. Gate or rewrite:

- a death, especially of a protagonist or a child
- a survival (the mirror of a death, and far easier to leak: sequels,
  connections and character rosters leak survival constantly)
- a twist identity - who someone really is, who did it
- a betrayal, or an allegiance that turns
- the ending, or the shape of the ending
- **what the book turns out to be** - the frame, the unreliable narrator, the
  structural reveal. This is where literary fiction lives.

**Incidental** - usually fine plainly:

- "set after the events of X", series and subseries membership
- publication history, prizes, adaptations, print runs
- premise, setup, inciting incident, anything in the first act
- a named recurring character who is on the book's own cover

## The publisher test

The most reliable discriminator, and the one that will overturn your
assumptions most often:

> **Is the fact in the book's own official jacket or back-cover copy?**

If the publisher printed it on the object the reader buys, stating it is not
spoiling - the reader cannot avoid it, and hiding it makes the site look broken
next to the physical book.

This test is only worth anything if you **actually look the copy up**. It cuts
both ways and it cuts hard:

- Father Callahan returning in *Wolves of the Calla* reads like a great
  surprise. The publisher's flap copy introduces him outright as "once of
  'Salem's Lot, Maine". Not a surprise.
- Brady Hartsfield surviving *Mr. Mercedes* reads like a sequel leak. He wakes
  up in that book's own epilogue. Nothing to protect.
- João Tordo's second island novel folding the first inside itself reads like
  the trilogy's central revelation. It is in the first paragraph of the
  Penguin/Companhia das Letras blurb. Marketing framing.
- And inverted: *Insomnia*'s Dark Tower connection reads like common knowledge.
  It is nowhere in the jacket copy and lands in the third act. Real reveal.

**Careful with the inverse.** A later book's blurb is publisher copy for *that*
book while spoiling an *earlier* one - publishers routinely trade book 1's
ending to sell book 2. The test asks whether the fact is on the jacket of the
book **it would spoil**, not on some jacket somewhere.

Where you cannot find the copy, say so and fall back to the asymmetry.

## Picking the anchor

`spoilerAfter: <work-id>` means: *revealed to a reader who has read this work;
shielded for everyone else.* One work, not a series, not a list.

> Anchor on **the work whose experience the fact damages** - which is the work
> that reveals it, not the work it happens in, and never the whole series.

Ask: *whose first read does this ruin?* That book is the anchor.

Worked example. Father Callahan appears in *Wolves of the Calla*. The fact that
gives away is **that he survived 'Salem's Lot** - so 'Salem's Lot is the book
damaged, and the anchor. Anchoring on *Wolves* instead is wrong twice: it hides
the connection from readers who finished 'Salem's Lot and earned it, and it
mis-states what is being protected.

His *later* appearances (books VI, VII) are a different fact - that he carries
**past** Wolves - so those anchor on *Wolves*. Same character, three
appearances, two boundaries. Precision here is the whole job.

Common anchoring errors:

- **Anchoring on the whole series.** There is no such thing; pick the volume.
- **Anchoring on the latest work mentioned.** Too tight, hides earned content.
- **Anchoring on where the event happens** rather than where it is revealed.
  A backstory disclosed in book 5 anchors on book 5, not the book it happened in.
- **Anchoring a publication fact at all.** Prizes, release dates and cycle
  completions are not plot. Leave them `null`.

## Rewrite before redact

**A sentence that survives spoiler-free beats a correct redaction**, because
everyone can read it. Reach for a boundary only when the fact genuinely cannot
be stated safely *and* is genuinely worth stating.

Most spoilers are one clause. Cut the clause, keep the entry:

- A synopsis: write the premise the jacket writes. Publishers are good at this;
  they have to sell the book without wrecking it. Follow their lead.
- A high-impact life event gated behind a novel for one trailing clause about
  how it is used inside the fiction: **drop the clause and ungate the event.**
  The biography reaches everyone and the reveal is simply never stated. Both
  directions improve at once - this is the shape to look for.
- A character description: describe who they are in their first appearance, not
  what their arc becomes.
- An `aka` naming a later identity: remove the alias. There is no gate on `aka`,
  and an alias is exactly a twist identity in a list.

Deleting content is the **last** resort and needs saying out loud in the PR.
The one clean case is a `connections` edge whose existence is the spoiler:
`docs/SCHEMA.md` prescribes carrying it as a gated character appearance
instead, so move it rather than losing it.

## Vectors to hunt

Work through these deliberately; the obvious file is rarely the worst one.

**`connections`.** Ungated, and a connection is a survival claim: "this
character/place/thread is still going in a later book". Judge each edge by what
it discloses about the *earlier* work.

**`characters.yaml`.** The densest vector. An arc summary spoils the book where
it resolves. Check `description` and `aka` as hard as `appearsIn` - and note
that a *shielded* appearance row still shows the reader that something exists
and names the unlocking work (see *Engine limits*).

**`startHere` paths.** Sales copy written to be enticing, which is exactly the
pressure that leaks endings. "The one where X dies" sells a path and ruins a
book.

**`orders[].rationale` and `orders[].debated`.** Systematically under-checked.
A reading order argues *why* a book goes where it goes, and the honest reason is
often the reveal ("read this one before that one for the late payoff").
Telegraphing that a book has a late payoff is itself a spoiler. Say what the
order does without saying what it pays off.

**Era descriptions.** Usually safe, but they summarise a decade's arcs and
sometimes name what a book resolves.

**`events/global.yaml`.** A real death or a war's outcome landing inside a
novel's timeframe can spoil that novel's frame. Rare, worth the pass.

**Synopses of later books in a series.** Where publisher copy trades book 1's
ending for book 2's sale. If you decline to use that copy, **leave a `note:`
saying why** - `note` on a work is curator-only and never rendered, so it is the
right place to disarm the landmine for the next enrichment pass, which will
otherwise pull the blurb wholesale and ship the spoiler you just removed.

## Literary fiction spoils differently

Genre asks *what happens next*; literary fiction more often asks *what is
actually going on*. So the reveal is rarely a death:

- the frame - who is really narrating, and from when
- the structural fold - that this book contains, rewrites, or is authored by
  another
- the unreliability - the moment the account collapses
- whether an absence was a death, a disappearance, or an escape - and note that
  literary blurbs often deliberately preserve that ambiguity; a synopsis that
  resolves what the jacket left open is spoiling even when it states no event

**Judge the text in its own language.** A Portuguese novel is judged on the
Portuguese back cover; translated summaries drift and add resolution the
original withheld.

## Translations: mirror every fix

`content/i18n/<locale>/` overlays merge **field by field**. An English rewrite
that is not mirrored leaves the old string live, so **the locale reader still
reads the spoiler you just removed.** A spoiler fix in one language is not a
fix.

For every prose field you rewrite, update the matching overlay entry in the same
PR, then run `python scripts/i18n_coverage.py` and report the delta. Coverage
holding steady is the evidence the fix actually landed everywhere.

(Changing only `spoilerAfter` needs no overlay work - it is structure, not
prose.)

## Engine limits worth knowing

- **Shields are not invisible.** `shieldCopy` renders "Hidden until you finish
  *<Title>*". A shielded row therefore discloses that something exists and names
  the unlocking work. For a character roster that leaks "this figure recurs, and
  it starts around book five". If even that is too much, the entry must not
  exist rather than be shielded.
- **Boundaries are single works, and membership is exact.** `isRevealed` is a
  set membership check: a reader who read books 1-7 but not the anchor stays
  shielded. Prefer an anchor readers will actually have read - typically the
  work that reveals the fact, which is also the one they cannot have skipped.
- **No gate on synopses, connections, descriptions, or order prose.** The big
  one. Rewriting is the only remedy there.

## Hard rules

- **Never change an id.** Rewriting prose is encouraged; renaming orphans real
  readers' shelves. This includes work, character, event, and order ids.
- **Verify the plot before ruling.** Read what actually happens and where it is
  revealed. Guessing whether something is a spoiler is how you ship one, and
  half-remembered plots are wrong in both directions.
- **Record every ruling, including the ones that changed nothing.** "Checked,
  it is jacket copy, left alone" is a result, and it stops the next auditor
  re-litigating it.
- **State your uncertainty.** A redaction you were unsure about must say so, or
  nobody will ever loosen it.
- No em dashes. Quote YAML values containing colons or apostrophes.
- `python scripts/validate.py` until green.

## Process

1. **Read the engine** (`lib/spoilers/`, `lib/content/types.ts`) and confirm
   which fields still carry a boundary. The table above is true as of writing;
   verify it rather than trusting it.
2. **Inventory** every file in the franchise, plus the author entities its works
   reference and `events/global.yaml`. Not just `events.yaml`.
3. **Research the plots** before ruling - what happens, where it is revealed,
   and what the publisher's own copy says. Delegate this if the catalogue is
   large; it is the expensive half and it is not optional.
4. **Classify** each candidate load-bearing or incidental.
5. **For each load-bearing one**: try a rewrite first; if it must be stated,
   pick the anchor by asking whose first read it ruins.
6. **Sweep the false positives** - existing boundaries on publication facts and
   jacket copy - and loosen them with the reason recorded.
7. **Mirror every rewrite** into the locale overlays.
8. **Validate and measure**: `validate.py` green, `i18n_coverage.py` reported.

## Done means

A PR whose body lists **every spoiler found, grouped by severity**; which were
**rewritten** versus given a **`spoilerAfter`** and why; every **existing
boundary loosened** and the reason; every ruling of "checked, not a spoiler"
with its basis; the **pt-PT (and other locale) strings invalidated** and
mirrored, with the coverage delta; and any place **the engine could not express
what the content needed**. Boundaries you were unsure about are called out
explicitly as loosenable.
