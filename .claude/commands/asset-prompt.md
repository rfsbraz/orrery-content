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

**Look at the neighbours first.** For a life or franchise event, read the
sketches already filed on the two events either side of it in the timeline
(`scripts/asset_audit.py <slug>` lists them in order) and vary at least two of
composition type, distance, tonal cast and motif carrier, per VISUAL.md §4a. A
sequence of individually good sketches that all look alike is the failure this
stage is most likely to produce, and it is invisible one asset at a time.

Two rules that override any instinct to make a nicer picture:

- **Draw only what the record says.** The description is the brief. Do not add
  incident, symbolism or biography the entity does not carry - an invented
  detail in an illustration is still an invented fact.
- **Never a likeness of a real person** (§3). A life event is its place, its
  weather, its objects or its consequence. For a death or a bereavement, draw
  the absence.

For a `world-event`, drop the wing's art language entirely: neutral house
style, transparent background, no author-specific motifs.

## Choose the presentation

Per VISUAL.md §5a, decide how this particular sketch should meet the page -
torn sheet, dissolving panel, objects on an implied surface, panel with a
break-out, or something else that serves the same end - and judge it on the
subject, the surface it lands on (a dark card, a half-page era spread, an
inverted rupture band) and what the neighbouring assets already did. State the
choice and the reason in the brief; it is an editorial call, not a default.

The transparency invariant is not part of that choice and never bends, and a
world-event sketch has no latitude at all: line and texture only, or the
per-wing tint turns it into a coloured blob.

## Return

Always all six, in this order:

1. **Asset** - type, entity id, the wing it belongs to, and the presentation
   chosen with its one-line reason.
2. **The prompt** - one block, ready to paste, no commentary inside it. It must
   contain the orrery motif as its **own paragraph** (VISUAL.md §1a - a clause
   bolted onto another sentence is what produces a tangled, illegible motif),
   and it must end with the **technical block** (§5b): exact pixel dimensions,
   a flat fully-saturated magenta `#FF00FF` background to be keyed out later
   (never ask for transparency - it does not survive the download), and no
   frame or matte.
3. **Size** - from the spec table (`1536x1024` era plates, `1024x1024` events).
4. **Background** - opaque, or transparent for world events (and say it must be
   tinted per wing with that accent).
5. **Reference images** - for Orrery assets the answer is **no**: the only
   asset that would want them is an author likeness, and we do not generate
   those. Say so explicitly rather than leaving it unstated, and if a future
   asset type does want references, name exactly which images and why.
6. **Filing** - the `prepare_asset.py --chroma` command and the YAML it prints, with `sketchCredit`
   saying it was generated (the validator rejects a credit that reads like a
   source).

Then one line on what to check when the image comes back: whether it sits
beside the wing's existing assets without looking like a different system.
