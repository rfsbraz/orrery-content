---
name: reading-orders
description: Author and audit how readers navigate a franchise's shelf - the additional reading orders in orders.yaml and the startHere entry paths in franchise.yaml. Decides which orders earn a slot, writes rationales and paths that name their cost, curates the entry wizard from received community practice, handles the prequel spoiler vector, and keeps both artefacts honest as works are added. Use when adding an order or entry path, reviewing a franchise bundle, or after a completeness audit changes the work list.
---

# reading-orders

Orrery is a reading-order platform. This skill owns both files that tell a
reader how to walk a shelf:

- **`orders.yaml`** - the additional reading orders: the file the product is
  named for, and the one most likely to ship a plausible lie - a list of books
  someone sorted, with a sentence of marketing under it.
- **`startHere`** in `content/franchises/<slug>/franchise.yaml` - the entry
  paths powering the wizard at `/f/<slug>/start`. "Where do I start?" is the
  most asked question about any large body of work, and a wrong answer is the
  one piece of content that can cost a reader the whole shelf.

This skill runs under **`docs/CURATION.md`** (the working contract, including
the aura editorial standard) and does not repeat it. Read it first, then
`docs/SCHEMA.md` (orders, `startHere`, the capabilities table). The `/author`
command (`.claude/commands/author.md`) runs this skill as one stage; its
footprint is exactly these two files.

## 1. Two artefacts, one division of labour

`orders.yaml` answers *"in what sequence?"*. `startHere` answers *"where do I
begin?"*. They interact but are not interchangeable:

> **A path is an entry strategy. An order is a full traversal.**
> The path says who should walk it and what it costs them. The order says what
> the sequence is and where the community disagrees about it.

A path has **exactly one** of `workIds` (a short curated list, usually 1-5
books: "read these") or `orderId` (an order in `orders.yaml`, or the literal
`default` for the derived publication order: "walk this traversal"); the
validator enforces the exclusivity and resolves the `orderId`. The line:
**more than about five works in a path means you are describing an order** -
put it in `orders.yaml` and point the path at it, because a path duplicating
an order's contents in `workIds` drifts out of sync and nothing notices.
Conversely, three paths describing the same long sequence in different words
are one order with one rationale, and an entry strategy of a handful of books
is a path's `workIds`, not a four-book order written so a path can reference
it. Adding an order does not oblige you to add a path; adding a path that
points at an order does oblige you to read that order's `rationale` and
`debated` and confirm the path's prose does not contradict them.

Because one agent owns both sides, **reconcile them in the same pass**. When
order discovery surfaces something path-shaped (an author's "start with this
one", a community's "skip the first two"), or path research surfaces a full
documented sequence, do not route a note to another stage: decide which
artefact it is, write it in the right one, and point the other at it where
warranted.

## 2. The default order is derived. Never author it.

**The default order is publication-chronological over every work in
`works.yaml`, and the app computes it.** It is not in `orders.yaml`, has no id
you can write, and updates itself when a work is added. `orders.yaml` holds
**additional** orders only. So:

- Hand-writing a publication order is a bug: it duplicates a computed view,
  then rots the moment the completeness auditor adds a work, because the copy
  does not update and the derived order does.
- A path that wants "everything, in order" uses `orderId: default` - the only
  correct reference to the derived order, accepted by the validator
  specifically for this.
- A franchise whose only sensible reading is publication order ships **zero**
  orders. That is a complete, correct bundle. `joao-tordo` ships one order for
  26 works and is right to.

**The one nuance that is not a loophole.** `published` is year-precision by
design, so the derived order's within-year sequence is arbitrary. A curated
order that fixes a genuinely known intra-year sequence carries real
information the default cannot: `agatha-christie/poirot-novels` is publication
order, but it settles the 1934, 1936, 1937, 1938 and 1940 ties the derived
sort cannot. If that is your order's whole contribution, **say so in the
rationale** and keep the order narrow. It is not a licence to restate
publication order for a franchise with no ties to break.

`official-publication` as a `type` exists for the rare franchise where a
publisher states an official sequence that **differs** from first-publication
dates. If it does not differ, you are writing the default by hand under a
different name.

## 3. What earns an order a slot

> An order earns a slot only if it produces a **materially different reading
> experience**, for a reader you can name, for a reason they can act on.

Two tests, both required. **The divergence test**: diff the candidate against
the derived default and every order already in the file. A handful of swapped
positions is no order - a reader cannot feel three books moving; they can feel
a thread pulled out of a 48-book shelf, or a prequel moving to the front.
**The actionable-reason test**: finish, without marketing, *"Read this instead
of publication order if you ..."*. "Want a different order" is nothing to act
on; "care most about Vimes and do not want to read the wizard books", "are
re-reading and want the timeline straight", "have five weeks, not five years"
are real.

### Kill on sight

- **Trivial reshuffles** - differing from the default in two places.
- **A "chronological" order for a franchise already chronological.** Most
  single-thread series were published in story order; an in-universe order
  identical to the default is a duplicate wearing a costume.
- **Personal preference with no community behind it.** You are researching
  orders that exist, not inventing one dressed as `curated`.
- **One blog post.** A single listicle is not a community reading practice.
- **An order that exists to make the wing look fuller.** The capabilities
  table lights `orderDiff` at 2+ orders (the derived default counts as one), a
  real temptation to pad to two - the worst reason to add an order, because it
  puts a false path in front of readers to switch on a UI feature.

**Where the honest count lands.** No quota, but calibrate: a linear series
with one genuine debate ships **1-2** orders (`wheel-of-time`); a multi-thread
shelf ships one per thread (`discworld`, six); a cross-series cosmology ships
**2-3** (`cosmere`). More orders than genuine reading strategies dilutes all
of them.

## 4. The four types, and what each demands

`type` is not a label you pick to taste. Each is a **claim about the world**,
and each claim needs different evidence.

**`official-publication`.** A publisher's or estate's stated sequence that
differs from first-publication dates. Evidence: the publisher's own numbering
or catalogue page, cited. If you cannot show the publisher saying it, this is
`curated` and you should say so.

**`chronological-inuniverse`.** A claim that the story happens in this order.
Evidence: a defensible internal chronology, plus two disclosures the rationale
must make: **how undated works are handled** (say which works the timeline
cannot place, where you put them, and why - silence here is the difference
between a reconstruction and a guess), and **where the chronology is not
settled**, in `debated`. If the author has said the dating is deliberately
loose (Sanderson has, explicitly), the rationale must say the order is a
community reconstruction, not a fact. An in-universe order for a franchise
published in story order is a duplicate - check before writing.

**`author-recommended`.** The heaviest claim in the file: a named human
recommended this. **The author must actually have said it** - cite where and
when (their FAQ, their site, a dated interview); "the author would probably
approve" is fabrication. **Authors change their minds, and several famously
have**: if the guidance was revised, cite the later statement and note the
earlier one in `debated`. **Do not over-read a refusal**: Sanderson's own FAQ
declines to mandate an order and offers five acceptable starting points, and
`cosmere/author-recommended` handles this correctly - a sequence that *follows
his stated rules*, with a rationale saying he leaves the order open. Never let
a constructed sequence imply the author dictated it. If the author stated only
a rule ("read each series in its own order") and not a sequence, consider
whether the honest artefact is an order at all, or a `startHere` note.

**`curated` and `community`.** `community` means a documented, converged
practice: **several independent guides agreeing**, or a canonical community
artefact (the L-Space reading-order guides for Discworld, a long-standing
fandom wiki page). One blog post is not a community. `curated` means this
catalogue's editorial arrangement of a real grouping (a publisher-numbered
trilogy, a named thread); it still needs a source for the grouping itself,
even when the sequence is obvious.

## 5. Prequels, publication order, and the spoiler vector

The genuine hard case, and the one most orders get wrong by being neutral. A
prequel is written for readers who have already read forward: its scenes are
built on knowing who these people become, and it routinely names, as
background, things the earlier books spend three volumes revealing. So:

> **An in-universe order that front-loads a prequel is a spoiler vector, not
> just a preference. The rationale must say so.**

`wheel-of-time` is the live case. `New Spring` is set roughly twenty years
before `The Eye of the World`, and reading it first spoils character reveals
in the first two main books. The file handles it correctly: two orders that
are both answers to "where does New Spring go", and the chronological order's
`debated` states plainly that reading it first is widely discouraged for
newcomers. Copy that shape: **name the cost in the rationale**, not only in
`debated` (which is for contested placements) - the reader needs the warning
in the prose they are reading to choose. **Say who it is for anyway** -
re-readers and completionists genuinely want the timeline straight; the
failure mode is an unlabelled order, not the order itself. **Tag the fit
honestly** if a path points at it: `experience: [completionist]`, not `[new]`.
And **do not state the reveal while warning about it** - "spoils character
reveals in the first two books" is the correct amount; naming the reveal to
justify the warning is the exact failure §7 forbids.

The same logic applies beyond prequels: any order that moves a later-published
book earlier is moving a book whose existence assumes the earlier ones. Ask
what that book's first page knows.

## 6. Received, not invented: sourcing both artefacts

CURATION.md states the principle; here is what it demands of these files.
Every non-derived order cites its evidence in `sources`, per §4. Every path
needs evidence that real readers recommend it - **if the only source is our
own reading, it is not a path.** The bar for paths, strongest first: **the
author's own advice** (Sanderson maintains a "Where do I start?" page; that is
as good as evidence gets - check the official site first); **the canonical
community guide** (Dragonmount for Wheel of Time, the Discworld Emporium and
the official reading-order page, a subreddit's pinned FAQ or wiki); **a
widely-cited article** from a publication that actually covers books; and
weakest, **settled fandom consensus** - so uniformly given that any reader of
that fandom would recognise it; say so explicitly and where you saw it, this
tier is the easiest to hallucinate. Below that line: our own judgement, which
is not a path.

**Recording a path's source.** `StartHerePath` has no `sources` field, and
adding one is an app change. Carry the citation as a **YAML comment directly
above the path** - a data citation, exactly what CURATION.md's comment policy
permits (facts about the data, not process). Comments are invisible to the app
and the reader, cost nothing, and survive in git for the next curator:

```yaml
    # Source: https://www.brandonsanderson.com/pages/where-do-i-start
    # "If you consider yourself a fantasy reader, try Mistborn: the Final
    # Empire or The Way of Kings."
    - id: mistborn-first
      title: Start with Mistborn
```

The `note:` field is reader-facing prose, not a citation slot: "Basis: the
publisher-numbered grouping" is a footnote leaking into the museum. Use a note
to tell the reader something useful ("read Roger Ackroyd first for the
shock"); put the receipt in the comment.

## 7. Ungated prose: the engine gives you nothing here

**Order prose and path prose both ship to every visitor, signed in or not.**
There is no `spoilerAfter` on an order (`rationale`, `debated`) and none on a
path (`title`, `description`, `note`) - and `/f/<slug>/start` is by definition
the page for people who have read nothing. Everything in these two files must
be written so that it needs no gate.

The risk is structural: a path that starts mid-series exists precisely because
there are earlier books, and the natural way to justify it is to say what
happens in them. Concretely: naming which book a character first appears in
can be a reveal; "by this point X has happened" is a spoiler even when X
sounds like setup; a subseries description can spoil the main sequence (who
survives to have their own thread is information); and even a work **title**
in a `workIds` list is visible - a title that is itself a reveal cannot be
hidden by careful prose around it.

Write at the level of premise and appeal - the level a back cover works at -
and the problem does not arise. A path that cannot be justified without a
spoiler is wrong for a newcomer, which is useful information, not a formatting
problem. Cross-reference `.claude/skills/spoiler-audit/SKILL.md`: order prose
and `startHere` are both in its scope precisely because the engine cannot
protect them, and it calls order prose "systematically under-checked" for
exactly this reason.

## 8. Name the cost. Always.

Anyone can sort books. The value Orrery adds is the sentence that tells a
reader whether this way in is for them - and it works identically for an
order's rationale and a path's description. Each states: **who it suits** (a
named reader, not "fans of the series"), **what it gains** (the specific thing
this arrangement makes possible), and **what it sacrifices**. Always.

**An order or path with no stated cost has not been thought about.** Every
route trades something: first-read surprise, momentum, tonal coherence, the
author's own escalation, the development you see reading in order (the writer
getting better in front of you), or simply the books it leaves out. It is the
fastest way to tell curation from marketing: marketing lists benefits. If you
genuinely cannot find the cost, the order fails the divergence test or the
path is padding, and it should not exist.

Good and bad, from the files: `wheel-of-time/chronological` states the cost in
its own rationale ("you trade several first-read surprises for a strictly
linear timeline") - the standard. So does `cosmere/chronological-inuniverse`
("Not recommended for a first read - several early-set books were published
later and spoil books set after them"). `discworld/death` says the books are
warm and philosophical and names the characters, but never says what a thread
reading costs: you lose the Disc's chronological development, meet running
jokes mid-flight, and Death cameos in books this path skips. The gain is
stated, the sacrifice is not.

For a path, the cost belongs in the `description` or `note`, in the reader's
language, not hedged into invisibility; one honest clause is enough. Keep
rationales reader-facing prose; curator reasoning belongs in `debated`
(contested placements, with the argument for each side) or a sourcing comment.

## 9. Coverage and honesty

An order may be **complete** (every work) or **partial** (a thread, a series,
a route). Both are legitimate. Only one thing is not:

> **Never silently drop a work from an order.**

A reader in a completionist catalogue reasonably assumes an order is the whole
picture unless told otherwise. So: **a partial order says it is partial, in
the rationale**, naming the shape of what is excluded ("novels only", "the
three Moist von Lipwig books", "the main sequence plus the prequel"). **Works
that fit nowhere get named in `debated`** - collections containing a series
novella, companions, anthologies, the nonfiction - saying where a reader can
slot them, or that guides disagree; `agatha-christie` does this well, both
orders explicitly novels-only with `debated` naming exactly which short-story
collections were left out and that guides disagree on placement. **A work in
no order at all is fine** and needs no apology; the derived default covers
every work by construction. The failure is a work excluded from an order that
*looks* like it should contain it.

Before shipping: for each order, list the works in its declared scope that it
does not contain, and confirm each absence is either obvious or stated.

## 10. `startHere`: the wizard and its judgement

The wizard asks the reader two questions and scores the declared paths. There
is no per-franchise app code; the content is the whole feature.

| Axis | Values | The question |
|---|---|---|
| `fit.experience` | `new` / `returning` / `completionist` | how much of this author have you read? |
| `fit.commitment` | `taste` / `arc` / `complete` | a few books, one thread, or everything? |

Scoring (`lib/wizard/match.ts`): an exact tag match scores 2 per axis; a path
declaring **no** tags on an axis scores 1 there, a soft universal fit. Ties
keep curator order, because the order is editorial. Every path is always
returned - the top one is the recommendation, the rest render as alternatives.
Two consequences: **there is no "no match" state** - a thin or badly tagged
set does not fail loudly, it just quietly gives bad advice, and nothing will
catch that but this skill. And **a franchise with no `startHere` simply has no
wizard** (`capabilities()` activates on `startHere.paths.length > 0`) - a
complete, correct bundle, not a gap. No wizard beats one built out of guesses.

**Two to five paths, always including a completionist path** (almost always
`orderId: default` - someone will want the whole thing, and a wizard that
cannot say so looks like it is hiding the shelf). Fewer than two is a
redirect, not a wizard - though see the sparse-author rule below, where one
path is right. More than five is a menu, not advice: the reader came here
because the shelf was already too big.

**The famous-book trap.** The best-known work is often the worst entry point -
not a paradox, just what fame does. The recurring shapes: **the unfinished or
sprawling cycle** the author is famous for, demanding commitment before the
reader knows if they like the writing (King's Dark Tower); **the atypical
masterpiece** that represents the author badly - brilliant, and nothing else
on the shelf is like it; **the late-career book** that quietly assumes the
earlier ones, its power built on twenty years of context the newcomer does not
have; and **the first book that is visibly a first book** - series that found
themselves later open on their weakest material, so publication order hands
the newcomer the worst chapter first (Discworld's Rincewind openers).

The rule: **judge an entry point by what it does for someone who has read
nothing, not by what it means to someone who has read everything** - fame,
sales and awards measure the second thing. Where it applies, the path must say
so: a reader who has heard of exactly one book will assume it is the door, and
be quietly confused when the wizard sends them elsewhere; tell them why in one
sentence and the recommendation gains authority. The discipline still holds:
the warning itself must be received advice. "Do not start with *The Colour of
Magic*" is only shippable if you can point at readers actually saying it;
otherwise it is a flag for the curator, not a sentence to write with
confidence.

**Fit-matrix coverage is loose.** Nine cells exist; you are not filling them.
Gaps are fine - the app falls back to the best partial match and always
returns something. **Do NOT invent a path to fill a cell**: a fabricated path
scored perfectly is worse than a real path scored approximately, because the
reader takes the recommendation either way. Leaving an axis untagged is a
deliberate tool, not laziness: a soft universal fit rather than a miss. The
one shape worth checking: `new` + `taste` (a curious newcomer) and
`completionist` + `complete` (the full walk) are the two most-used answers; if
neither is covered, the wizard is mistargeted.

**Sparse and non-English authors.** Two padding temptations. For an author
with a dozen books and no subseries, the honest answer may be "start at the
beginning" and **one path** - a correct bundle. Manufacturing a "thematic
entry" and a "short works entry" to reach three invents two of them; if one
path is the truth and one feels too thin to ship, ship no `startHere` and no
wizard. For a non-anglophone author, look for the entry advice **in that
language**: Portuguese readers recommending João Tordo, not English ones -
anglophone coverage of a Portuguese literary novelist is thin, late and
derivative. Search the author's own site, the publisher, the national press,
the local book community. And be willing to conclude that **"no citable
entry-path consensus exists"** - a real, useful finding, said in the PR. A
prize and a publisher grouping are facts, and neither is a reader saying
"start here".

## 11. pt-PT overlays: prose only, same commit

One rule for both artefacts: **an overlay carries prose, never structure.**

- Order overlays (`content/i18n/pt-PT/franchises/<slug>/orders.yaml`, keyed by
  order id) carry `name`, `rationale` and `debated` only - never
  `orderedWorkIds` or `type`. An order's `name` **is** translatable and should
  be: it is a curated label a reader reads, and `validate.py` allows `name` in
  order overlays specifically. The existing pt-PT order overlays carry a
  header comment claiming the opposite and translate no names; the comment is
  wrong and the names are a real coverage gap.
- Path overlays carry `title`, `description` and `note` only - **never
  `workIds`, never `orderId`, never `fit`**. Hard rule from a bug that
  shipped: overlays once copied nested values wholesale over the base, every
  pt-PT path lost its `workIds`, `orderId` and `fit`, and the entire
  Portuguese wizard recommended nothing at all. Fixed in the app (orrery PR
  #38), but the content-side rule is permanent: structure is not prose, and a
  translator does not re-pick the books.

Consequences: order and path ids are load-bearing for translation too
(`mergeList` merges by id; rename one and the overlay silently detaches,
leaving English prose in a Portuguese wizard), and order ids are additionally
referenced by `startHere.orderId` and achievement `criteria.orderId`, so a
rename breaks a badge readers have earned. Any prose change on either artefact
means fixing both sides **in the same commit**; adding an order or a path
means adding its overlay entry too, or coverage falls.

## 12. Auditing: both artefacts decay silently

Authoring is the smaller half. Nothing about a stale order or a drifted path
fails CI. Run this audit whenever you touch a franchise, and always after a
completeness audit.

**Dangling ids.** `scripts/validate.py` catches unresolvable `workIds` and
`orderId`s, on orders and paths alike - the one failure mode already handled.

**Orders that duplicate the derived default.** Sort the order's works by
publication year and compare. A match means the order adds nothing structural
and survives only if its prose carries something real (a thread identity, a
tie-break, a documented community practice) - say which, in the PR. Note that
**all six Discworld thread orders are exactly their `subseries` filtered and
sorted by year** - justified by the thread identity and the L-Space guide, but
also hand-maintained copies of a computable view, so a later correction to a
work's `subseries` will silently desynchronise them.

**Rationales gone stale.** Prose written against a smaller catalogue. Header
comments count: `stephen-king/orders.yaml` still opens by declaring
`works.yaml` "a first pass (core novels + Dark Tower + Bachman + key
collections)" and calls completing it a TODO, against a `works.yaml` that now
holds 95 works. The comment is now false, and a future agent will trust it.

**Orders whose meaning changed when works were added.** The dangerous one, and
invisible. An order described as complete, or as covering a subseries, becomes
a lie the moment the completeness auditor adds works to that scope; nothing
errors, the order simply now excludes books it claims to cover. After every
completeness pass, re-derive each order's declared scope from `works.yaml` and
diff it against the order's contents. The live example:
`stephen-king/dark-tower-connected` contains `black-house` (2001) but **not**
`the-talisman` (1984), book one of the same two-book sequence and the book
`black-house` continues - a reader following it meets a sequel cold. Either
the order needs `the-talisman` or the rationale must say why it was left out.

**Silent drops.** Check every order against the works its scope implies. In
`cosmere`, `author-recommended` omits `white-sand`, `mistborn-secret-history`,
`shadows-for-silence`, `sixth-of-the-dusk` and `the-hope-of-elantris` while
presenting itself as following Sanderson's rules for the whole Cosmere, and
`debated` mentions none of them; `recommended-reading-order` drops
`white-sand` without a word. Exactly the omissions §9 forbids.

**Coverage of the franchise's own groupings.** Where one named series has an
order, ask why its siblings have none. `joao-tordo` has an order for the
publisher-numbered `Trilogia dos Lugares Sem Nome` and none for the three-book
`Pilar Benamor` sequence, also a named, numbered grouping. Either is
defensible; the inconsistency needs a reason.

**Drifted path targets.** The validator does not catch a path that has quietly
become *wrong*: an order reshuffled under it, a curated list that no longer
matches the description above it. Open every order a path points at and read
it.

**Contradiction with the order's own sources.** A path stating as consensus
something the order's own cited sources contradict is the worst defect in
these files - it launders a contested call into advice. This shipped: the
Wheel of Time `recommended-integrated` path told readers the community places
*New Spring* after book five, while both sources the order cites recommend
after book ten.

**Advice that predates a completeness audit.** If works were added since the
paths were written, an "essentials" list may be missing an obvious candidate
and an "everything" claim may describe a smaller shelf than exists. Check for
a **missing completionist path** while you are there.

**Unsourced paths** - the main event. Classify each one: **SOURCED** (find the
citation, add the comment); **REAL BUT UNSOURCED** (genuinely and commonly
given advice with no citable page - find one, or flag it; do not promote it to
sourced because it feels true); **INVENTED** (no evidence anyone recommends
this - recommend removal).

**Do not silently delete an order or a path.** Removing either changes what a
reader is told. List it with a recommendation and let the curator decide. The
same goes for one you can only weaken: proposing "drop the consensus claim
from this sentence" is a better deliverable than quietly rewriting it.

## Hard rules

- **Never author the publication order by hand**; reference the derived order
  with `orderId: default`.
- **`type` must be one of** `official-publication`,
  `chronological-inuniverse`, `author-recommended`, `curated`, `community` -
  the validator rejects anything else. An `author-recommended` order without a
  datable statement from the author is fabrication, whatever the sequence
  looks like.
- **Exactly one of `workIds` or `orderId`** per path; more than ~5 works means
  it is an order.
- **Two to five paths, always including a completionist path** (or none at
  all, or one path for a sparse shelf that honestly supports only one).
- **Every order and every path names its cost.**
- **All prose in both files is ungated**; written to need no spoiler gate,
  because none exists.
- **Overlays carry prose only** (order `name`/`rationale`/`debated`, path
  `title`/`description`/`note`), in the same commit as the base change.

## Process

1. **Read the franchise first**: `works.yaml` (and know the count),
   `orders.yaml`, the existing `startHere`.
2. **Derive the default** (all works, sorted by `published`) to diff
   candidates against. Nothing you write may reproduce it.
3. **Audit what is already there** per §12, on both artefacts.
4. **Research what exists**: author statements, publisher numbering, community
   guides, entry advice in the author's own language. You are documenting
   practice, not designing it. Reconcile order-shaped and path-shaped findings
   in this same pass (§1).
5. **Apply the two tests** in §3 to every order candidate, and write the
   rejections down. A rejected order with a reason is a deliverable.
6. **Write the rationale before the list**, and each path's cost in one
   clause. If you cannot name who it is for, what it gains, and what it
   costs, the list is not worth sorting.
7. **Check the prequel and famous-book cases** (§5, §10), then re-read every
   line of prose as an anonymous newcomer (§7).
8. **Tag `fit` honestly**, untagged where a path suits anyone; check coverage
   loosely, never invent to fill. Confirm no path promises something its
   order no longer delivers.
9. **Mirror all prose into pt-PT** per §11, then run the gates from
   CURATION.md §3 and report the deltas.

## Done means

A PR whose body states: each order added or changed with its type, its
evidence, and the one sentence naming who it suits, what it gains and **what
it costs**; a table of every path with a verdict (SOURCED with the URL, REAL
BUT UNSOURCED with what you searched, INVENTED with a removal
recommendation); every candidate **rejected** and why; the audit result for
every pre-existing order and path, including the ones you changed nothing
about; every work an order's declared scope omits, with the reason; contested
calls between a path and the order it points at, and any path whose promise
you had to adjust; which franchises have no `startHere` and whether they
should; and the i18n coverage delta. Validator green.

An `orders.yaml` that reports every order healthy has probably not been diffed
against `works.yaml`, and paths you could not source are as much of the
deliverable as the ones you fixed - the curator decides what a reader is told,
not you.
