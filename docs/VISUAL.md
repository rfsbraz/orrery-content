# The Orrery visual system

Every generated image should read as part of one editorial publication. The
house style below is fixed; each wing varies only through its `theme.art`
block. If an asset looks like it came from a different illustration system,
it is wrong even when it is beautiful.

## 1. House style

- refined hand-drawn linework, lightly imperfect, dip-pen rather than ruled
- simplified vector-like colour fields, few of them
- restrained ink shading, sparing cross-hatching
- warm, lightly textured background; visible paper fibre
- strong negative space, uncrowded
- literary rather than technological
- **the orrery itself, once in every sketch** (see §1a)
- no photorealism, no glossy 3D, no game concept art
- **no typography inside the image**, with one narrow exception for era plates
  (§4b): the app sets its own type over these, and invented lettering is the
  fastest way to make an illustration look machine-made

## 1a. The orrery motif: found in the scene, not laid over it

Every sketch in the catalogue carries the same mark - **concentric orbital
rings with small nodes riding on them** - and that shared mark is what makes a
Pratchett sketch and a Mãe sketch read as one publication.

It is **not** a watermark and not a fixed overlay in the sky. Put it on
something the scene would plausibly contain, so it looks found rather than
applied:

- engraved on the face of a compass, a dial, a pocket watch, an astrolabe
- printed as the cancellation stamp on an envelope, a ticket, a library card
- woven into a rug, a mat, a tablecloth, a shawl border, a tiled floor
- pressed into a coin, a medal, a seal, a bookplate, a bottle cap
- the rings of a cut log, ripples spreading on water, a spiral of birds
- worked into a gate, a window grille, a bannister, a wheel

Choosing the carrier is part of drawing the scene: pick what that subject
already has. A writing desk offers a paperweight; a fishing village offers
net floats and ripples; a hospital corridor offers a wall clock. **Vary it
between assets in the same wing** - the same compass in six sketches becomes a
logo, which is the opposite of the point.

Faint arcs across an empty sky are still allowed, but as one option among many
rather than the default, and only where the composition has real empty sky.

### Write the motif as its own paragraph, and keep it legible

The single most common failure is a **tangled** motif: the rings get drawn on
top of whatever markings the carrier already had, and the result is a busy
smudge that reads as neither. A compass already has a rose and degree marks; a
clock already has numerals; a coin already has a device.

So, in the prompt:

- Give the motif **its own short paragraph**, never a clause tacked onto the
  end of a sentence about something else. It is a distinct instruction.
- Say explicitly that it **replaces** the carrier's usual markings rather than
  being added over them: *"in place of an ordinary compass rose"*, *"in place
  of the usual numerals"*.
- Describe the shape concretely and simply: **two or three plain concentric
  ellipses with three or four small solid dots sitting on them**, and nothing
  else inside that area. Name the clear space: *"no other engraving, degree
  marks or lettering on that face"*.
- Say how big it should read and how much clear space it needs.

Two constraints hold whichever carrier is used:

- **It never competes with the subject.** Same ink, no heavier than its
  surroundings. If a reader notices the rings before the scene, it is too
  strong.
- **It is never the subject.** No sketch is *about* an orrery, and it is never
  a floating diagram with nothing holding it.

## 2. The model

**Target: `gpt-image-1`.** Not DALL-E 3, which cannot take reference images and
whose sizes do not include a portrait ratio we want.

| Capability | Value |
|---|---|
| Sizes | `1024x1024`, `1024x1536` (portrait), `1536x1024` (landscape), `auto` |
| Reference images | **Supported** - pass via the image-edit endpoint |
| Transparent background | Supported (`background: transparent`, png or webp) |
| Quality | `low` / `medium` / `high` |

There is no 4:5 size. A portrait asset uses `1024x1536` (2:3) and is cropped by
the app, not by the prompt.

## 3. Real people are photographed, never generated

**Do not generate a likeness of a real author.** Authors carry a licensed
photograph in `images.portrait` with its credit, sourced by the
`visual-metadata` stage. An illustrated face standing in for a sourced one
replaces a fact with a plausible invention, which is the failure this whole
repo is built to prevent - and OpenAI's policy refuses public-figure
likenesses in any case.

This constrains life-event sketches in particular: **a life event is drawn as
its place, its weather, its objects or its consequence, never as a portrait of
the person it happened to.** "Wins a prize" is not a man holding a trophy; it
is the room, the light, the book on a table.

The same care applies to the recently dead and the bereaved: draw the absence,
not the person.

The worked example is the 2023 double bereavement on the Mãe wing: a vase of
dried flowers, a lit tea candle, an open book with a pressed flower, letters in
a hand nobody can read - and, in a standing frame, a figure **turned away**,
drawn as a drawing-of-a-photograph rather than a portrait. The frame says a
person is being mourned; the turned head means we have not invented their face.
That is the shape to reach for whenever a real person is the subject of a
moment: the objects that person left, and their likeness withheld.

## 4. Asset specs

| Asset | Size | Background | References | Renders in |
|---|---|---|---|---|
| `era-plate` | `1536x1024` | opaque, wing paper tone | no | the right half of the era plate, bleeding off the page edge; the title and prose hold the left (see §4b) |
| `life-event` | `1024x1024` | **transparent** | no | the illustrated event card in `river.tsx`, laid beside the prose |
| `franchise-event` | `1024x1024` | **transparent** | no | the illustrated event card in `river.tsx` |
| `world-event` | `1024x1024` | **transparent** | no | every wing that carries the event, **tinted with that wing's `accent`** |
| `work-cover` | - | - | - | not generated: covers are licensed or absent (see `visual-metadata`) |
| `author-portrait` | - | - | - | not generated: see §3 |

World events are shared, so they are drawn once in the neutral house style with
no wing-specific motifs, on transparency, and coloured per wing in CSS. A
world-event sketch that only suits one author is a bug.

## 4-impact. A high-impact event is a rupture, and gets the whole width

The river renders `impact: high` events as **ruptures**: full-bleed bands in the
wing's ink colour, inverted out of the page. On a dark wing that band is warm
paper, and a transparent sketch lands on it with no edge whatsoever - the
drawing simply sits on the page. This is the strongest argument for
transparency in the whole system: one asset reads correctly on a dark card and
on an inverted paper band, and a baked background would ruin one of them.

Compose a rupture sketch differently from a seam sketch:

- **Wide and centred, under the prose**, not beside it. The app gives it the
  full column.
- **Slower and quieter.** This is the moment the reader is meant to stop at, so
  it earns stillness: fewer objects, more air between them, softer shading.
- **The register carries it**, not incident. A death is a table after the fact -
  dried flowers, a lit candle, an open book, letters - lit low and warm.

## 4a. Breaking monotony in a sequence

A wing's life events are read one after another down a single column, so a set
of individually good sketches can still fail: six wide landscapes with a warm
wash and a compass become wallpaper by the third. **Each sketch is drawn
against its neighbours, not only against its own brief.** Before writing a
prompt, look at what the two events either side of it already got, and vary at
least two of these four:

- **Composition type.** Rotate deliberately between: a wide landscape or vista;
  a cluttered working still-life seen close (a desk, a press, a kitchen table);
  a single object given the whole frame; and a quiet intimate arrangement (a
  vase, a candle, a photograph face-down). The 1971 birth is a vista, so the
  1974 that follows it should not be.
- **Distance.** Far, middle, near. A landscape then a tabletop then an object
  in the hand reads as a rhythm; three middle distances read as one picture.
- **Tonal cast.** Stay inside the wing's palette but let the temperature carry
  the register: warmer and drier for a beginning, cooler and greyer for
  hardship, a mauve or ashen cast for grief. This is the cheapest way to make a
  sequence feel written rather than generated - and it must never break into a
  colour the wing does not own.
- **The orrery motif's carrier** (§1a). Six compasses is a logo.

The app alternates which side of the card the illustration sits on as you go
down the page, so **do not build the composition around a side**: keep the
subject central enough to read mirrored.

## 4b. The era plate

An era plate is the largest asset in the catalogue and the only one that gets a
half-page. It is not a background behind text: the prose holds the left side,
the illustration owns the right and bleeds off the edge of the page.

Compose it as **a place of work with a world behind it** - the near ground
carries the era's objects in a dense, warm still-life (the books it produced,
the tools it was made with, a lamp, a cup, the papers), and behind them the
horizon opens onto the landscape or city that era belongs to, drawn lighter and
looser so it recedes. Depth is what makes it a plate rather than a picture: near
clutter, middle distance, far vista.

Two era-specific liberties, both earned by the size:

- **The orrery motif can be large here** - full arcs sweeping the sky with
  planets on them - because there is room for it to be atmosphere rather than a
  detail. It still sits behind everything.
- **Real names may appear on objects** - a book spine, a masthead, a shop sign -
  where the record actually contains that name (a press the author founded, a
  magazine they edited). Keep it to two or three short words, and **check the
  spelling in the returned image**: a misspelt real imprint is worse than no
  lettering at all, and this is the one place §1's "no typography" rule bends.

## 5. Assembling a prompt

In order, always:

1. **The house style** (§1), stated plainly.
2. **The wing's `theme.art`** from `theme.yaml`: motifs, atmosphere,
   lineCharacter, backgroundTexture, accentUse. Quote it, do not paraphrase it
   away - it is the only thing making two assets belong to the same wing.
3. **The subject**, derived from the entity's own `title` and `description`.
   Draw what the record says happened; do not invent incident.
3a. **The orrery motif's carrier for this scene** (§1a) - name the specific
   object that carries the rings here, and vary it from the wing's other
   assets.
4. **The composition**, from the asset spec (§4).
5. **The shared negative prompt** (§6), plus the wing's own `art.avoid`.
6. **The technical block** (§5b), verbatim. Never leave the output format to be
   inferred from the composition.

For a **world event**, skip step 2 entirely and say "neutral house style, no
author-specific motifs, transparent background".

## 5b. The technical block

Every prompt ends with an explicit statement of what file is wanted. Leaving it
implicit is how a sketch comes back opaque, or square when it needed to be wide,
and each of those costs a re-roll.

**Do not ask for a transparent background.** It was the obvious approach and it
does not survive: the model produces real alpha, and the download flattens it
onto the viewer's checkerboard - a machine-regular grid of two near-white greys.
Rebuilding alpha from that grid fails, because the checkerboard shares its grey
with any drawn sky, so the flood eats holes in the artwork and leaves the seams
behind as a faint lattice.

**Ask for a solid chroma background instead, and key it out afterwards.**

- **Flat, fully saturated magenta, `#FF00FF`**, filling every part of the frame
  the artwork does not occupy. Magenta because nothing in this catalogue's
  palette is near it - the wings are warm greys, umbers, parchment and
  terracotta, all in the red-orange hues - so the key can be global and cannot
  eat the picture. Green would collide with foliage.
- Say **flat**: no gradient, no texture, no shading, no vignette in the
  background, and no magenta anywhere inside the artwork itself.
- **Say, in the same breath, that the artwork must not reach the frame.** A
  chroma instruction reads as "put the picture on a coloured card", and the
  model will happily fill the canvas corner to corner and give you a neat
  rectangle - which is exactly the ragged dissolve you were trying to keep.
  Spell it out: *"the magenta must be visible along all four edges of the
  frame; the artwork must not touch the border at any point; its outline is
  irregular and hand-torn, the ink and wash breaking up and stopping unevenly,
  never a straight edge and never a rectangle."* Naming a rough margin helps -
  *"leave roughly a tenth of the frame as magenta around the artwork"*.
- Still state **exact pixel dimensions** from §4 (`1024x1024` for an event,
  `1536x1024` for an era plate) - not "square", not an aspect ratio.
- Still ban borders, frames, mattes and drop shadows onto the background.

Then file it with:

    python scripts/prepare_asset.py <image.png> <slug> <entity-id> --chroma

which keys the magenta to real alpha with a soft edge, despills the fringe so
edges do not glow pink on a dark page, trims the empty margins, converts to
webp under the size cap and prints the YAML to paste.

## 5a. Choosing the presentation

How a sketch meets the page is a decision per item, not a house rule. The job
is always the same - **either blend the art into the page or deliberately pop it
off the page** - but which reads better depends on the subject, the surface it
lands on, and what the neighbouring assets did.

Pick one and say which you picked, and why, in the prompt's brief:

- **Torn sheet.** A drawn sheet of aged paper with deckled, irregular edges,
  fibres showing where it tore. Pops off the page; suits anything documentary
  or archival - a place remembered, a manuscript, a letter, a record.
- **Dissolving panel.** The drawing fills its frame and thins out at the edges,
  ink and wash fading to nothing rather than stopping at a line. Blends into
  the page; suits vistas, cityscapes, weather, anything atmospheric.
- **Objects on an implied surface.** No paper and no panel at all: a still-life
  on a suggested tabletop with soft shadows under the objects, everything else
  transparent. Blends completely; the natural choice on a rupture band, where
  the band itself is already warm paper (see §4-impact).
- **Panel with a break-out.** A dissolving panel plus one element crossing
  outside its edge - a compass, a branch, a spill of papers. Pops, but keeps
  the calm of a panel behind it. Good when a scene needs an anchor in the
  foreground.

Anything else is allowed if it serves the same end. What is **not** negotiable,
whichever you choose:

- **Nothing may assume what colour is behind it.** Transparent background
  always, no vignette, no painted-in page colour, no rounded rectangle, no
  frame, no drop shadow onto the background - shadows fall onto the paper or
  the implied surface, never onto the void. This is what lets one asset work on
  a dark card and on an inverted paper band; it is the reason the whole system
  holds together, and it is the rule most likely to be broken by accident.
- **Vary it down a sequence** along with everything else in §4a. Four torn
  sheets in a row is the same monotony as four vistas.

**World events are the exception and have no latitude.** A shared sketch is
recoloured per wing by painting the wing's accent through its alpha, so it must
be **line and texture only, on transparency** - no paper, no panel, no wash, no
filled shapes. Anything with a solid fill becomes a solid accent-coloured blob.

An earlier version of this section prescribed the torn sheet for everything, and
said the app owned edges before that. Both were premature: the treatment is an
editorial judgement about a specific subject, and the only durable rule is the
transparency invariant above.

## 6. Shared negative prompt

Append to every prompt:

> Avoid: photorealism; cinematic concept art; generic fantasy art; anime;
> children's-book cartoon styling; glossy 3D rendering; neon colours; heavy
> gradients; thick black outlines; crowded compositions; any text, lettering,
> captions, signatures or watermarks; publisher logos; reproductions of real
> book covers; UI elements; decorative elements covering faces; excessive stars
> and planets; literal outer-space imagery unrelated to the subject; vignettes;
> borders, frames or rounded rectangles; any painted-in background colour; drop
> shadows cast onto the background rather than onto the paper or surface within
> the artwork.

Plus the wing's `art.avoid`, which names that author's specific cliche.

## 7. Workflow for a wing

1. Settle `theme.art` in `theme.yaml`. Nothing else may be generated first.
2. Era plates, largest surfaces first - they set the palette in practice.
3. Life events, then franchise events.
4. Shared world events last, in house style.
5. Put every result side by side before accepting any of it. Reject anything
   that looks like a different illustration system, however good it is alone.
6. File it with `python scripts/prepare_asset.py <image.png> <slug> <entity-id>`,
   which refuses an image that has lost its alpha, trims the empty margins,
   converts to webp under the size cap and prints the YAML to paste. **Keep the
   original PNG from the model** - a screenshot or a re-export flattens the
   transparency onto a checkerboard, and what arrives looks fine until it is on
   a dark page.

`python scripts/asset_audit.py <slug>` reports what exists and what is next in
exactly this order; `/asset-prompt` writes the prompt for one asset.

## 8. Colour

The interface palette stays stable across the catalogue: deep navy, warm cream,
off-white, muted blue-grey, charcoal text. A wing's own palette applies to
sketch backgrounds, era plates, hero areas, dividers and progress accents -
never to navigation, typography, spacing or main surfaces.

Each wing has one dominant accent (`theme.palette.accent`), used in artwork on
**one element per image, never as a fill**.
