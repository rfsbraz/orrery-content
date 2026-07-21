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
- subtle celestial or orbital geometry, used sparingly and never as decoration
  for its own sake
- no photorealism, no glossy 3D, no game concept art
- **no typography inside the image, ever** (the app sets its own type over it)

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

## 4. Asset specs

| Asset | Size | Background | References | Renders in |
|---|---|---|---|---|
| `era-plate` | `1536x1024` | opaque, wing paper tone | no | the era plate in `river.tsx`, full-bleed behind the title |
| `life-event` | `1024x1024` | opaque, wing paper tone | no | an event seam in the river / timeline |
| `franchise-event` | `1024x1024` | opaque, wing paper tone | no | an event seam in the river / timeline |
| `world-event` | `1024x1024` | **transparent** | no | every wing that carries the event, **tinted with that wing's `accent`** |
| `work-cover` | - | - | - | not generated: covers are licensed or absent (see `visual-metadata`) |
| `author-portrait` | - | - | - | not generated: see §3 |

World events are shared, so they are drawn once in the neutral house style with
no wing-specific motifs, on transparency, and coloured per wing in CSS. A
world-event sketch that only suits one author is a bug.

## 5. Assembling a prompt

In order, always:

1. **The house style** (§1), stated plainly.
2. **The wing's `theme.art`** from `theme.yaml`: motifs, atmosphere,
   lineCharacter, backgroundTexture, accentUse. Quote it, do not paraphrase it
   away - it is the only thing making two assets belong to the same wing.
3. **The subject**, derived from the entity's own `title` and `description`.
   Draw what the record says happened; do not invent incident.
4. **The composition**, from the asset spec (§4).
5. **The shared negative prompt** (§6), plus the wing's own `art.avoid`.

For a **world event**, skip step 2 entirely and say "neutral house style, no
author-specific motifs, transparent background".

## 6. Shared negative prompt

Append to every prompt:

> Avoid: photorealism; cinematic concept art; generic fantasy art; anime;
> children's-book cartoon styling; glossy 3D rendering; neon colours; heavy
> gradients; thick black outlines; crowded compositions; any text, lettering,
> captions, signatures or watermarks; publisher logos; reproductions of real
> book covers; UI elements; decorative elements covering faces; excessive stars
> and planets; literal outer-space imagery unrelated to the subject.

Plus the wing's `art.avoid`, which names that author's specific cliche.

## 7. Workflow for a wing

1. Settle `theme.art` in `theme.yaml`. Nothing else may be generated first.
2. Era plates, largest surfaces first - they set the palette in practice.
3. Life events, then franchise events.
4. Shared world events last, in house style.
5. Put every result side by side before accepting any of it. Reject anything
   that looks like a different illustration system, however good it is alone.
6. Record the asset with `sketch` + `sketchCredit` saying it was generated.

`python scripts/asset_audit.py <slug>` reports what exists and what is next in
exactly this order; `/asset-prompt` writes the prompt for one asset.

## 8. Colour

The interface palette stays stable across the catalogue: deep navy, warm cream,
off-white, muted blue-grey, charcoal text. A wing's own palette applies to
sketch backgrounds, era plates, hero areas, dividers and progress accents -
never to navigation, typography, spacing or main surfaces.

Each wing has one dominant accent (`theme.palette.accent`), used in artwork on
**one element per image, never as a fill**.
