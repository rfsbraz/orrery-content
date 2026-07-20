---
name: where-to-start
description: Curate a franchise's startHere entry paths - the "where do I start?" wizard - reporting the ways a community actually recommends entering a body of work rather than inventing our own. Use when adding, auditing, or repairing the startHere block in content/franchises/<slug>/franchise.yaml.
---

# where-to-start

Curate `startHere` in `content/franchises/<slug>/franchise.yaml`: the two-to-five
curated **entry paths** that power the wizard at `/f/<slug>/start`.

Read `docs/SCHEMA.md` (the `startHere` section and the capabilities table) before
writing YAML. `scripts/validate.py` enforces the structure; this skill owns the
judgement.

## Why this has to be right

"Where do I start?" is the single most asked question about any large body of
work, and getting it wrong is how a reader bounces off an author forever.
Starting Discworld at *The Colour of Magic* or King at *The Dark Tower* has
talked more people out of those authors than any bad review ever did. A wrong
path is not a cosmetic error; it is the one piece of content that can cost the
reader the whole shelf.

## The core principle: a path is received, not invented

> **Orrery reports how a community actually recommends entering a body of work.
> It does not issue its own opinion in a serif font.**

Every path needs evidence that real readers recommend it: a community FAQ, a
well-known guide, the author's own advice, a widely-cited article, or settled
fandom consensus you can point at. **If the only source is our own reading, it
is not a path.**

This is the same principle the `eras` and `reading-orders` skills work under,
and it is not modesty. A curated list assembled from taste is a blog post; a
reported consensus is a reference work. Only one of those is worth building.

The bar in practice, strongest first:

1. **The author's own advice.** Sanderson maintains a "Where do I start?" page;
   that is as good as evidence gets. Check the official site first, always.
2. **The canonical community guide.** Dragonmount for Wheel of Time, the
   Discworld Emporium and the official reading-order page, a subreddit's
   pinned FAQ or wiki.
3. **A widely-cited article** from a publication that actually covers books.
4. **Settled fandom consensus** - so uniformly given that any reader of that
   fandom would recognise it. Say so explicitly and say where you saw it; this
   is the weakest tier and the easiest to hallucinate.

Below that line: our own judgement, which is not a path.

### Recording the source

`StartHerePath` has no `sources` field, and adding one is an app change, not a
content change. So carry the citation as a **YAML comment directly above the
path**. Comments are invisible to the app and to the reader, cost nothing, and
survive in git where the next curator will find them.

```yaml
    # Source: https://www.brandonsanderson.com/pages/where-do-i-start
    # "If you consider yourself a fantasy reader, try Mistborn: the Final
    # Empire or The Way of Kings."
    - id: mistborn-first
      title: Start with Mistborn
```

The `note:` field is reader-facing prose, not a citation slot. "Basis: the
publisher-numbered grouping" reads as a footnote leaking into the museum. Use a
note to tell the reader something useful ("read Roger Ackroyd first for the
shock"), and put the receipt in the comment.

## The mechanic

The wizard asks the reader two questions and scores the declared paths. There is
no per-franchise app code; the content is the whole feature.

| Axis | Values | The question |
|---|---|---|
| `fit.experience` | `new` / `returning` / `completionist` | how much of this author have you read? |
| `fit.commitment` | `taste` / `arc` / `complete` | a few books, one thread, or everything? |

Scoring (`lib/wizard/match.ts`): an exact tag match scores 2 per axis; a path
that declares **no** tags on an axis scores 1 there, a soft universal fit. Ties
keep curator order, because the order is editorial. Every path is always
returned - the top one is the recommendation, the rest render as alternatives.

Two consequences worth internalising:

- **There is no "no match" state.** A reader always gets a recommendation, so a
  thin or badly tagged set does not fail loudly. It just quietly gives bad
  advice. Nothing will catch that but this skill.
- **A franchise with no `startHere` simply has no wizard** (`capabilities()`
  activates it on `startHere.paths.length > 0`). That is a complete, correct
  bundle, not a gap. Shipping no wizard is always better than shipping one
  built out of guesses.

## `workIds` versus `orderId`

Exactly one. The validator enforces that much; the judgement is where the line
falls.

- **`workIds`** - a short curated list of specific books. A handful: two to
  five. This is "read these", an entry strategy.
- **`orderId`** - a full sequence that already exists in `orders.yaml`, or the
  literal `default` for the derived publication order. This is "walk this
  traversal from the top".

The line: **if you find yourself listing more than about five works, you are
describing an order, not a path.** Put it in `orders.yaml` (that is the
`reading-orders` skill's job, with its own sourcing rules and a `debated:` field
for contested placements) and point the path at it. A path duplicating an
order's contents in `workIds` will drift out of sync with it and nothing will
notice.

Said once, cleanly, so the two skills do not fight:

> **A path is an entry strategy. An order is a full traversal.**
> The path says who should walk it and what it costs them. The order says what
> the sequence is and where the community disagrees about it.

When a path points at an order, **read that order's `rationale` and `debated`
fields and make sure the path's prose does not contradict them.** A path that
flattens a contested placement into "the common recommendation" has broken the
order's honesty (see the audit note on Wheel of Time below - this is a real
defect that shipped).

## Two to five paths, always including a completionist path

- **Fewer than two** is not a wizard, it is a redirect. If the honest answer is
  one path, consider whether the franchise should have `startHere` at all -
  though see "Sparse and non-English authors" below, where one path is right.
- **More than five is a menu, not advice.** The reader came here because the
  shelf was already too big. Handing them seven options recreates the problem
  in miniature.
- **Always include a completionist path**, almost always `orderId: default`.
  Someone will want the whole thing in order, and if the wizard cannot say so it
  looks like it is hiding the shelf.

## Name the cost

Like a reading order's rationale, **a path must say what it sacrifices.**

"Start with the essentials" gains momentum and loses the development you see
reading in order - the writer getting better in front of you. "Start with the
Watch" gains the best thread and loses the jokes that land only once you know
the world. "Publication order" gains the real experience and costs you two weak
books up front.

**A path with no stated cost has not been thought about.** It is the single
fastest way to tell curation from marketing: marketing lists benefits.

The cost belongs in the `description` or the `note`, in the reader's language,
not hedged into invisibility. One honest clause is enough.

## The famous-book trap

**The best-known work is often the worst entry point.** This is not a paradox;
it is what fame does. The recurring shapes:

- **The unfinished or sprawling cycle** the author is famous for, which asks for
  a commitment before the reader knows if they like the writing (King's Dark
  Tower).
- **The atypical masterpiece** that represents the author badly - brilliant, and
  nothing else on the shelf is like it.
- **The late-career book** that quietly assumes the earlier ones, whose power
  comes from twenty years of accumulated context the newcomer does not have.
- **The first book that is visibly a first book.** Series that found themselves
  later open on their weakest material; publication order hands the newcomer the
  worst chapter first (Discworld's Rincewind openers).

The rule: **judge an entry point by what it does for someone who has read
nothing, not by what it means to someone who has read everything.** Fame,
sales, and awards measure the second thing.

Where it applies, **the path must say so.** A reader who has heard of exactly
one book by this author will assume that is the door, and will be quietly
confused when the wizard sends them elsewhere. Tell them why, in one sentence,
and the recommendation gains authority instead of looking arbitrary.

And the discipline still holds: **the warning itself must be received advice.**
"Do not start with *The Colour of Magic*" is only shippable if you can point at
readers actually saying it. If you cannot, that is a flag for the curator, not
a sentence to write with confidence.

## Spoiler safety: the engine gives you nothing here

**`startHere` prose is ungated. There is no `spoilerAfter` on a path.** Unlike
an event or a note, a path's `title`, `description` and `note` ship to every
visitor of `/f/<slug>/start`, which is by definition the page for people who
have read nothing. There is no mechanism to hide any of it.

So: **a path must be written so that it needs no gate.**

The risk is structural, not incidental - a path that starts mid-series exists
precisely because there are earlier books, and the natural way to justify it is
to say what happens in them. Concretely:

- Naming which book a character first appears in can be a reveal.
- "By this point X has happened" is a spoiler even when X sounds like setup.
- A subseries description can spoil the main sequence (who survives to have
  their own thread is information).
- Even a work **title** in a `workIds` list is visible; a title that is itself a
  reveal cannot be hidden by careful prose around it.

Write entry paths at the level of premise and appeal - the level a back cover
works at - and the problem does not arise. If a path genuinely cannot be
justified without a spoiler, the path is wrong for a newcomer, which is useful
information rather than a formatting problem.

Cross-reference `spoiler-audit`: `startHere` is in its scope precisely because
the engine cannot protect it.

## Fit-matrix coverage

Cover the matrix **loosely**. Nine cells exist; you are not filling them.

- Gaps are fine. The app falls back to the best partial match and always returns
  something.
- **Do NOT invent a path to fill a cell.** A fabricated path scored perfectly
  against a reader's answers is worse than a real path scored approximately -
  the reader takes the recommendation either way.
- Leaving an axis **untagged is a deliberate tool**, not laziness: it makes the
  path a soft universal fit (score 1) rather than a miss. Use it for a path that
  genuinely suits anyone.
- The one shape worth checking: the `new` + `taste` cell (a curious newcomer
  with no commitment) and the `completionist` + `complete` cell (the full walk)
  are the two most-used answers. If neither is covered, the wizard is
  mistargeted.

## Sparse and non-English authors

Two failure modes to resist, both of which are padding:

**The small bibliography.** For an author with a dozen books and no subseries,
the honest answer may be "start at the beginning" and **one path**. That is a
correct bundle. Manufacturing a "thematic entry" and a "short works entry" to
reach three paths invents two of them. If one path is the truth and one path
feels too thin to ship, ship no `startHere` and no wizard - see the mechanic
above.

**The non-anglophone author.** Look for the entry advice **in that language**.
Portuguese readers recommending João Tordo, not English ones. English-language
coverage of a Portuguese literary novelist is thin, late, and often derivative,
and building a path from it means reporting what the anglophone internet guessed
rather than what his readers say. Search the author's own site, the publisher
(Penguin Livros / Companhia das Letras, Porto Editora), the national press, and
the local book community.

And be willing to conclude: **"no citable entry-path consensus exists"** is a
real, useful finding. Say it in the PR. It is not a failed research task; a
prize and a publisher grouping are facts, and neither is a reader saying "start
here".

## Translations: the overlay carries prose only

**Hard rule, from a bug that shipped.** Translation overlays were copying nested
values wholesale over the base, and **every `startHere` path in pt-PT lost its
`workIds`, `orderId` and `fit`** - so the entire Portuguese wizard recommended
nothing at all. Fixed in the app (orrery PR #38), but the content-side rule is
permanent:

> **An overlay carries a path's `title`, `description` and `note` ONLY.
> Never `workIds`, never `orderId`, never `fit`.**

Those are structure, not prose. A translator does not re-pick the books.

Consequences for editing:

- **A path `id` may never be renamed.** Translations key off it (`mergeList`
  merges by id); rename one and the overlay silently detaches, leaving the
  reader English prose in a Portuguese wizard. Ids are permanent, like work ids.
- **Any `title` / `description` / `note` change invalidates the overlay.** Fix
  both sides **in the same commit**, and keep `python scripts/i18n_coverage.py`
  at its current number. A change that drops coverage is unfinished.
- Adding a path means adding its overlay entry too, or coverage falls.

## Auditing an existing block

`startHere` had no owner for a long while: it was written as part of the
research bundle with no sourcing discipline, and it goes stale silently because
nothing downstream re-checks it. What to look for, in order:

1. **Dangling and drifted targets.** The validator catches a `workIds` or
   `orderId` that no longer resolves. It does **not** catch a path that has
   quietly become *wrong* - an order whose contents were reshuffled under it, a
   curated list that no longer matches the description above it. Open every
   order a path points at and read it.
2. **Contradiction with the order's own sources.** Read the order's `rationale`,
   `debated` and `sources`. A path that states as consensus something the
   order's own cited sources contradict is the worst defect in this file,
   because it launders a contested call into advice. This shipped: the Wheel of
   Time `recommended-integrated` path told readers the community places *New
   Spring* after book five, while both sources the order cites recommend after
   book ten.
3. **Advice that predates a completeness audit.** If works were added to
   `works.yaml` since the paths were written, an "essentials" list may now be
   missing an obvious candidate, and a "everything" claim may be describing a
   smaller shelf than exists.
4. **Missing completionist path.**
5. **Unsourced paths** - the main event. Classify each one:
   - **SOURCED** - find the citation, add the comment.
   - **REAL BUT UNSOURCED** - the advice is genuinely and commonly given, but
     you have no citable page. Find one, or flag it. Do not promote it to
     sourced because it feels true.
   - **INVENTED** - no evidence anyone recommends this. Recommend removal.
6. **Fit coverage**, per the loose rule above.

**Do not silently delete a path.** Removing one changes what a reader is told.
List it with a recommendation and let the curator decide. The same goes for a
path you can only weaken: proposing "drop the consensus claim from this
sentence" is a better deliverable than quietly rewriting it.

## Hard rules

- **Never fabricate a source or a consensus.** Not a URL, not a "widely
  recommended", not an author quote. Verify every URL loads and says what you
  attribute to it. An honest "REAL BUT UNSOURCED, flagged" is a good outcome; a
  plausible citation is a lie with a footnote.
- **Two to five paths, always including a completionist path.**
- **Exactly one of `workIds` or `orderId`** per path; more than ~5 works means
  it is an order.
- **Every path names its cost.**
- **Path ids are permanent** - translations key off them.
- **Overlays carry `title` / `description` / `note` only.**
- **Written to need no spoiler gate**, because none exists.
- **No em dashes** (regular dashes, commas, parentheses). Quote YAML values
  containing colons or apostrophes, and quote URLs containing `?` in flow
  sequences.
- **`python scripts/validate.py` green**, and `python scripts/i18n_coverage.py`
  no worse than you found it.

## Process

1. **Read the franchise first** - `works.yaml`, `orders.yaml`, and the existing
   `startHere`. You cannot judge an entry point into a shelf you have not seen.
2. **Find the receipts before writing anything.** Author's site, canonical
   community guide, widely-cited article, in that order, and in the author's
   language. What you find determines what paths exist; do not decide the paths
   first and go looking for support.
3. **Draft the paths from what you found**, two to five, completionist included.
4. **For each, write the cost in one clause.** If you cannot name one, you have
   not understood the path.
5. **Apply the famous-book check** - is the best-known work the door here? If
   not, does a path say so, and is that warning itself sourced?
6. **Spoiler-read every line** as someone who has read nothing.
7. **Tag `fit` honestly**, leaving axes untagged where a path suits anyone.
   Check coverage; do not invent to fill.
8. **Update the pt-PT overlay** in the same commit, prose only.
9. **Validate** - `scripts/validate.py` and `scripts/i18n_coverage.py`.

## Done means

A PR whose body carries **a table of every path with a verdict** - SOURCED (with
the URL), REAL BUT UNSOURCED (with what you searched), or INVENTED (with a
removal recommendation) - plus: which franchises have no `startHere` and whether
they should; every path's stated cost; contested calls you found between a path
and the order it points at; and the translation-coverage number before and
after. Paths you **could not** source are as much of the deliverable as the ones
you fixed, because the curator decides what a reader is told, not you.
