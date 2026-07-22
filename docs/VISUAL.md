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

## 3a. Withholding a likeness is not the same as refusing to draw

§3 forbids one specific thing: **inventing the face of a real person**. It has
repeatedly been read as forbidding something much larger - people, scenes,
weather, incident, the world - and the cost of that misreading is visible in
the first two finished wings. Of eleven Mãe seam sketches, seven were a table
seen at three-quarters from the middle distance. Not because seven of those
moments were about a table, but because a still-life of objects is the safest
thing to draw when you believe you are not allowed to draw anything else.

**Draw the moment.** A sketch may contain:

- **Anonymous figures**, as many as the scene wants: a crowd at a reading, a
  queue outside a shop, workers on a press, a child in a doorway, a congregation
  of folding chairs with people actually in them. Turned away, at distance, in
  silhouette, mid-gesture, cropped by the frame. What is banned is a recognisable
  likeness of a *named real person*, not the human figure.
- **Action and incident.** Weather arriving, a room mid-argument, a press
  running, a street at closing time, a hospital corridor with someone walking
  down it.
- **Place at full scale.** A village, a coastline, a city block, an interior with
  a world visible through its window.

Scale the pictorialism to the wing and to the moment. A wing whose `theme.art`
asks for the flat register of an instruction manual should stay closer to
diagram than to landscape - that is its identity, not timidity - but even there,
the pictogram figures on the safety card are *figures*, and the wing is allowed
to use them. A wing built on villages, hands and weather should be full of
villages, hands and weather.

**The test is whether a reader could describe what happened from the picture.**
Four objects arranged on a table rarely passes it. A room with people in it
usually does.

The object still-life remains one composition type among several in §4a. It is
not the default, and a wing where it is the majority has failed §4a whether or
not each sketch is good on its own.

## 4. Asset specs

| Asset | Size | Background | References | Renders in |
|---|---|---|---|---|
| `era-plate` | `1536x1024` | **transparent** (chroma key, §5b) | no | the right half of the era plate, bleeding off the page edge; the title and prose hold the left (see §4b) |
| `life-event` | `1024x1024` | **transparent** | no | the illustrated event card in `river.tsx`, laid beside the prose |
| `franchise-event` | `1024x1024` | **transparent** | no | the illustrated event card in `river.tsx` |
| `world-event` | `1024x1024` | **transparent** | no | every wing that carries the event, **tinted with that wing's `accent`** |
| `work-cover` | - | - | - | not generated: covers are licensed or absent (see `visual-metadata`) |
| `author-portrait` | - | - | - | not generated: see §3 |

**Every generated asset is chroma-keyed, era plates included.** This table once
said era plates were opaque on the wing's paper tone, which was wrong and was
caught when a prompt writer followed the first plate's actual precedent instead
of the docs. A plate dissolves into the page, and that only works with alpha:
baked onto paper it becomes a rectangle sitting on the page rather than part of
it, and a baked paper tone can only match one wing's background.

The app additionally masks a plate with a soft radial fade (`variant="plate"` in
`sketch.tsx`), so a plate that also draws its own hard edge gets treated twice
and reads as a picture inside a picture. Draw it to §5a's dissolve like
everything else and let the mask do the rest.

Shared world-event art lives in `assets/global/`, not under any one wing: it is
catalogue canon, and filing it beside the author who happened to prompt it
would imply otherwise.

World events are shared, so they are drawn once in the neutral house style with
no wing-specific motifs, on transparency, and coloured per wing in CSS. A
world-event sketch that only suits one author is a bug.

## 4-impact. A high-impact event is a rupture, and earns its weight in scale

The river renders `impact: high` events as **ruptures**: the same dark card
every other event gets, at greater scale. Full column width, a taller
illustration bleeding further into the card, more vertical air, a larger title.
Nothing inverts.

**This used to be an inverted band in the wing's ink colour, and that was the
single worst decision in the visual system.** It was measured before it was
replaced: on the Palahniuk wing the band's luminance is 233 and its six rupture
sketches averaged 217, a separation of sixteen points out of 255. The art the
reader was meant to stop at was the least visible art on the page. The same
assets sit at ~190 points of separation on the dark card. A wing whose
`theme.art` calls for a pale, even-weight line - which is a legitimate and
well-argued identity - could not survive being dropped onto near-white paper,
so the treatment was punishing wings for having a point of view.

The consequence for prompt writers is the good news: **a rupture sketch and a
seam sketch have the same specification.** One surface, one spec, one way an
asset can look wrong. Only these differ:

- **Scale.** A rupture is drawn to hold a bigger box, so it can carry a wider
  scene and more depth. A seam is read at roughly a third of the column.
- **Pace.** This is the moment the reader is meant to stop at, so it earns
  stillness: fewer competing elements, more air between them, softer shading.
- **Register over incident.** A death is the room after the fact, not the fact.

Hierarchy now comes from size, space and typography, which is where hierarchy
belongs. It is never carried by a colour the artwork has to survive.

## 4a. Breaking monotony in a sequence

A wing's life events are read one after another down a single column, so a set
of individually good sketches can still fail: six wide landscapes with a warm
wash and a compass become wallpaper by the third. **Each sketch is drawn
against its neighbours, not only against its own brief.** Before writing a
prompt, look at what the two events either side of it already got, and vary at
least two of these four:

- **Composition type.** Rotate deliberately between: a wide landscape or vista;
  **a peopled scene** (a room in use, a crowd, a street, figures at work - see
  §3a); a cluttered working still-life seen close (a desk, a press, a kitchen
  table); a single object given the whole frame; and a quiet intimate
  arrangement (a vase, a candle, a photograph face-down). The 1971 birth is a
  vista, so the 1974 that follows it should not be.

  **Count them before accepting a wing.** No composition type may take more
  than a third of a wing's event sketches. The Mãe wing shipped with seven of
  eleven as the same close still-life, which no per-asset review caught because
  each one was individually fine. This is arithmetic, so do the arithmetic.
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
  frame; the artwork must not touch the border at any point; the ink and wash
  thin out and break up as they approach the magenta, fading to nothing at a
  different rate on each side, never a straight edge, never a torn-paper edge
  and never a rectangle."* Naming a rough margin helps - *"leave roughly a
  tenth of the frame as magenta around the artwork"*.
- **Ban the soft glow explicitly.** The model likes to ease the artwork into
  the chroma with a haze rather than break it up, and a magenta-to-artwork
  gradient is the one thing the keyer cannot resolve: it sits too far from the
  key to be cut and too close to be clean, and survives as an opaque mauve
  corona. Five shipped assets carry one. Say *"no glow, halo, mist, vignette or
  gradient between the artwork and the magenta; the transition is broken ink,
  not a blur"*.
- Still state **exact pixel dimensions** from §4 (`1024x1024` for an event,
  `1536x1024` for an era plate) - not "square", not an aspect ratio.
- Still ban borders, frames, mattes and drop shadows onto the background.

Then file it with:

    python scripts/prepare_asset.py <image.png> <slug> <entity-id> --chroma

which keys the magenta to real alpha with a soft edge, despills the fringe so
edges do not glow pink on a dark page, trims the empty margins, converts to
webp under the size cap and prints the YAML to paste.

## 5a. The presentation is fixed: one mode, every event

**Every event sketch is a dissolving panel.** The drawing fills its frame and
thins out at every edge, ink and wash fading to nothing rather than stopping at
a line. No torn sheet, no deckled edge, no drawn paper, no panel border, no
floating objects on nothing. The card behind the art supplies the frame, so the
artwork never draws one for itself.

This is not a preference. An earlier version of this section offered four modes
as an editorial choice per asset, and the result was measured across two
finished wings: within a single column you could find assets that were 100%
opaque hard rectangles, assets that were 79-94% opaque torn sheets, and assets
that were 20-33% floating objects. Three incompatible ways of meeting the page,
stacked one above the other. A reader does not experience that as range. They
experience it as nobody being in charge.

The choice was between enforcing "deliberate" across thirty-odd assets and
removing the decision. Enforcing it had already been tried and had already
failed, so the decision is removed.

What the dissolve has to get right:

- **It thins on all four sides.** A panel that fades on three edges and stops
  flat on the fourth reads as a crop, not a dissolve. This is the most common
  way this mode fails.
- **The fade is uneven and hand-made**, ink and wash running out at different
  rates in different places, never a soft-focus vignette and never a uniform
  radial blur. A machine-even fade looks like a filter, because it is one.
- **Something may cross the dissolve.** One element pushing out past the thinning
  edge - a branch, a spill of papers, a wheel - keeps the panel from reading as
  a rectangle with soft corners. Use it when a scene needs a foreground anchor;
  it is the one liberty left in this section.

What is not negotiable:

- **Nothing may assume what colour is behind it.** Transparent background
  always, no vignette, no painted-in page colour, no rounded rectangle, no
  frame, no drop shadow onto the background - shadows fall onto the surface
  within the artwork, never onto the void. This is the rule most likely to be
  broken by accident, and `scripts/validate.py` now checks it (§5c).
- **No baked paper tone.** The wing's paper is the card. An asset carrying its
  own paper colour is a rectangle sitting on the page, and it can only ever
  match one wing.

**World events are the exception and have less latitude, not more.** A shared
sketch is recoloured per wing by painting the wing's accent through its alpha,
so it must be **line and texture only, on transparency** - no paper, no wash, no
filled shapes. Anything with a solid fill becomes a solid accent-coloured blob.

## 5c. The invariants are checked, not trusted

Every rule in §5a that can be expressed as arithmetic is enforced by
`scripts/validate.py`. This section exists because the previous three failures
in this document were all *stated clearly and then violated anyway*: the opaque
era plate, the four presentation modes, the mauve corona. A rule nobody measures
is a rule nobody follows.

| Check | Fails when | Catches |
|---|---|---|
| `alpha-present` | opaque pixel fraction ≥ 0.98 | an asset that lost its alpha (`antes-dos-romances` was 1.00) |
| `edge-dissolve` | any frame edge has > 2% of its length opaque | a hard crop or a baked rectangle |
| `no-chroma-cast` | mean magenta excess > 8 over pixels with alpha > 120 | an un-keyed halo or spill |
| `world-event-flat` | a `global` asset has any large filled region | a sketch that will tint to a blob |

Each check reports the measured number, not a pass/fail word. A check that can
only say "ok" teaches nobody anything and cannot be argued with when it is
wrong.

**Watch these fail before trusting them.** Every one of them was written against
a known-bad asset and confirmed to reject it before being pointed at the
catalogue. `python scripts/validate.py --assets --explain <slug>` prints the
numbers per asset so a borderline case can be judged rather than obeyed.

## 6. Shared negative prompt

Append to every prompt:

> Avoid: photorealism; cinematic concept art; generic fantasy art; anime;
> children's-book cartoon styling; glossy 3D rendering; neon colours; heavy
> gradients; thick black outlines; cluttered compositions with no focal point;
> any text, lettering, captions, signatures or watermarks; publisher logos;
> reproductions of real book covers; UI elements; decorative elements covering
> faces; excessive stars and planets; literal outer-space imagery unrelated to
> the subject; vignettes; borders, frames or rounded rectangles; torn-paper,
> deckled or ragged-sheet edges; any glow, halo, mist or gradient around the
> artwork; any painted-in background colour; drop shadows cast onto the
> background rather than onto a surface within the artwork.

Note that this bans **clutter**, not people. A crowded frame with no focal point
is the failure; a scene with twenty figures in it and one clear subject is not
(§3a). Earlier versions read "crowded compositions" as "no crowds", which is
part of how two wings ended up with almost nobody in them.

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
