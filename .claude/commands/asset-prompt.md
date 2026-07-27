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
(the 16 organisations, the compatibility rules, the rotation budget), and
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
  `diptych`/`split-counterpoint`; more for a `strip`; **0 for an `epigraph`**).
- **For each `franchise-event`, weigh whether it is about the fiction itself**
  - a character's debut, a franchise milestone, an adaptation announcing its
  own identity, a scene whose *reception* is the event - and if so, whether a
  character or scene reference (VISUAL.md §3c) would carry the moment better
  than staying purely contextual. This is a per-event judgement, not a
  default: most franchise events (a sale figure, a prize, a contract dispute)
  have no character in them and should stay exactly as before. Life events are
  never in scope for this - §3/§3a's real-person discipline is unchanged.
  Record the call either way; a "no" here is as much a decision as a "yes".

**`epigraph` produces no prompt.** It is the one organisation with no artwork:
the author's own words are the illustration, so it gets no `illustration_type`,
no `Rotation:` illustration fields, no size, no reference image, no filing
command and **no issue** - it is assigned in Step 1 like any other
organisation, and then Step 2 simply skips it. What it needs instead is the
`quote` itself, verbatim and sourced, written straight onto the event in
content (`quote`, `title` as attribution, `sources`, `images_required: 0`).
Never reconstruct a quotation from memory or paraphrase one into place: an
invented drawing is an invented detail, but an invented quotation is words put
in a real person's mouth in their own voice. If the exact wording cannot be
sourced, do not make it an `epigraph`.

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

**Point the picture down the page** (§4a). Where the subject has an implied
direction, the `COMPOSITION` block states it: into the depth of the frame or
descending, never up and out of the top edge. A river is read one way, and a
picture that faces out of it stops the reader. Say it as depth or descent, not
as left or right - the app mirrors which side the art sits on. This one is
constant across the wing, not rotated.

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
2. **The prompt** - one block per image, ready to paste, no commentary inside it.

   **Always put the prompt inside a fenced code block** (```` ```text ````), with
   nothing else inside the fence: it opens at `STYLE:` and closes after the
   technical block. The prompt is not something to read on the issue, it is
   something to copy into a generator in one click, and prose on a GitHub page
   has to be hand-selected across a page-and-a-half of scrolling. Everything
   that is *about* the asset - the `Rotation:` line, the slot heading, size,
   background, reference images, the filing command, what to check - stays
   OUTSIDE the fence, both because it must not reach the generator and because
   `art_rotation.py` parses the `Rotation:` line out of the comment body. On a
   multi-slot entry each slot gets its own fence, with that slot's size,
   background and filing under it.

   **One image, one prompt. An entry with `images_required: n` gets `n` complete
   prompts, never one prompt describing n panels.** A single prompt that says
   "IMAGE 1 ... IMAGE 2" asks the model to compose a multi-panel layout inside
   one frame, which is the thing it is worst at, and it contradicts the asset
   block it is answering (`images_required: 2`, two slots, two destination
   files). Each prompt repeats the STYLE block verbatim and stands entirely on
   its own - own SCENE, own SUBJECT, own motif paragraph, own COMPOSITION, own
   CONSTRAINTS and technical block - because it is pasted on its own. Label them
   `Slot 1 of n`, `Slot 2 of n`, and say what each one is (the before, the
   after, the third instalment), so the relationship survives being split.

   **A sequence drawn as one run is the exception.** A comic strip, a contact
   sheet, a row of weekly instalment panels - `strip`, `mosaic`, `layered-stack`
   - stays at `images_required: 1` and one prompt: the shared baseline, even
   spacing and repetition across the run are the picture, and drawing the units
   separately gives a row of unrelated sketches. Only the two-panel
   counterpoints (`diptych`, `split-counterpoint`) split.

   **All n prompts go in ONE comment.** `art_rotation.py` reads only the
   issue's last comment for the `Rotation:` line, and `issue_assets.py` starts
   the round at the last comment carrying a prompt - so one prompt per comment
   would drop the asset out of the rotation counts and reset the round halfway
   through the set. One comment, one `Rotation:` line at the top, n prompt
   blocks under it.

   Each prompt block: describe
   the whole image concept first; then, as the **last** creative step, add the
   **orrery motif** as its own paragraph (VISUAL.md §1a): the universal
   concentric rings - **never this wing's emblem** - dropped into an off-centre
   spot the finished scene allows, in a carrier you have not used elsewhere in
   this wing (vary it every time). A clause bolted onto another sentence, or the
   wing's emblem borrowed in its place, is what makes the motif tangle or vanish.
   It must end with the **technical block** (§5b): exact pixel dimensions,
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
   per wing. On a multi-image entry, size, background, reference and filing are
   stated **under each slot's prompt**, not once for the set - the person
   generating works one slot at a time.
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

   On a multi-image entry the slots are **siblings and must be generated in
   order**: slot 1 against the anchor, then each later slot against the anchor
   **plus the accepted slot 1**, saying that these panels are one entry and
   share line weight, paper tone, shading density and object language, only the
   subject changing. That is not the chaining §5d warns about - the drift being
   guarded there is across a wing, and two panels rendered side by side in one
   cell have to match each other or the cell looks broken.
6. **Filing** - the `prepare_asset.py` command with the flags the illustration
   type needs: `--chroma --neutral` for keyed types; add `--type <illustration_type>`
   so the processor applies the right edge (artifact types skip the dissolve,
   opaque types skip chroma); `--opaque` for opaque scene types; `--slot N` for
   each image of a multi-image entry. `--neutral` full strength on a cold wing,
   ~0.4 on a warm one. Then the YAML it prints, with `sketchCredit` saying it was
   generated (the validator rejects a credit that reads like a source).

Then one line on what to check when the image comes back: whether it sits
beside the wing's existing assets without looking like a different system.
