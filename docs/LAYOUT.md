# The Orrery timeline layout grammar

The river is a life told down a page. This document defines the **grammar** that
lets it be told with rhythm instead of as a stack of identical cards.

It has two orthogonal axes, and keeping them separate is the whole point:

- **`organisation`** - how a cell lays image and text out. The **app** renders
  these. This is where *variety* lives.
- **`illustration_type`** - what the artwork depicts and how it is authored.
  The **generator** makes these (see `VISUAL.md`). This is where *cohesion*
  lives (one author visual system, applied uniformly).

Cohesion and variety used to fight on one axis, so a wing could only be same
(monotonous) or drifting (incoherent). Split apart, a wing is visually uniform
in *style* and deliberately varied in *shape*. A magazine is cohesive across a
dozen layouts per issue; so is this.

Two more fields refine an entry:

- **`treatment`** - a surface finish, author/era specific (`photocopy-grain`,
  `palimpsest`, `restrained-rust-accent`). Open set; see the wing's `theme.art`.
- **`modifier`** - a composition twist applied to a compatible organisation
  (`breakout`, `pull-focus`, `fold-reveal`, `anchor-with-satellites`, `branch`).

## Whole images, even for composed organisations

A multi-part organisation (`diptych`, `strip`, `mosaic`, `split-counterpoint`,
`layered-stack`) is generated as **one complete image**, not assembled by the
app from separate subject assets. This is a deliberate ruling: gpt-image is
weakest exactly at multi-panel layout, so the risk is real, but the single-image
route is simpler to render and file, and it is what we are trying first. **If
composed images come back unreliable, the fallback is app-side composition from
per-subject assets** - which is why `images_required` (below) already lets an
entry carry more than one asset. Do not build anything that forecloses that
retreat.

## Schema fields (on an event / life-event)

```yaml
organisation: artifact-spread          # one of the 16 below; default `beside`
illustration_type: manuscript-proof    # one of VISUAL.md's 25; drives the art
treatment: [photocopy-grain]           # optional surface finishes
modifier: breakout                     # optional; must be compatible (below)
images_required: 1                     # how many image slots this entry needs
```

`images_required` is the field that makes the pipeline future-proof: a `beside`
needs 1, a `diptych` needs 2, a `strip` may need several, an `epigraph` needs
none. The issue writer records it, and the asset processor uses it to know how
many images to pull from an issue and how to file them (`<id>.webp`,
`<id>-2.webp`, ...). It is **1** unless the organisation's spec says otherwise;
at **0** no art issue is opened at all.

## The organisations

Each spec gives what the **app** must render (desktop + mobile), what the
**generator** must produce (image count + aspect + background), the illustration
types it can hold, and the moments it fits. Aspect and background are the art
contract; the app must not assume a square.

Slugs are the contract - use them verbatim in content, validator, and app.

---

### `beside` - the workhorse
Two neighbouring regions in one restrained cell: prose one side, one
self-contained illustration the other, ~45/55, alternating side down the page.
Shared surface, no heavy divider.
- **Desktop**: prose and art side by side; rail + date marker outside the cell.
- **Mobile**: prose first, art second at its own aspect; never two shrunk columns.
- **Images**: 1 · aspect `4:3`/`3:2`/`1:1` · background transparent (dissolve).
- **Holds**: every illustration type EXCEPT the three artifact types
  (`document-facsimile`, `manuscript-proof`, `archive-stack`) - those need
  `artifact-spread`, which skips the dissolve their drawn edge requires.
- **Use**: ordinary and medium-weight events. The default; most of a wing is this.

### `full-bleed-vista` - the breath
A wide establishing illustration spanning the full content column; prose in a
separate block above or below, never overlaid.
- **Desktop**: panoramic image across the column; prose a narrow block to one side or above.
- **Mobile**: image reaches both edges; prose above or below, never beside.
- **Images**: 1 · aspect `16:9`/`3:2` · background **opaque**.
- **Holds**: `establishing-landscape`, `place-portrait`, `map-route`, `journey-transit`.
- **Use**: birthplace, arrival, migration, a new city, the opening of a period. A pause.

### `immersion` - the total stop
The artwork is the full-width background surface; prose sits **over** it inside a
deliberate low-detail quiet zone (~35-45% of the frame).
- **Desktop**: full-width deep composition; text anchored left or right to the quiet zone.
- **Mobile**: crop responsively around the subject; preserve the quiet zone; text stays part of the image, never a separate card.
- **Images**: 1 · aspect `3:2`/`16:9` · background **opaque**, authored for overlay (quiet zone reserved).
- **Holds**: `portrait-of-absence`, `establishing-landscape`, `symbolic-still-life`, `atmospheric-motif-field`.
- **Use**: the one or two largest ruptures in a life - a death, sudden fame, catastrophe, breakthrough. Cap it hard (see rotation budget).

### `floating-object` - the aside on the page
One small isolated object placed directly on the editorial page (no card),
prose wrapping or margined around it.
- **Desktop**: object 15-28% of the cell, offset into a corner or the wide margin; text wraps.
- **Mobile**: object beside the first paragraph or offset between sections; never enlarged.
- **Images**: 1 · aspect `1:1`/`4:5` · background **transparent**, 8%+ padding, contact shadow only.
- **Holds**: `isolated-object`, `book-object`, `emblem-seal`.
- **Use**: a keepsake, a ticket, a torn note, a small private memory. A minor beat.

### `artifact-spread` - the document is the page
One primary archival artifact (manuscript, letter, proof, newspaper) replaces
the illustration card and is the principal surface; prose in a disciplined
supporting column or margin.
- **Desktop**: artifact 55-70% width; prose a narrow column beside/below.
- **Mobile**: artifact first at near-full width; prose below.
- **Images**: 1 · aspect `3:2`/`4:5` · background transparent OR simple desk surface. **This type DRAWS its own paper edge - it does NOT get the dissolve filter** (see VISUAL.md edge rule).
- **Holds**: `document-facsimile`, `manuscript-proof`, `book-object`.
- **Use**: rejection, contract, letter, submission, censorship, court record, publication proof. Evidence.

### `diptych` - two states
Two related panels of equal or deliberately contrasting weight, a small
connector between them, one shared title/prose introducing the relationship.
- **Desktop**: two frames side by side, relationship across the centre seam.
- **Mobile**: stacked, sequence preserved, optional vertical connector.
- **Images**: 2 (or 1 image containing both panels - see whole-image ruling) · aspect each `1:1`/`4:5` · background per illustration type.
- **Holds**: `manuscript-proof`, `place-portrait`, `editorial-portrait`, `book-object`, `symbolic-still-life`.
- **Use**: genuine before/after - rejected then rewritten, flop then cult, private then public.

### `strip` - the sequence
A short wide band of 5-12 repeated modular units in a horizontal sequence,
readable left to right; title/prose above.
- **Desktop**: strip spans the content width, most units visible.
- **Mobile**: unit size preserved, strip scrolls sideways beyond the viewport, next unit partially cropped to signal scroll. Never shrink all units to illegibility.
- **Images**: 1 wide strip (or N unit images - whole-image ruling) · aspect wide, e.g. `3:1`/`4:1` · background transparent or paper.
- **Holds**: `serial-contact-sheet`, `process-diagram`.
- **Use**: serialisation, weekly instalments, drafts, submissions, production stages, accumulated incidents.

### `marginalia` - the footnote
A predominantly textual entry with a tiny transparent vignette tucked in the
outer margin (8-15%), near the gutter/rail.
- **Desktop**: object outside or partly outside the text column, may overlap the rail/date.
- **Mobile**: beside the date or title, small scale kept; never promoted to a centred illustration.
- **Images**: 1 · aspect `1:1` · background **transparent**, tiny.
- **Holds**: `isolated-object`, `emblem-seal`.
- **Use**: minor honours, brief appearances, side projects, small contextual details.

### `medallion` - the keepsake (the one round shape)
A circular or oval vignette with a restrained physical frame (rim, seal edge,
mount), spacious around it so the round form interrupts the rectangular rhythm.
- **Desktop**: 20-35% of the width, centred above prose or offset beside the title, may align to the timeline node.
- **Mobile**: centred or slightly offset; never enlarged to fill the screen.
- **Images**: 1 · aspect `1:1` · background transparent; art composed for a circular crop (subject centred, safe margin).
- **Holds**: `editorial-portrait`, `emblem-seal`, `portrait-of-absence`, `book-object`.
- **Use**: honours, memorials, membership, recognition, legacy, symbolic remembrance.

### `split-counterpoint` - two simultaneous realities
Two parallel lanes for events in the same period, each labelled
(PRIVATE / PUBLIC, WRITING / RECEPTION), connected by a shared baseline or date.
They **coexist** - one does not become the other (that is `diptych`).
- **Desktop**: two parallel columns, equal or intentionally unequal.
- **Mobile**: lanes stacked, labels prominent, a connector/shared date preserving simultaneity.
- **Images**: 2 (or 1 composed) · aspect each `4:5`/`1:1` · background per type.
- **Holds**: every illustration type EXCEPT the three artifact types (as `beside`).
- **Schema note**: rendering the lane *labels* (PRIVATE / PUBLIC) needs a
  per-lane label field the event schema does not carry yet; add it when a wing
  first uses this organisation.
- **Use**: contradiction - success during hardship, private loss beside public triumph, personal beside historical.

### `layered-stack` - accumulation
Several overlapping physical artifacts (3-7) as a believable stack/desk spread,
one dominant top piece, depth and repeated handling; prose in a separate clear
zone.
- **Desktop**: stack half to two-thirds of the cell, pieces may extend past the image area.
- **Mobile**: one large visual group, overlap and depth kept, never a carousel.
- **Images**: 1 · aspect `4:3`/`1:1` · background transparent preferred.
- **Holds**: `archive-stack`, `manuscript-proof`, `press-media-collage`.
- **Use**: research, repeated rejection, multiple editions, correspondence, years of revision. (Quantity - versus `artifact-spread`'s single document.)

### `mosaic` - public noise
4-9 unequal fragments in one irregular editorial field, one dominant, deliberate
hierarchy, modest overlap, enough negative space to avoid clutter; title/prose
outside the dense area.
- **Desktop**: broad irregular field beside or beneath the text.
- **Mobile**: the collage stays one composed image; fragments are not split into cards.
- **Images**: 1 · aspect `3:2`/`4:3` · background transparent edges or paper field.
- **Holds**: `press-media-collage`, `symbolic-still-life`.
- **Use**: sudden fame, controversy, press response, award season, adaptations, many voices at once.

### `interlude` - the pause
A deliberately sparse entry with far more empty space than its neighbours: one
date, one short line, an optional faint trace; the rail may pause, fade or go
dotted across the gap. The emptiness is the device.
- **Desktop**: tall section, restrained content off-centre.
- **Mobile**: vertical emptiness kept; do not collapse the pause away.
- **Images**: 0 or 1 · aspect `1:1`/`4:3` · background transparent, barely-present subject.
- **Holds**: `portrait-of-absence`, `atmospheric-motif-field`, or none.
- **Use**: grief, disappearance, creative silence, unknown years, illness, missing records.

### `passage` - compressed time
A shallow full-width band bridging two larger entries, compressing an extended
period into one transition; short prose (1-3 sentences), a date **range**.
- **Desktop**: full-width band, progression left to right.
- **Mobile**: motifs stacked or a cropped continuous band; not shrunk to tiny.
- **Images**: 1 wide · aspect `16:9`/`3:1` · background opaque or transparent.
- **Holds**: `serial-contact-sheet`, `journey-transit`, `process-diagram`, `atmospheric-motif-field`.
- **Use**: teaching years, ongoing work, research periods, slow recovery, years that matter collectively not individually.

### `epigraph` - the author's own words
A quotation set as the illustration. The only organisation with **no artwork at
all**: the author's own sentence is given the space and the weight a picture
would have had, with its attribution beneath.
- **Desktop**: centred on a narrow measure, large display type, generous air above and below; **no card** - no border, no surface fill, no padding box. It is a hole in the run of cells, and that is the whole device.
- **Mobile**: the same break, type stepped down one size; never boxed back into a card to reclaim vertical space, which would turn it into just another entry.
- **Images**: **0** · no illustration type, no asset, no prompt, no issue.
- **Holds**: none. The quotation is the illustration.
- **Use**: a line from the work, a sentence from an interview, an epigraph the author chose for a book, a stated intention or a refusal. One that earns its size - not a convenient pull-quote from the prose we already wrote.

Extra fields, this organisation only:

```yaml
organisation: epigraph
quote: "..."          # REQUIRED - the words, verbatim
title: "..."          # the attribution: the work, the interview, the occasion
description: "..."    # optional one-line gloss, shown small beneath
images_required: 0
sources: [...]        # REQUIRED - where the quotation comes from
```

**A quotation is a fact, and it is the easiest fact in this repo to invent.**
Everywhere else a fabrication would be an invented detail in a drawing; here it
would be words put in a living person's mouth, in their own voice, under their
own name. So `quote` is verbatim or it does not ship: never paraphrased, never
tidied, never reconstructed from memory of what an author "says a lot", never
translated by us when a published translation exists (use it and credit the
translator). It carries `sources` like any other claim, and the validator
requires them. If the exact wording cannot be sourced, the moment is not an
`epigraph` - write it as prose in a `beside` and say who reported it.

### `chapter-gate` - the era opening
A large transitional section introducing a new era (this is the era-plate slot,
not an event). Eyebrow, large era title, date range, a thematic line, a short
summary, one atmospheric illustration summarising the era; a strong visual reset.
- **Desktop**: title/summary one side, broad atmospheric art the other, generous padding.
- **Mobile**: era title, then illustration below, ceremonial spacing.
- **Images**: 1 · aspect `16:9`/`3:2` · background transparent (bleeds off the page; app applies its plate mask).
- **Holds**: `atmospheric-motif-field`, `symbolic-still-life`, `establishing-landscape`.
- **Use**: the opening of each major creative or biographical phase. One per era.

## Modifiers

Applied to a compatible organisation; they change authoring, not the content
model.

- **`breakout`** - one isolated foreground element crosses beyond the artwork
  boundary (the card edge, the row divider, the rail), on transparency, clean
  silhouette. Never over body text. *Compatible: `beside`, `diptych`,
  `artifact-spread`, `layered-stack`, `medallion`.*
- **`pull-focus`** - a magnified detail inset (circular/torn/lens) connected to a
  point in the primary art by a hairline, revealing something too small to read.
  *Compatible: `artifact-spread`, `beside`, `diptych`, `layered-stack`, `mosaic`.*
- **`fold-reveal`** - an upper surface partially conceals a lower one (lifted
  photo, folded corner, censor strip), the concealed layer visible enough to
  read the relationship. *Compatible: `artifact-spread`, `layered-stack`,
  `diptych`, `immersion`.*
- **`anchor-with-satellites`** - one dominant anchor with 3-6 subordinate
  vignettes around it, connected by thin lines/orbit, hand-composed not
  corporate. *Compatible: `beside`, `immersion`, `chapter-gate`, `mosaic`.*
- **`branch`** - the rail visibly divides into labelled paths (pseudonyms,
  parallel careers, divergent adaptations), curved not flowchart. *Compatible:
  `split-counterpoint`, and the rail itself.* App-level; the rail component owns it.

## Compatibility

The validator enforces two things: `modifier` must be listed as compatible with
its `organisation` (above), and `illustration_type` must be in the
organisation's **Holds** list (above). An illegal pairing (a `map-route` in a
`medallion`, a `branch` on a `floating-object`) is a content error, not a
rendering surprise.

`epigraph` holds nothing and takes no modifier: it has no artwork for either to
apply to, so an `illustration_type` or a `modifier` on one is an error rather
than a harmless extra field. It is also the only organisation with required
fields of its own (`quote`, `sources`), which the validator checks in the same
pass.

## The rotation budget: rhythm is authored, not random

Sixteen organisations used freely is drift again; two used repeatedly is the
monotony we are fixing. So a wing's organisations are **assigned deliberately
down the timeline**, the same discipline as the composition rotation
(`art_rotation.py`), now on the organisation axis too:

- **`beside` is the workhorse** and is exempt from the general cap: it may be
  the plurality, targeting **around half** of a wing's events (a soft ~60%
  ceiling, not three-quarters). **Every OTHER organisation is capped at ~40%.**
  `art_rotation.py` encodes exactly this: beside its own ceiling, all others at
  the 40% cap.
- **`immersion` is capped at 1-2 per wing** (the biggest ruptures only). Same
  for `chapter-gate` (one per era) and `interlude` (a real silence, not a
  convenience).
- **`epigraph` is capped at 2-3 per wing.** It costs nothing to produce, which
  is exactly why it needs a cap: an unlimited free organisation would get used
  as filler wherever a good line exists, and a page of quotations is its own
  kind of monotony. It also loses its force by repetition - the beat works
  because the reader has been looking at pictures.
- **No two consecutive events share an organisation.** A vista then a beside
  then an artifact-spread reads as rhythm; three besides read as a table.
- **The shape should track the life**: open a period with `full-bleed-vista` or
  `chapter-gate`, carry the dead years with `passage` or `interlude`, stop at a
  death with `immersion`, file the evidence with `artifact-spread`. The
  organisation is a narrative instrument, not decoration.

`art_rotation.py` scores both axes (organisation and illustration composition)
and `--check` fails a wing that breaks the caps or repeats a neighbour. The
prompt writer assigns the whole wing in one pass so the rhythm can actually be
composed (see `.claude/commands/asset-prompt.md`).

### The contour: caps say how often, not in what order

Every cap above is a frequency, and a wing can clear all of them and still be
badly paced - six loud cells running, then a flat stretch. Exhibition designers
name this outright: alternate higher-intensity spaces with lower-intensity
ones, or the visitor never gets to process anything. So `art_rotation.py` also
grades each organisation loud / mid / quiet (`immersion`, `full-bleed-vista`,
`chapter-gate` and `mosaic` are loud; `passage`, `interlude`, `marginalia` and
`epigraph` are quiet) and checks the SEQUENCE:

- **No two loud cells touching.** A rupture earns its weight from the quiet
  around it; back to back they cancel.
- **No plateau**: five or more consecutive cells at the same intensity, however
  varied the organisations inside it are.
- **No two loud cells in one screenful.** The caps are counted over a whole
  wing, so two vistas three events apart look far apart in the arithmetic and
  land together on the page. Print composes against the spread - the unit the
  reader takes in at once - and the web's spread is the viewport. The script
  carries a measured table of roughly how much of a phone viewport each
  organisation occupies, and slides a one-viewport window down the wing.

The report prints the wing's contour as one line (`#` loud, `=` mid, `.`
quiet), which is the fastest way to see the shape of a life at a glance. A wing
that has not been cut onto the grammar yet prints as `=============`, thirteen
identical mid cells, and that string is the original monotony complaint stated
exactly.

## Transitions: the gutter is part of the grammar

Sixteen organisations describe the CELLS. Nothing above describes what happens
**between** two of them, and in every sequential medium that is where the
reading actually happens: comics grammar puts elapsed time not in the panel but
in the gutter, and the reader crossing that space is what supplies the passage
of time. Our only sequencing rule until now was negative - "no two consecutive
events share an organisation" - which says avoid a repeat, never *compose a
transition*.

Three transitions, and **all three are DERIVED from the dates the content
already carries**. There is no `transition:` field and there should not be one:
a curator writing "this follows closely from the last one" next to two dates
that say otherwise is a fact that can drift, and the dates cannot.

| Between | Reads as | What the app does |
|---|---|---|
| Same year | facets of one moment | already grouped: one stratum, one year heading, one ghosted numeral |
| 1-3 years | an ordinary cut | the standard gap between strata |
| **4+ years** | **a leap, a silence** | a **gutter**: extra space scaled to the span, and the span said out loud ("29 anos depois") |

The threshold is 4 because a working writer publishes most years, so three
quiet years is ordinary and four begins to be something. The gutter's height
steps up at 7 and again at 15, so a three-decade silence looks like one.

**Saying the span is the load-bearing half**, not the empty space. A big gap on
its own is ambiguous - it reads as a layout decision rather than as a silence -
and a reader has no way to tell four years from forty without subtracting two
ghosted numerals themselves.

What this means for composing a wing: an `interlude` is no longer the only way
to show a silence, and it should not be spent on one the dates already state.
Reach for `interlude` when the silence is **the event** (grief, illness,
a disappearance, a refusal to write) and there is something to say about it.
The gutter covers the case where nothing was recorded at all, which is most of
them, and it costs no entry and no artwork.

## How this reaches the app

The app renders a dispatcher: one component per `organisation`, chosen by the
event's field, each responsive (desktop + mobile per the specs above). The old
single `RiverEventCard` becomes `beside`, one of sixteen. The event carries
`organisation`, `illustration_type` (for alt/analytics only - the app renders
the filed image), `images_required` (how many image slots to lay out), and any
`modifier`. Aspect and background come from the filed asset, never assumed.
