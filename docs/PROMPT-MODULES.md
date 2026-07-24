# Illustration authoring modules

The per-`illustration_type` briefs that `VISUAL.md` §3b only indexes. This is
what the prompt writer pulls to author a given asset: *what to draw and how*,
one module per type. The layout (how the cell arranges image and text) is the
`organisation` axis, in `LAYOUT.md`, and is not repeated here.

Everything here sits UNDER the house rules that are stated once and never
duplicated:

- **House style** (`VISUAL.md` §1) and the wing's own `theme.art` - quoted, not
  paraphrased. Every module inherits these; a module only adds subject-specific
  authoring.
- **The orrery motif** (`VISUAL.md` §1a) - its own quiet paragraph in every
  scene sketch, sky by default. Object/artifact/emblem types that have no scene
  carry it on the object per §1a, or omit it when there is genuinely nowhere for
  it to sit (a bare `isolated-object`, an `emblem-seal`).
- **The technical block** (`VISUAL.md` §5b) - verbatim, ending every prompt:
  exact pixel size, magenta `#FF00FF` chroma for keyed types, the glow/gradient
  ban.
- **The shared negative prompt** (`VISUAL.md` §6) plus the wing's `art.avoid`.
- **Background and edge follow the type**, per the §3b table and the edge rule:
  transparent object/scene types are chroma-keyed and dissolved; the three
  artifact types draw their own edge and file `--no-dissolve`; opaque scene
  types file `--opaque` (no chroma, no dissolve).

## The rule the new types must not break: no invented likeness of a real person

`VISUAL.md` §3 stands: **a real, named person is never drawn as a likeness.**
Author portraits are photographed. This constrains three of the types below -
`editorial-portrait`, `relationship-tableau`, `portrait-of-absence` - which the
grammar allows but which must, for any real named individual, fall back to the
withheld-face treatment: the person shown by their place, their objects, their
turned back, a face-down photograph, never an invented face. A drawn
`editorial-portrait` is only for a figure who is *not* a real identifiable
person (an anonymous archetype, a pictogram). If a moment seems to need a real
person's face, it becomes `portrait-of-absence`. This is not negotiable and is
the one place the new grammar bends to an older, load-bearing rule.

---

## The 25 modules

Each: what the subject is, how to compose it, what to avoid beyond §6. Aspect
and background are in the §3b table; the note here only flags the non-obvious.

### `establishing-landscape`
The environment is the subject; no central figure. Clear foreground, middle
ground, distance; one recognisable geographic feature; horizon on the upper or
lower third; restrained human traces (a road, poles, distant houses); broad
quiet, low-to-medium contrast. Communicate what living there *felt* like, not a
documentary record. Opaque, wide.

### `place-portrait`
One meaningful structure or frontage as the anchor, slightly oblique not frontal,
simplified architecture, minimal or no people, signs of period and use, one
dominant silhouette with air around it. Observed and remembered, not an
architectural render. No readable signage unless the exact words are supplied.

### `domestic-interior`
A private room implying its people through objects, not a staged scene. At most
five important elements (chair, table, window, lamp, bed, a personal object).
Middle distance, believable depth, one focal source, controlled shadow,
lived-in but uncluttered, empty space that carries feeling. People absent unless
essential.

### `workplace-workshop`
A room defined by process and discipline: the activity explained by arrangement,
not by active figures. One strong geometric arrangement, repeated furniture or
tools, evidence people just left or are about to arrive. No busy crowd, no
staged productivity. The room's order reveals the method.

### `aftermath-scene`
What remains after the action, never the climax. Displaced or abandoned objects
(an overturned chair, an open envelope, an abandoned microphone, a marked desk).
Middle distance, few objects, controlled stillness, no violence shown, no
emotional close-up. The viewer reconstructs the event from the evidence.

### `public-event-tableau`
A public setting where scale or reception matters. One focal speaker/stage/
podium; grouped figures rendered economically as repeated silhouettes, faces
secondary; architectural framing establishes the venue. No celebrity-photo
composition, no spotlights, no individually rendered crowd faces.

### `journey-transit`
Movement between places, biographical and reflective not action-film. One
transport or route anchor (a train, a bicycle, a road, a platform, a suitcase).
Movement conveyed by converging lines, receding landscape, a directional gesture,
arrival or departure architecture. Opaque scene, or a transparent isolated
vehicle when the organisation wants an object.

### `historical-context-tableau`
An external event changing the author's conditions, shown through ONE concrete
symbolic situation, not a full reconstruction (a closed newspaper office, a
printing press, a ration line, a changed border). Plausible period objects,
minimal figures. No propaganda composition, no graphic violence, no flag design,
no attempt to depict the whole event. This is the house-style world-event
register; on a shared world event, drop the wing's motifs (VISUAL.md §5a).

### `editorial-portrait`
**Real named people: do not draw a likeness (see the rule above) - use
`portrait-of-absence` instead.** This type as a drawn face is only for an
anonymous archetype or a pictogram figure that stands for a role, not a person.
When used that way: chest-up or head-and-shoulders, eye level, generous negative
space, simplified clothing, no props unless essential, the wing's palette
without covering the figure.

### `relationship-tableau`
Two+ people shown through their relationship, not a posed group and - for real
named people - not through their faces. Use the relation itself: a shared table,
an exchanged letter, facing chairs, a manuscript passed between hands, two
figures walking, parallel workspaces, one figure observing another. One clear
relational gesture, restrained body language, minimal setting. Faces only for
anonymous figures.

### `portrait-of-absence`
A person shown by what they left, never directly. One central absence marker (an
empty chair, an unmade side of a bed, a coat on a hook, a face-down photograph,
an extinguished lamp, an unfinished letter, a paired object with one missing).
Sparse; the meaning emerges from the missing presence. The worked example is the
Mãe 2023 bereavement (VISUAL.md §3). This is the correct type for the death of,
or separation from, any real named person.

### `isolated-object`
One item, no scene, complete silhouette. Transparent, no frame, no environment,
no unrelated props, controlled three-quarter or top-down view, clear material and
period, readable small, minimal internal detail, contact shadow only, 8%+
transparent padding. The motif may be omitted (nowhere to sit). Keyed +
dissolved.

### `symbolic-still-life`
Two to five objects communicating a moment metaphorically, one dominant, the
rest arranged by overlap, alignment, scale contrast on a shared surface with
controlled negative space. Each object must earn its place. Avoid the generic
literary desk (flowers, candles, books, pens) unless specifically meaningful -
this is the §4c still-life-clutter trap; name four or five objects, not ten.

### `book-object`
A volume as a physical artifact, never a cover recreation. Plain cloth/paper/
board binding, a subtle abstract emblem, initials only if permitted, a visible
page block, wear appropriate to its history. It may be closed, part-open,
face-down, stacked, missing from a row, or fading from the frame. Transparent or
a neutral surface.

### `document-facsimile`
One letter, form, or official page as evidence. Period paper, believable folds
and wear, short marks/signatures/stamps/redactions, a clear block hierarchy, no
paragraphs of legible invented prose (abstract lines; only supplied short
phrases). Viewed top-down, angled, part-folded, or in an envelope. **Artifact
type: draws its own edge, files `--no-dissolve`.**

### `manuscript-proof`
Working pages showing revision: typed or handwritten lines, corrections,
crossings-out, arrows, margin notes, editor marks, one clear focal intervention
(a heavy deletion, a circled passage, a rejection stamp, an exact page count).
Not every page full of legible prose. **Artifact type: own edge,
`--no-dissolve`.**

### `archive-stack`
Documents implying quantity and accumulated history: three to seven layers
(folders, letters, photographs, proofs, clippings), one dominant top artifact,
visible lower layers, credible paper thickness, signs of handling, controlled
overlap, one cohesive physical group (no floating collage). **Artifact type: own
edge, `--no-dissolve`.** (Quantity - versus `document-facsimile`'s single page.)

### `press-media-collage`
Dense but organised public response: four to nine fragments (a newspaper front, a
review column, a ticket, a microphone, an audience sketch, an invitation), one
dominant, several supporting, varied paper sizes, slight overlap, limited
readable text, one period. No fabricated full headlines unless supplied, no
modern mood-board look.

### `map-route`
A geographic or conceptual journey as a hand-drawn editorial map: simplified land
or city forms, one clearly differentiated route, two to six stops, restrained
landmarks, one direction of movement, period map language. No modern navigation
UI, no satellite imagery, no dense road network, no software pins, no exactitude
that does not serve the story.

### `process-diagram`
How something worked, in objects not boxes: three to eight stages, arrows or
threads or spatial progression, one start and end, an optional cutaway
(manuscript to printed book, story to screenplay to film, an editorial revision
cycle). Not a corporate flowchart, not software architecture, not an infographic
template.

### `network-constellation`
Relationships around a central subject: one dominant central vignette, three to
seven secondary nodes (small objects, books, places, symbols - not real faces),
connected by threads, hand-drawn lines, orbit-like paths, with irregular spacing
and narrative hierarchy. Not a symmetrical corporate network diagram. Pairs
naturally with the `anchor-with-satellites` modifier.

### `serial-contact-sheet`
A prepared sequence of small related frames: identical dimensions, shared line
character and scale, one simple state per frame, readable small, meaningful
difference between neighbours (contact prints, index cards, stamped forms,
calendar slips, changing manuscript pages). NOT one panoramic scene divided by
lines. This is the art for the `strip` organisation.

### `emblem-seal`
A compact identity mark for a series, prize, or idea, from one to three motifs:
strong silhouette, limited internal detail, readable at 48-96px, no typography
unless supplied, no existing-logo recreation, no fantasy crest. A circular seal,
a simple badge, a geometric mark, an institutional stamp. Transparent, square.

### `palimpsest-erasure`
An image built from revision and surviving traces: an earlier state partly
visible beneath a later intervention (a rewritten manuscript, a censored article,
a traced-over drawing, a replaced title page). Incomplete removal, ghost marks,
overwritten lines, torn or lifted sections. The earlier layer must stay visible
enough to affect the reading of the later. No digital glitch effect.

### `atmospheric-motif-field`
A low-information tone layer for gates, overlays and quiet backgrounds: a small
vocabulary of repeated faint elements (lines, diagram fragments, paper stains,
distant windows, map contours, photocopy grain), very low contrast, sparse, large
text-safe areas, no dominant subject, no complete scene, no seamless wallpaper
repeat. Supports text and other art rather than attracting attention.

## The assembly template

Every prompt the writer produces follows `VISUAL.md` §5's labelled sections. The
two-axis grammar adds the organisation's art requirement to the composition
block. Skeleton:

```
STYLE:      <house style §1 + the wing's theme.art, verbatim>
SCENE:      <where, as physical material>            [from the illustration module]
SUBJECT:    <what happens; people by role, never a real likeness (§3)>
DETAIL:     <the orrery motif, its own paragraph §1a>
            <composition/distance/tonal cast, chosen against neighbours §4a>
COMPOSITION:
            <the illustration module's framing>
            <the ORGANISATION's art requirement: aspect, the text-safe/quiet
             zone the layout needs, any breakout element, per LAYOUT.md>
            <direction, where the subject has one: into the depth of the frame
             or descending, never up and out of the top edge §4a>
            <leave the artwork off the frame; ~a tenth as margin (keyed types)>
CONSTRAINTS:
            <shared negative §6 + wing art.avoid>
            <the technical block §5b, verbatim: exact size, magenta chroma or
             opaque per the type, the glow/gradient ban>
```

The `COMPOSITION` block is where the two axes meet: the illustration module says
what the picture is, the organisation says what shape it must be and where the
text will sit. A `full-bleed-vista` wants a wide opaque scene with no reserved
text zone (text is a neighbour); an `immersion` wants a 35-45% low-detail quiet
zone for text over the art; a `medallion` wants the subject centred inside a
circular safe area. Pull the organisation's spec from LAYOUT.md and state it.

## Worked example (Palahniuk, 1995 rejection)

```
organisation: artifact-spread
illustration_type: manuscript-proof
modifier: breakout
treatment: [photocopy-grain]
images_required: 1
```

STYLE: cold institutional grey stock, flat even-weight ruling-pen line, photocopy
grain, one antiseptic-teal accent, deadpan fluorescent atmosphere (the Palahniuk
theme.art, verbatim). SUBJECT: a stack of returned manuscript pages, exactly
seven squared pages, a returned envelope, no readable long-form text. DETAIL: the
orrery motif as faint concentric rings in a rubber date-stamp impression, lower
left. COMPOSITION: the manuscript is the surface (artifact-spread, ~65% width,
prose column beside); the returned envelope crosses the lower edge (breakout);
3:2; the artifact draws its own torn/folded edge. CONSTRAINTS: §6 + Palahniuk
art.avoid; technical block, `1024x1024`... wait - 3:2, so state the exact 3:2
pixel size; magenta chroma; no glow. File: `prepare_asset.py in.png
chuck-palahniuk palahniuk-fight-club-origin-1995 --chroma --neutral --type
manuscript-proof` (the `--type` skips the dissolve, since this artifact draws its
own edge).
