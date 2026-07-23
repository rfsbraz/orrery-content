---
description: Write the image-generation prompt for one Orrery visual asset - identify the asset type, assemble it from the house style and the wing's own art language, and state size, background, reference-image policy and where it lands.
argument-hint: <slug> <asset-type> <entity-id>   (or just <slug> to take the next job)
---

# /asset-prompt

Produce a ready-to-paste **gpt-image-1** prompt for one asset of **$ARGUMENTS**,
plus everything needed to generate and file it.

`docs/VISUAL.md` is the source of truth for the house style, the asset specs and
the negative prompt. This command owns only the assembly: reading the right
entity, pulling the wing's art language, and returning a prompt that could not
have come from another wing.

## Resolve the job

With a slug only, take the next job from
`python scripts/asset_audit.py <slug> --next`. With an explicit asset type and
id, use that.

Then read, and read nothing else:

- `content/franchises/<slug>/theme.yaml` -> `art` (the wing's visual language)
  and `palette.accent`.
- the entity itself: the era in `eras.yaml`, the event in `events.yaml`, the
  life event on `content/authors/<id>.yaml`, or the world event in
  `content/events/global.yaml`.

**If `theme.art` is missing, stop.** Say so and ask for it to be settled first;
a sketch generated without it will not match the wing, and matching is the
entire point.

## Assemble

Follow `docs/VISUAL.md` §5: **labelled sections** (`STYLE`, `SCENE`, `SUBJECT`,
`DETAIL`, `COMPOSITION`, `CONSTRAINTS`), never one long paragraph, with the
wing's `art` quoted rather than paraphrased and the constraints last. Keep the
whole prompt under ~6,000 characters: the documented cap is far higher, but long
prompts are reported to fail silently, returning an image with little relation
to the instructions and no error.

**Look at the neighbours first.** For a life or franchise event, read the
sketches already filed on the two events either side of it in the timeline
(`scripts/asset_audit.py <slug>` lists them in order) and vary at least two of
composition type, distance, tonal cast and motif carrier, per VISUAL.md §4a. A
sequence of individually good sketches that all look alike is the failure this
stage is most likely to produce, and it is invisible one asset at a time.

**Draw the moment, not a table of objects.** §3's ban on inventing a real
person's face is not a ban on people, scenes or incident (§3a). Anonymous
figures, crowds, rooms in use and weather are all in scope, and a wing whose
sketches are mostly close still-lifes has failed §4a - the Mãe wing shipped
seven of eleven that way. No composition type may take more than a third of a
wing.

Two rules that override any instinct to make a nicer picture:

- **Draw only what the record says.** The description is the brief. Do not add
  incident, symbolism or biography the entity does not carry - an invented
  detail in an illustration is still an invented fact.
- **Never a likeness of a real person** (§3). A life event is its place, its
  weather, its objects or its consequence. For a death or a bereavement, draw
  the absence.

For a `world-event`, drop the wing's art language entirely: neutral house
style, transparent background, no author-specific motifs.

## The presentation is not a choice any more

VISUAL.md §5a used to offer four modes per asset. It offers one: every event
sketch is a dissolving panel, and **the dissolve itself is applied by
`prepare_asset.py`, not drawn by the model**. Do not describe the edge in the
prompt - no torn paper, no fading, no ragged ink. Ask only that the artwork
leaves roughly a tenth of the frame as magenta all the way around.

Every event now lands on the same dark card, ruptures included (they get scale,
not an inverted band), so there is no per-surface judgement left to make either.

The transparency invariant never bends, and a world-event sketch has no latitude
at all: line and texture only, or the per-wing tint turns it into a coloured
blob.

## Return

Always all six, in this order:

1. **Asset** - type, entity id, the wing it belongs to.

   Then, on its own line and in exactly this form, the four rotation fields:

       Rotation: composition=<type> | distance=<far|middle|near> | cast=<tonal cast> | carrier=<orrery motif carrier>

   `scripts/art_rotation.py <slug>` parses this line out of the issue comments
   to rebuild the wing's whole rotation table, which is how §4a's cap can be
   checked at all. The rotation plan used to live in a branch-local `.orrery/`
   file that is deleted before merge, so the one artifact needed to write the
   wing's next asset evaporated the moment the wing was finished. Derived from
   the issues it cannot go stale, because the issues are what actually happened.

   Keep the line exactly as shown. A prompt whose rotation cannot be parsed is
   reported as unparsed and left out of the counts, which makes the wing look
   more varied than it is.
2. **The prompt** - one block, ready to paste, no commentary inside it. It must
   contain the orrery motif as its **own paragraph** (VISUAL.md §1a - a clause
   bolted onto another sentence is what produces a tangled, illegible motif),
   and it must end with the **technical block** (§5b): exact pixel dimensions,
   a flat fully-saturated magenta `#FF00FF` background to be keyed out later
   (never ask for transparency - it does not survive the download, and the
   parameter knocks out light regions inside the drawing), an explicit ban on
   any glow, halo, mist or gradient between the artwork and the magenta, and no
   frame or matte.
3. **Size** - from the spec table (`1536x1024` era plates, `1024x1024` events).
4. **Background** - opaque, or transparent for world events (and say it must be
   tinted per wing with that accent).
5. **Reference images** - name the wing's **anchor image** (§5d) and say to
   attach it, plus up to two other accepted assets from the same wing that
   differ in subject. This is the strongest cohesion tool available and the
   first two wings were built without it: there is no seed and no style token
   for this model, so a style block in the prompt is necessary and not
   sufficient. Always re-anchor to the original; never chain off the asset
   generated immediately before, which compounds drift.

   The only exception is the wing's own first era plate, which has no anchor
   yet because it becomes one, and world events, which belong to the catalogue
   rather than to a wing.
6. **Filing** - the `prepare_asset.py --chroma` command, plus `--neutral` (full
   strength on a cold wing, ~0.4 on a warm one) to correct the model's warm
   cast, and the YAML it prints, with `sketchCredit` saying it was generated
   (the validator rejects a credit that reads like a source).

Then one line on what to check when the image comes back: whether it sits
beside the wing's existing assets without looking like a different system.
