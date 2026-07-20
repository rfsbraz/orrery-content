---
name: reading-orders
description: Author and audit a franchise's additional reading orders in orders.yaml - deciding which orders earn a slot, writing rationales that state what an order costs as well as what it gains, handling the prequel and in-universe chronology problem, and keeping orders honest as works are added. Use when adding an order, reviewing a franchise bundle, or after a completeness audit changes the work list.
---

# reading-orders

Orrery is a reading-order platform. `orders.yaml` is the file the product is
named for, and it is the file most likely to ship a plausible lie: a list of
books someone sorted, with a sentence of marketing under it.

This skill owns that file. Read `docs/SCHEMA.md` (orders, `startHere`, and the
capabilities table) first, and the **aura editorial standard** in the
`franchise-research` skill for the house bar on what earns a slot. Reading
orders are held to the same kind of bar, applied to a different artefact.

## 1. The default order is derived. Never author it.

**The default order is publication-chronological over every work in
`works.yaml`, and the app computes it.** It is not in `orders.yaml`, it has no
id you can write, and it updates itself when a work is added.

`orders.yaml` holds **additional** orders only. So:

- An agent hand-writing a publication order is a bug, not a thin contribution.
  It duplicates a computed view, then rots the moment the completeness auditor
  adds a work, because the hand-written copy does not update and the derived one
  does.
- A `startHere` path that wants "everything, in order" uses
  `orderId: default`. That literal is the only correct way to reference the
  derived order, and the validator accepts it specifically for this.
- A franchise whose only sensible reading is publication order ships **zero**
  orders. That is a complete, correct bundle. `joao-tordo` ships one order for
  26 works and is right to.

**The one nuance that is not a loophole.** `published` is year-precision by
design, so the derived order's within-year sequence is arbitrary. A curated
order that fixes a genuinely known intra-year sequence carries real information
the default cannot. `agatha-christie/poirot-novels` does exactly this: it is
publication order, but it settles the 1934, 1936, 1937, 1938 and 1940 ties that
the derived sort cannot. If that is your order's whole contribution, **say so in
the rationale** and keep the order narrow. It is not a licence to restate
publication order for a franchise with no ties to break.

`official-publication` as a `type` exists for the rare franchise where a
publisher states an official sequence that **differs** from first-publication
dates. If it does not differ, you are writing the default by hand under a
different name.

## 2. What earns an order a slot

The bar, and it is high:

> An order earns a slot only if it produces a **materially different reading
> experience**, for a reader you can name, for a reason they can act on.

Two tests, both required.

**The divergence test.** Diff the candidate against the derived default (and
against every order already in the file). If the difference is a handful of
swapped positions, there is no order here. A reader cannot feel three books
moving; they can feel a thread being pulled out of a 48-book shelf, or a prequel
moving to the front.

**The actionable-reason test.** Finish this sentence without marketing: *"Read
this instead of publication order if you ..."*. If the ending is "want a
different order", there is nothing to act on. If it is "care most about Vimes
and do not want to read the wizard books", "are re-reading and want the timeline
straight", or "have five weeks, not five years", the order is real.

### Kill on sight

- **Trivial reshuffles.** An order that differs from the default in two places.
- **A "chronological" order for a franchise that is already chronological.**
  Most single-thread series were published in story order; an in-universe order
  identical to the default is a duplicate wearing a costume.
- **Personal preference with no community behind it.** You are researching
  orders that exist. Do not invent one and dress it as `curated`.
- **One blog post.** A single listicle is not a community reading practice.
- **An order that exists to make the wing look fuller.** The capabilities table
  lights `orderDiff` at 2+ orders (the derived default counts as one), which is
  a real temptation to pad to two. Padding for a capability is the worst reason
  to add an order, because it puts a false path in front of readers to switch on
  a UI feature.

### Where the honest count lands

There is no quota, but calibrate against what the catalogue supports: a linear
series with one genuine debate ships **1-2** orders (`wheel-of-time`); a
multi-thread shelf ships one per thread (`discworld`, six); a cross-series
cosmology ships **2-3** (`cosmere`). A franchise with more orders than genuine
reading strategies has diluted all of them.

## 3. The four types, and what each demands

`type` is not a label you pick to taste. Each type is a **claim about the
world**, and each claim needs different evidence.

### `official-publication`

A publisher's or estate's stated sequence that differs from first-publication
dates. Evidence: the publisher's own numbering or catalogue page, cited. If you
cannot show the publisher saying it, this is a `curated` order and you should
say so.

### `chronological-inuniverse`

A claim that the story happens in this order. Evidence: a defensible internal
chronology, plus **two disclosures the rationale must make**:

- **How undated works are handled.** Every long franchise has works the
  timeline cannot place. Say which, and where you put them and why. Silence here
  is the difference between a reconstruction and a guess.
- **Where the chronology is not settled**, in `debated`. If the author has said
  the dating is deliberately loose (Sanderson has, explicitly), the rationale
  must say the order is a community reconstruction, not a fact.

An in-universe order for a franchise published in story order is a duplicate.
Check before writing.

### `author-recommended`

The heaviest claim in the file: that a named human recommended this. Rules:

- **The author must actually have said it.** Cite where and when: their FAQ,
  their site, an interview with a date. "The author would probably approve" is
  fabrication.
- **Authors change their minds, and several famously have.** If the guidance was
  revised, cite the later statement and note the earlier one in `debated`.
- **Do not over-read a refusal.** Sanderson's own FAQ declines to mandate an
  order and offers five acceptable starting points. `cosmere/author-recommended`
  handles this correctly: it presents a sequence that *follows his stated rules*
  and says in the rationale that he leaves the order open. Never let a
  constructed sequence imply the author dictated it.
- If the author only stated a rule ("read each series in its own order") and not
  a sequence, consider whether the honest artefact is an order at all, or a
  `startHere` note.

### `curated` and `community`

`community` means a documented, converged practice. Evidence is **several
independent guides agreeing**, or a canonical community artefact (the L-Space
reading-order guides for Discworld, a long-standing fandom wiki page). One blog
post is not a community.

`curated` means this catalogue's editorial arrangement of a real grouping (a
publisher-numbered trilogy, a named thread). It still needs a source for the
grouping itself, even when the sequence is obvious.

## 4. Prequels, publication order, and the spoiler vector

This is the genuine hard case, and the one most orders get wrong by being
neutral about it.

A prequel is written for readers who have already read forward. Its scenes are
built on knowing who these people become, and it routinely names, as background,
things the earlier books spend three volumes revealing. So:

> **An in-universe order that front-loads a prequel is a spoiler vector, not
> just a preference. The rationale must say so.**

`wheel-of-time` is the live case in this catalogue. `New Spring` is set roughly
twenty years before `The Eye of the World`, and reading it first spoils
character reveals in the first two main books. The file handles it correctly:
two orders that are both answers to the "where does New Spring go" question, and
the chronological order's `debated` states plainly that reading it first is
widely discouraged for newcomers. Copy that shape.

What that shape requires of you:

- **Name the cost in the rationale**, not only in `debated`. `debated` is for
  contested placements; a reader choosing this path needs the warning in the
  prose they are reading to choose.
- **Say who it is for anyway.** Re-readers and completionists genuinely want the
  timeline straight, and the order should exist for them. The failure mode is an
  unlabelled order, not the order itself.
- **Tag the fit honestly** if a `startHere` path points at it:
  `experience: [completionist]`, not `[new]`.
- **Do not state the reveal while warning about it.** "Spoils character reveals
  in the first two books" is the correct amount. Naming the reveal in order to
  justify the warning is the exact failure `spoiler-audit` catches, and
  `orders[].rationale` and `orders[].debated` are **ungated prose that ships to
  every reader, signed in or not**. There is no `spoilerAfter` on an order.
  Cross-reference `.claude/skills/spoiler-audit/SKILL.md`, which calls order
  prose "systematically under-checked" for exactly this reason.

The same logic applies beyond prequels: any order that moves a later-published
book earlier is moving a book whose existence assumes the earlier ones. Ask what
that book's first page knows.

## 5. The rationale is the deliverable. The list is not.

Anyone can sort books. The value Orrery adds is the sentence that tells a reader
whether this path is for them.

Every rationale states three things:

1. **Who it suits.** A named reader, not "fans of the series".
2. **What it gains.** The specific thing this arrangement makes possible.
3. **What it sacrifices.** The cost. Always.

**An order with no stated cost has not been thought about.** Every order trades
something: first-read surprise, momentum, tonal coherence, the author's own
sense of escalation, or simply the books it leaves out. If you genuinely cannot
find the cost, that is strong evidence the order fails the divergence test and
should not exist.

Good and bad, from the file:

- `wheel-of-time/chronological` states the cost in its own rationale ("you trade
  several first-read surprises for a strictly linear timeline"). This is the
  standard.
- `cosmere/chronological-inuniverse` states it ("Not recommended for a first
  read - several early-set books were published later and spoil books set after
  them"). Also the standard.
- `discworld/death` says the books are warm and philosophical and names the
  characters. It never says what a thread reading costs: you lose the Disc's
  chronological development, you meet running jokes mid-flight, and Death cameos
  in books this path skips. The gain is stated, the sacrifice is not.

Keep the rationale reader-facing prose, not curator notes. Curator reasoning
belongs in `debated` (contested placements, with the argument for each side) or
in a YAML comment.

## 6. Coverage and honesty

An order may be **complete** (every work) or a **partial path** (a thread, a
series, a route). Both are legitimate. Only one thing is not:

> **Never silently drop a work from an order.**

A reader looking at an order in a completionist catalogue reasonably assumes it
is the whole picture unless told otherwise. So:

- **A partial order says it is partial, in the rationale.** Name the shape of
  what is excluded ("novels only", "the three Moist von Lipwig books", "the main
  sequence plus the prequel").
- **Works that fit nowhere get named in `debated`.** Collections that contain a
  series novella, companions and maps, anthologies, the nonfiction. Say where a
  reader can slot them, or say that guides disagree. `agatha-christie` does this
  well: both orders are explicitly novels-only and `debated` says exactly which
  short-story collections were left out and that guides disagree on placement.
- **A work in no order at all is fine** and needs no apology; the derived
  default covers every work by construction. The failure is a work excluded from
  an order that *looks* like it should contain it.

The test to run before shipping: for each order, list the works in its declared
scope that it does not contain, and confirm each absence is either obvious or
stated.

## 7. `startHere` is related, and different

`orders.yaml` answers *"in what sequence?"*. `startHere` (in `franchise.yaml`)
answers *"where do I begin?"*. They interact but are not interchangeable.

- A `startHere` path has **exactly one** of `workIds` (a short curated list,
  usually 1-5 books) or `orderId` (an order in `orders.yaml`, or the literal
  `default`). The validator enforces the exclusivity and resolves the `orderId`.
- **Two to five paths, always including a completionist path**, which is
  normally `orderId: default`.
- `fit.experience` (`new` / `returning` / `completionist`) and `fit.commitment`
  (`taste` / `arc` / `complete`) are how the wizard scores paths. Tag honestly:
  a path pointing at a spoiler-carrying chronological order is not
  `experience: [new]`, whatever its appeal.

The useful division of labour: **an entry strategy that is a handful of books is
a `startHere` path with `workIds`; a full sequence is an order that a path points
at.** If you find yourself writing an order of four books so a path can reference
it, write the path's `workIds` instead. Conversely, if three `startHere` paths
all describe the same long sequence in different words, that is one order with
one rationale.

Adding an order does not oblige you to add a path. Adding a path that points at
an order does oblige you to check the order's rationale still matches what the
path promises.

## 8. Auditing existing orders

Authoring is the smaller half. Orders decay silently, because nothing about them
fails CI. Run this audit whenever you touch a franchise, and always after a
completeness audit.

**Dangling `workIds`.** `scripts/validate.py` catches these, so they are the one
failure mode that is already handled. Run it and move on.

**Orders that duplicate the derived default.** Sort the order's own works by
publication year and compare. If they match, the order adds nothing structural
and survives only if its prose carries something real (a thread identity, a
tie-break, a documented community practice). Say which, in the PR. Note that
**all six Discworld thread orders are exactly their `subseries` filtered and
sorted by year** - they are justified by the thread identity and the L-Space
guide, but they are also hand-maintained copies of a computable view, so a later
correction to a work's `subseries` will silently desynchronise them.

**Rationales gone stale.** Prose written against a smaller catalogue.
Header comments count: `stephen-king/orders.yaml` still opens by declaring
`works.yaml` "a first pass (core novels + Dark Tower + Bachman + key
collections)" and calls completing it a TODO, against a `works.yaml` that now
holds 95 works. The comment is now false, and a future agent will trust it.

**Orders whose meaning changed when works were added.** This is the dangerous
one and it is invisible. An order described as complete, or as covering a
subseries, becomes a lie the moment the completeness auditor adds works to that
scope. Nothing errors. The order simply now excludes books it claims to cover.
After every completeness pass, re-derive each order's declared scope from
`works.yaml` and diff it against the order's contents.

The live example: `stephen-king/dark-tower-connected` contains
`black-house` (2001) but **not** `the-talisman` (1984), which is book one of the
same two-book sequence and the book `black-house` continues. A reader following
this order meets a sequel cold. Either the order needs `the-talisman` or the
rationale needs to say why it was left out.

**Silent drops.** Check every order against the works its scope implies. In
`cosmere`, `author-recommended` omits `white-sand`, `mistborn-secret-history`,
`shadows-for-silence`, `sixth-of-the-dusk` and `the-hope-of-elantris` while
presenting itself as following Sanderson's rules for the whole Cosmere, and
`debated` mentions none of them. `recommended-reading-order` drops `white-sand`
without a word. These are exactly the omissions §6 forbids.

**Coverage of the franchise's own groupings.** Where a franchise gives one named
series an order, ask why its siblings have none. `joao-tordo` has an order for
the publisher-numbered `Trilogia dos Lugares Sem Nome` and none for the
three-book `Pilar Benamor` sequence, which is also a named, numbered grouping.
Either is defensible; the inconsistency needs a reason.

## Hard rules

- **Never fabricate an order, and never attribute one to an author who did not
  give it.** Every non-derived order cites its source in `sources`. An
  `author-recommended` order without a datable statement from the author is
  fabrication, whatever the sequence looks like.
- **Never author the publication order by hand.** It is derived. Use
  `orderId: default` to reference it.
- **Order ids are permanent.** They are referenced by `startHere.orderId` and by
  achievements `criteria.orderId` (`order_complete`), and the validator resolves
  both. Renaming an id breaks a badge readers have earned. Rewrite the `name`
  and the prose freely; never the `id`.
- **Every `workId` must resolve.** `python scripts/validate.py` enforces it, and
  a PR failing on a dangling reference was not finished.
- **`type` must be one of** `official-publication`, `chronological-inuniverse`,
  `author-recommended`, `curated`, `community`. The validator rejects anything
  else.
- **Order prose is ungated and ships to everyone.** No `spoilerAfter` exists on
  an order. Say what the order does without saying what it pays off.
- **Adding or changing an order's prose needs a pt-PT overlay** in
  `content/i18n/pt-PT/franchises/<slug>/orders.yaml`, keyed by the order id and
  carrying `name`, `rationale` and `debated` only, never `orderedWorkIds` or
  `type`. Without it you have shipped a coverage regression. Run
  `python scripts/i18n_coverage.py` and report the delta.
  An order's `name` **is** translatable and should be translated: it is a
  curated label a reader reads, and `validate.py` allows `name` in overlays for
  `orders.yaml` specifically. The existing pt-PT order overlays carry a header
  comment claiming the opposite and translate no names; the comment is wrong and
  the names are a real coverage gap.
- **No em dashes.** Quote YAML values containing colons or apostrophes, and
  quote URLs with query strings inside flow sequences.

## Process

1. **Read `works.yaml` first**, and know the count. Every judgement below is
   made against the real work list, and stable work ids are the only thing an
   order may contain.
2. **Derive the default** (all works, sorted by `published`) so you have
   something to diff candidates against. Nothing you write may reproduce it.
3. **Audit what is already there** per §8 before adding anything: duplicates of
   the default, stale prose and header comments, silent drops, scope drift since
   the last completeness pass.
4. **Research the orders that exist.** Author statements, publisher numbering,
   community guides. You are documenting practice, not designing it.
5. **Apply the two tests** in §2 to every candidate, and write the rejections
   down. A rejected order with a reason is a deliverable.
6. **Write the rationale before the list.** If you cannot name who it is for,
   what it gains, and what it costs, the list is not worth sorting.
7. **Check the prequel and reordering cases** against §4, and re-read the
   rationale as ungated prose that any anonymous visitor sees.
8. **Reconcile `startHere`** per §7: paths resolve, fits are honest, no path
   promises something its order no longer does.
9. **Mirror the prose into pt-PT**, then run `python scripts/validate.py` until
   green and `python scripts/i18n_coverage.py` for the delta.

## Done means

A PR whose body states: each order added or changed with its type, its evidence,
and the one sentence naming who it suits, what it gains and **what it costs**;
every candidate **rejected** and why (as useful as what shipped); the audit
result for every pre-existing order in the franchise, including the ones you
changed nothing about; every work in an order's declared scope that the order
omits, with the reason it is omitted; any `startHere` path whose promise you had
to adjust; and the i18n coverage delta. Validator green.

An `orders.yaml` that reports every order healthy has probably not been diffed
against `works.yaml`.
