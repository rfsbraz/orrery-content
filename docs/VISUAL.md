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

**It is an afterthought, and it should feel like one.** The reader meets the
scene first. Somewhere after that, they notice the rings and think *oh, that's
fun*. That reaction is the whole specification. If the motif is the first thing
seen, or if it needed its own clearing in the composition to be readable, it
has been drawn wrong no matter how well it was drawn.

**The sky is its home.** Faint arcs high in an open sky is the default and the
best version: it sits in the one part of the picture nothing else is using, it
never has to fight a carrier's existing markings, and it stays incidental
without effort. Reach for it first.

**In the sky, draw it enormous and open, never small and closed.** This is the
counterintuitive part and it is the one that keeps going wrong. Asking for a
small mark produces a compact ellipse system in one corner: a discrete object,
a little diagram parked in the air, and the eye goes straight to it. Asking for
a vast one produces something the eye reads as *sky*.

So for any scene with open sky:

- **Shallow arcs spanning the full width of the frame**, running off both edges
  rather than closing. Segments of circles far larger than the picture.
- **Concentric with the horizon**, echoing its curve, as if the rings belonged
  to the earth's own curvature rather than sitting in front of it.
- **No part of it reads as a shape.** If you can point at the motif and trace
  its outline, it is too small and too closed.
- The dots ride **far apart** along the arcs, a few across the whole sky, never
  clustered into a cluster that reads as a diagram.
- Faint enough to pass for high cirrus or the ruled lines of an old chart the
  weather has nearly taken back.

Never a closed ellipse, never an orbit diagram, never a compact device in the
upper corner.

**Vary away from the sky when the scene has none, or when a wing is getting
repetitive** - not as a matter of course. An interior, a close still life or a
night scene may have no sky to use, and then the motif goes on something the
scene already plausibly contains:

- the rings of a cut log, ripples spreading on water, a spiral of birds
- woven into a rug, a mat, a tablecloth, a shawl border, a tiled floor
- worked into a gate, a window grille, a bannister, a cartwheel
- printed as the cancellation stamp on an envelope, a ticket, a library card
- pressed into a coin, a medal, a seal, a bookplate

**Do not default to a small round object.** Compasses, dials, pocket watches,
floats and bottle caps are the obvious carriers and therefore the ones that
turn into a tic: a run of sketches each hiding the rings on a little disc reads
as a game of spot-the-logo. If the scene has sky, use the sky.

**Vary it between assets in the same wing** - the same compass in six sketches
becomes a logo, which is the opposite of the point.

### Write the motif as its own paragraph, and keep it quiet

Give the motif **its own short paragraph**, never a clause tacked onto the end
of a sentence about something else, because a tangled clause is how it gets
missed entirely. But write that paragraph to make it *recede*:

- Describe the shape concretely and simply: **two or three plain concentric
  ellipses with three or four small solid dots sitting on them**, and nothing
  else inside that area.
- **Never say "small".** In the sky it produces a compact diagram in a corner,
  which is the single most persistent failure this section has. Say **vast**,
  **spanning the whole sky**, **running off both edges of the frame**, and say
  it is faint. Size and prominence are opposites here.
- Never say it should be legible, prominent, or given clear space around it.
  Those words turn an afterthought into a centrepiece, and the generator obeys
  them exactly.
- Say it is drawn in the **same ink and no heavier** than its surroundings.

When the carrier is an object rather than sky, one extra failure appears: the
rings get drawn on top of markings the carrier already had, and the result is a
busy smudge reading as neither. A compass already has a rose, a clock has
numerals, a coin has a device. So say the motif **replaces** those markings
rather than joining them: *"in place of the usual numerals"*.

Two constraints hold whichever carrier is used:

- **It never competes with the subject.** If a reader notices the rings before
  the scene, it is too strong.
- **It is never the subject.** No sketch is *about* an orrery, it never gets
  its own careful attention in the prompt, and it is never a floating diagram
  with nothing holding it.

## 1b. Generated art is a placeholder with no seniority

Every sketch in this catalogue is generated, and none of it has tenure. **Human
art always wins.** If someone offers a drawing that fits a moment on a timeline,
it replaces the generated one, and the generated file is deleted rather than
kept as an alternative.

That is a standing rule, not a case-by-case judgement, and it holds even when
the generated image is good and the wing looks settled. The images exist because
188 assets could not be commissioned, not because generation is the preferred
outcome.

In practice:

- A generated asset is never a reason to decline an offered one.
- Human work carries its author's name in `sketchCredit`, and the terms it was
  given under. Generated assets say `Generated for Orrery (gpt-image-1)`, which
  is how you tell them apart at a glance and how you find what is replaceable.
- An offer that does not fit the wing's visual language is a reason to talk
  about the visual language, not an automatic no. The house style serves the
  catalogue; it does not outrank a real artist's work.
- Recommendations count too. If public-domain or openly-licensed art exists that
  suits a moment, that is worth more than anything we can generate, and the
  rights check is a normal part of accepting it.

Anyone offering art should open an issue on this repo. See the README.

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

Shared world-event art lives in `assets/global/`, not under any one wing: it is
catalogue canon, and filing it beside the author who happened to prompt it
would imply otherwise.

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
- **Where the orrery motif sits** (§1a). Sky is the default, so most of a
  wing's sketches carry it there; when a scene has no sky, vary the carrier.
  Six compasses is a logo, and so is six little discs of any kind.

**Read the wing's prompt history before writing a new one.** Every prompt is
posted as a comment on its own GitHub issue, and the issue title carries the
slug, so the wing's whole visual record is one query:

    gh issue list --repo rfsbraz/orrery-content --state all \
      --search "<wing-slug> in:title" --json number,title,comments

That is the only way monotony can actually be checked. An agent writing a
wing's seventh sketch cannot otherwise know what the first six chose, and
"vary it between assets" becomes an instruction nobody is able to follow.
Skim the previous prompts for the distances, the carriers, the tonal casts and
the objects already used, then deliberately go somewhere else.

The app alternates which side of the card the illustration sits on as you go
down the page, so **do not build the composition around a side**: keep the
subject central enough to read mirrored.

## 4c. Writing a still-life brief without producing clutter

A still-life prompt fails in a specific, repeatable way: **every object you name
gets drawn.** Name ten and you get ten, evenly weighted, filling the frame, with
no focal point and none of the negative space §1 requires. The result looks like
a flatlay rather than a drawing.

- **Name four or five objects, not ten**, and say what the frame should hold
  *most* of: *"a work table with only a few things on it, and real air between
  them"*.
- **Give the composition a subject.** One object leads; the rest support it.
  Without that the eye has nowhere to land.
- **Put the orrery motif off centre.** Dead centre makes it the subject, which
  §1a forbids. Say where it sits: *"toward the lower left, not centred"*.
- **State the break-out first, not last.** If the presentation is a torn sheet
  with objects crossing its edge (§5a), that instruction belongs near the top
  of the brief. Buried after an object list it gets ignored, and everything
  stays politely inside the rectangle.
- **Keep tonal variation inside the wing's palette.** §4a asks for a different
  temperature per asset, and it is easy to overshoot: "cool greys and ink
  blue-black" on a warm-umber wing produced blue-grey books that belong to a
  different catalogue. Say *"cooler within the same umbers"*, never a new
  colour family.

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
3a. **Where the orrery motif sits in this scene** (§1a) - the sky by default,
   an object only when the scene has no sky to use. Keep it faint, small and
   off-centre; it is an afterthought a reader finds on second look, never
   something the prompt dwells on.
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
