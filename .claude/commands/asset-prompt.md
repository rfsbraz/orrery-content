---
description: Compose a whole author wing's visual layer at once - assign each event an organisation (how it lays out) and an illustration type (what it depicts), as one told story, then write every ready-to-paste gpt-image-1 prompt with the rhythm already planned across the wing.
argument-hint: <slug>   (the whole wing; or <slug> <entity-id> for one asset against an already-planned wing)
---

# /asset-prompt

Compose the visual layer for the **$ARGUMENTS** wing. The default and correct
mode is **the whole wing in one pass**: a life is told down a page, and its
rhythm - the shape of each cell and the kind of picture in it - can only be
composed by seeing the whole timeline at once. A prompt written for one event in
isolation cannot know it is the fourth still-life in a row.

Two axes decide each entry (kept separate on purpose - see `docs/LAYOUT.md`):

- **`organisation`** - how the cell lays image and text out; the app renders one
  of 15. This is where *variety* lives, and it is assigned as **rhythm** across
  the wing (the budget below).
- **`illustration_type`** - what the artwork depicts and how it is authored; one
  of 25 (`docs/PROMPT-MODULES.md` has the authoring brief for each). This is
  where *cohesion* lives: every one is drawn in the wing's own `theme.art`.

Sources of truth, read them, do not restate them: `docs/VISUAL.md` (house style,
§3b illustration catalogue, §5b technical block, §6 negative prompt), `docs/LAYOUT.md`
(the 15 organisations, the compatibility rules, the rotation budget), and
`docs/PROMPT-MODULES.md` (the per-illustration-type authoring modules). This
command owns the assembly and the *composition of the wing as a story*.

## Read the whole wing first

Read the wing's `theme.art` and `palette.accent` (`theme.yaml`), and **every**
event in timeline order: the eras (`eras.yaml`), the life events
(`content/authors/<id>.yaml`), and the franchise events (`events.yaml`), plus
the shared world events that reach it. Use `scripts/wing_digest.py <slug>` to
orient cheaply, then read the entries you will plan.

**If `theme.art` is missing, stop.** A wing generated without it will not cohere,
and cohesion is the entire point.

## Step 1: compose the wing (before any prompt)

Assign every event two fields, as one told story, and write the plan down before
writing a single prompt:

- **`organisation`** per event, honouring the LAYOUT.md **rotation budget**:
  `beside` is the workhorse (~half); every other organisation capped at ~40%;
  `immersion` 1-2 for the largest ruptures only; `chapter-gate` one per era;
  `interlude` for a real silence; **no two consecutive events share an
  organisation**. Assign to track the life - open a period with `full-bleed-vista`
  or `chapter-gate`, carry dead years with `passage`/`interlude`, stop at a death
  with `immersion`, file evidence with `artifact-spread`.
- **`illustration_type`** per event, from the 25, compatible with that event's
  organisation (LAYOUT.md's Holds), and rotated on composition/distance/tonal
  cast per VISUAL.md §4a so no type dominates.
- **`images_required`** per event, from the organisation (1 for most; 2 for
  `diptych`/`split-counterpoint`; more for a `strip`).

Run `scripts/art_rotation.py <slug> --check` against the plan once assigned; it
scores both axes and fails on a broken cap or a repeated neighbour. Revise until
it holds. This is the step that makes the wing a story rather than a stack.

## Step 2: assemble each prompt from the two axes

Follow `docs/VISUAL.md` §5 and the skeleton in `PROMPT-MODULES.md`: **labelled
sections** (`STYLE`, `SCENE`, `SUBJECT`, `DETAIL`, `COMPOSITION`, `CONSTRAINTS`),
never one paragraph, the wing's `art` quoted not paraphrased, constraints last,
under ~6,000 characters (long prompts fail silently).

The two axes meet in the `COMPOSITION` block: the **illustration module**
(`PROMPT-MODULES.md`) says what the picture is; the **organisation**
(`LAYOUT.md`) says what shape it must be and where the text will sit. State the
organisation's art requirement explicitly - a `full-bleed-vista` is a wide
opaque scene with no reserved text zone; an `immersion` reserves a 35-45%
low-detail quiet zone for text over the art; a `medallion` centres the subject
in a circular safe area; an `artifact-spread` is the document itself. Aspect and
background come from the illustration type (§3b), never assumed square.

**The wing was composed in Step 1, so the rhythm is already planned** - each
prompt just realises its assigned organisation and type. Still check each
sketch's composition against its neighbours (§4a): even within one illustration
type, vary distance, tonal cast and the motif carrier.

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

## The edge is still the processor's job, not the prompt's

For every keyed type (object and scene types, per §3b), **the dissolve is applied
by `prepare_asset.py`, not drawn by the model**. Do not describe the edge - no
torn paper, no fading, no ragged ink - ask only that the artwork leaves ~a tenth
of the frame as magenta. The exception is the three **artifact types**
(`document-facsimile`, `manuscript-proof`, `archive-stack`): those ARE about the
paper, so they draw their own torn/folded/stacked edge and file `--no-dissolve`.
And **opaque scene types** (`full-bleed-vista`, `immersion`, `establishing-landscape`
et al. per §3b) are opaque, not keyed - no magenta, no dissolve, filed `--opaque`.

A shared world event still has no latitude: line and texture only, or the
per-wing tint turns it into a coloured blob.

## Return

Always all six, in this order:

1. **Asset** - type, entity id, the wing it belongs to.

   Then, on its own line and in exactly this form, the grammar + rotation
   fields (both axes, so `art_rotation.py` can score the wing from the issues):

       Rotation: organisation=<org> | illustration=<type> | images=<n> | composition=<type> | distance=<far|middle|near> | cast=<tonal cast> | carrier=<orrery motif carrier>

   `scripts/art_rotation.py <slug>` parses this line out of the issue comments to
   rebuild the wing's rotation on both axes, which is how the budget and the §4a
   cap are checked at all. Keep the line exactly as shown; an unparsed line drops
   the asset from the counts and makes the wing look more varied than it is.

   Also record the grammar fields onto the event itself in content
   (`organisation`, `illustration_type`, `images_required`, any `modifier`) - the
   app and the validator read them there; the issue line is for the rotation
   tracker.
2. **The prompt** - one block, ready to paste, no commentary inside it. It must
   contain the orrery motif as its **own paragraph** (VISUAL.md §1a - a clause
   bolted onto another sentence is what produces a tangled, illegible motif),
   and it must end with the **technical block** (§5b): exact pixel dimensions,
   a flat fully-saturated magenta `#FF00FF` background to be keyed out later
   (never ask for transparency - it does not survive the download, and the
   parameter knocks out light regions inside the drawing), an explicit ban on
   any glow, halo, mist or gradient between the artwork and the magenta, and no
   frame or matte.
3. **Size** - the exact pixel dimensions for the illustration type's aspect
   (§3b), e.g. `1536x1024` for a `16:9` vista, `1024x1024` for a square object,
   `1024x1536` for a `4:5` portrait. State exact pixels, never a ratio.
4. **Background** - keyed magenta for object/scene types, **opaque** for the
   opaque scene types, per §3b; world events are line-and-texture only, tinted
   per wing. Multi-image entries (`images_required > 1`) list each image's
   subject and slot.
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
6. **Filing** - the `prepare_asset.py` command with the flags the illustration
   type needs: `--chroma --neutral` for keyed types; add `--type <illustration_type>`
   so the processor applies the right edge (artifact types skip the dissolve,
   opaque types skip chroma); `--opaque` for opaque scene types; `--slot N` for
   each image of a multi-image entry. `--neutral` full strength on a cold wing,
   ~0.4 on a warm one. Then the YAML it prints, with `sketchCredit` saying it was
   generated (the validator rejects a credit that reads like a source).

Then one line on what to check when the image comes back: whether it sits
beside the wing's existing assets without looking like a different system.
