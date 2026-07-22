---
name: visual-language
description: Settle a wing's visual law - the art block on theme.yaml that every sketch for that wing must obey. Use when a wing has no theme.art, or when its bibliography or eras have changed enough that the existing art language no longer describes the books. Runs before any asset is generated for that wing.
---

# visual-language

Write the `art:` block on `content/franchises/<slug>/theme.yaml`: the motifs,
atmosphere, line character, background texture, accent rule and prohibitions
that every drawing made for this wing must obey. Output is git YAML, reviewed
by a curator via PR.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md) - the
prime directives, comment policy, gates, shared trap registry and verification
doctrine apply throughout and are not repeated here.

## Cheap tools before expensive habits (this stage pays for its own calls)

Every tool call re-sends your whole context, so what a stage costs is roughly
its context multiplied by how many calls it makes. One wing's editions stage
made 144 sequential fetches; the pages were not the expense, fetching them one
at a time was. Three habits, before you start:

- **Fetch in batches, not one by one.** `python scripts/fetch.py URL [URL...]`
  takes many URLs in a single call, caches to `.cache/fetch/` (so a URL an
  earlier stage already paid for is free), sends the browser User-Agent that
  portoeditora.pt, infopedia.pt, observador.pt and the BNP catalogue require,
  and prints a bounded extract rather than a whole page. Use `--grep 'ISBN|1a ed'`
  to pull just what you need, `--check` for link sweeps, `--max-chars` to tighten.
  Collect the URLs you want, then make one call. **web.archive.org rate-limits
  and starts refusing connections at the default 6 workers** - pass
  `--workers 2` for archive-heavy batches rather than losing the batch.
- **Orient with the digest before reading the wing.**
  `python scripts/wing_digest.py <slug> --for <your stage>` renders a finished
  wing in ~2.4KB where the YAML is ~98KB, and answers "which works still lack a
  cover, an edition, a synopsis, an era" directly (`--missing cover`). Then read
  in full the entries you are actually going to edit - the digest orients, it
  never substitutes for reading what you edit.
- **Scope every check to your own wing.** You are building one author; a report
  covering nine buries your own numbers, costs context for nothing, and tempts
  you to tune against a neighbour's figures or "fix" a wing nobody asked you to
  touch. Pass the slug:
  `validate.py --slug <slug>` (checking stays catalogue-wide - a broken
  reference crosses wings - only the warning list narrows),
  `aura_density.py <slug>`, `wing_digest.py <slug>`, `asset_audit.py <slug>`,
  `stage_plan.py <slug>`. `event_density.py` has no slug on purpose: it measures
  the shared `global.yaml` budget, which is catalogue-wide by nature.
- **Build the URL instead of searching for it.** Publisher product pages and
  catalogue records follow patterns. A search whose only output is a URL you
  could have constructed costs thousands of tokens for nothing. Search when you
  need to discover *that* something exists; fetch when you know where it is.

None of this licenses thinner research. It buys the same evidence for less, so
that the budget goes on judgement instead of on transport.

## The sanctuary rule (no exceptions, including for this stage)

**A content YAML file is a sanctuary for the author and the work.** A comment in
one explains the data sitting next to it: the source a value came from, why this
value and not the rival one, why a slot is deliberately empty and what was
checked to establish that, a trap the next reader would otherwise fall into.
That is the whole permitted range.

A comment never mentions the curating. Not the stage, agent, pass, run, budget
or tooling. Not addressing anyone ("a curator call", "left to the curator",
"flag if a future pass finds..."). Not narrating the research instead of the
data ("not yet a finished audit", "first built on one source, since checked
against two", "that remains open") - collapse those to what is known, in the
present tense: "publisher and year are corroborated by two independent sources;
the 2018 title rests on one." The weakness survives the edit. The diary does
not.

The test: **would this comment still be true and useful if the pipeline had
never existed and a human had typed the file by hand?** Process belongs in the
handoff, the PR body and git history. `docs/CURATION.md` §2 is the long form;
`validate.py` scans content comments and warns.

## Why this stage exists at all

Assets are generated one at a time, months apart, by a model with no memory of
the last one. Nothing about that process produces consistency on its own. The
`art:` block is the only thing standing between a wing and ten illustrations
that happen to share a subject and nothing else.

So this is a **gate, not a garnish**. `scripts/asset_audit.py` refuses to list
a single job for a wing without it, and `scripts/validate.py` fails a wing that
has none. Seven of the catalogue's ten wings once sat blocked behind exactly
this, which is roughly 156 assets that could not be drawn because nobody had
decided what they should look like.

## What you are actually deciding

Six fields, and each one is a constraint on a future drawing, not a mood board:

- **`motifs`** - the recurring objects, places and framings this wing returns
  to. Derive them from the books: read `eras.yaml` and skim `works.yaml`
  titles. Motifs taken from the genre's reputation rather than the author's
  actual work are how a wing ends up looking like its own marketing.
- **`atmosphere`** - the emotional weather, and what it is NOT. This is where
  you rule out the obvious cliche before it arrives.
- **`lineCharacter`** - how the mark is made. The single most load-bearing
  field, because it is what makes two drawings look like one hand. Be physical
  and specific: what instrument, what pressure, ruled or not, what kind of
  imperfection.
- **`backgroundTexture`** - the paper the wing is drawn on.
- **`accentUse`** - the palette's accent colour is a scalpel. Name exactly ONE
  element per image it may touch, and say it is never a fill.
- **`avoid`** - the wing's specific prohibitions, beyond the shared negative
  prompt in `docs/VISUAL.md` §6. Name the cliche this author's work attracts.

## Distinctness is the job

A visual language that could belong to any wing has failed even if every field
is filled in. Before writing, read the `art:` block of every wing that already
has one, and be explicit about how yours differs.

Look hard for **adjacency**: wings sharing a palette accent, a display face, a
language, a genre or a country will converge unless pushed apart deliberately.
Two epic-fantasy wings sharing a gold accent were separated by drawing one with
an instrument (mineral, ruled, diagrammatic) and the other with a thread
(woven, curved, illuminated). A third Portuguese wing was kept clear of the
other two by being urban, wet and nocturnal where they are rural and dry. When
the risk is real, put the differentiation in the `avoid` list, in words.

## What you must not do

- **Do not touch `palette`, `preset`, `displayFace`, `signature` or `notes`.**
  They are set at scaffold and the app's implemented sets constrain them. You
  are adding a block, not redesigning a wing.
- **Do not use the books' own cover art, in-world heraldry, glyphs or an
  adaptation's visual identity as a motif.** We draw the author's territory,
  not the merchandise, and copying a living illustrator's style is both a
  rights problem and an admission we had no idea of our own.
- **Do not specify a real person's likeness.** `docs/VISUAL.md` §3 is absolute:
  real people are photographed, never generated. A life event is drawn as its
  place or its consequence.
- **Do not bake in text.** Lettering does not survive translation to pt-PT, and
  image models garble it.
- **Do not describe edges, fades, crops, rounding or opacity.** Those belong to
  the app (`components/sketch.tsx`), not to the prompt or the language. See
  VISUAL.md §5a.

## Done means

- `art:` present with all six fields, on every wing you were asked to settle.
- `python scripts/asset_audit.py <slug>` reports `art:yes` and now lists jobs.
- `python scripts/validate.py` exits 0, checked directly and run after your
  last write.
- You can say in one sentence how this wing's drawings will differ from those
  of the wing nearest it, and that sentence is reflected in the YAML.
