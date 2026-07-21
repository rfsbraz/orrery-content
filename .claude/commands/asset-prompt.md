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

Follow `docs/VISUAL.md` §5 in order: house style, the wing's `art` quoted
rather than paraphrased, the subject from the entity's own `title` and
`description`, the composition from the asset spec, then the shared negative
prompt plus the wing's `art.avoid`.

Two rules that override any instinct to make a nicer picture:

- **Draw only what the record says.** The description is the brief. Do not add
  incident, symbolism or biography the entity does not carry - an invented
  detail in an illustration is still an invented fact.
- **Never a likeness of a real person** (§3). A life event is its place, its
  weather, its objects or its consequence. For a death or a bereavement, draw
  the absence.

For a `world-event`, drop the wing's art language entirely: neutral house
style, transparent background, no author-specific motifs.

## Return

Always all six, in this order:

1. **Asset** - type, entity id, and the wing it belongs to.
2. **The prompt** - one block, ready to paste, no commentary inside it.
3. **Size** - from the spec table (`1536x1024` era plates, `1024x1024` events).
4. **Background** - opaque, or transparent for world events (and say it must be
   tinted per wing with that accent).
5. **Reference images** - for Orrery assets the answer is **no**: the only
   asset that would want them is an author likeness, and we do not generate
   those. Say so explicitly rather than leaving it unstated, and if a future
   asset type does want references, name exactly which images and why.
6. **Filing** - the YAML to add once the image is hosted, with `sketchCredit`
   saying it was generated (the validator rejects a credit that reads like a
   source).

Then one line on what to check when the image comes back: whether it sits
beside the wing's existing assets without looking like a different system.
