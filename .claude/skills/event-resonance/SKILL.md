---
name: event-resonance
description: Decide which global events actually belong on a specific author's timeline, and why. Judges resonance per franchise rather than assuming a global event reaches every author. Use after world-events changes the shared layer, or when adding a franchise whose span overlaps events it may not have felt.
---

# event-resonance

Decide, for one franchise, **which of the shared global events actually reached
this author's page** - and be able to say what each one meant to them.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md); the aura
editorial standard is its §6. Read `.claude/skills/world-events/SKILL.md`
first: that skill decides whether an event belongs in the catalogue at all,
this one whether it belongs on *your author*. They are different questions and
the second one has never been asked.

## Cheap tools before expensive habits (this stage pays for its own calls)

Every tool call re-sends your whole context, so what a stage costs is roughly
its context multiplied by how many calls it makes. One wing's editions stage
made 144 sequential fetches; the pages were not the expense, fetching them one
at a time was. Three habits, before you start:

- **Editions and visual-metadata: reach for `scripts/metadata/lookup.py` FIRST.**
  For those two stages the whole fetching half is already one tool call:
  `python scripts/metadata/lookup.py <slug> --author "<name>"` sweeps the
  registered providers and prints a TSV of edition and cover candidates for the
  entire wing (`--verify-isbns` checks an existing `editions.yaml`,
  `--check-covers` HEADs every cover, `--markets no,en,pt` widens the search,
  `--json` when something parses it). Measured on the Jo Nesbo wing it replaced
  ~360 sequential fetches (~880k tokens, 57 min) with ~40 HTTP requests inside
  one call. It does **not** replace the stage's judgement - which market, is
  this an omnibus, is this a title-page scan - and every real catch on the wings
  built so far was one of those, not a lookup. So run it, then judge the table.
  A source it does not cover yet is one provider class in
  `scripts/metadata/providers.py`; add it there rather than hand-fetching around
  it. The rest of this section still applies to the verification fetches the
  table sends you back for.
- **Every other stage: fetch in batches, not one by one.** `python scripts/fetch.py URL [URL...]`
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

## The problem this exists to fix

`reach: global` was being read as "every franchise renders this". It should mean
"any franchise *could*". The difference was visible and embarrassing:

> João Tordo was born in 1975. His page opened in **1910**, and walked the
> reader through the First and Second World Wars before reaching his first
> novel in 2004.

The events were correctly curated. They were simply being shown to an author
they could not possibly have touched.

## What the engine already does for free

**Do not spend judgement on arithmetic.** The app now filters global events to
the span of the authors' lifetimes: an event is the weather a writer wrote in,
and nobody wrote in weather that predates them. A dead author's window closes at
death; where a franchise has several authors, the window stays open while any of
them is living. That rule alone fixed the world wars for Tordo, Sanderson, King
and Pratchett, kept both wars for Christie, costs no curation, and never needs
re-running when a franchise is added.

**Your job is the residue: the events that overlap the author's life but may
still not belong, and the rare event outside it that does.**

## The test

For each candidate, try to write **one sentence saying what this event meant for
this author's work.** Not for the world. Not for literature. For these books.

- If the sentence is specific and true, the event stays.
- If you find yourself writing "this shaped the era in which they wrote", that
  is the sound of a sentence with nothing in it. Exclude.
- If the honest sentence is "they lived through it and it never reached the
  page", exclude. Living through something is not resonance.

This is the same admission test as the aura standard - *does it pass through the
author into the page?* - applied one author at a time.

### Worked example, and the live case

`financial-crisis-2008` currently renders on **every** franchise. The
`world-events` curation itself called it "the weakest entry in the file" and
graded it `low`, on the grounds that almost nothing in the catalogue answers it.
That is exactly the shape of an event that survives the arithmetic gate and
fails the resonance test nearly everywhere. Rule on it per author rather than
inheriting it by default.

Compare `carnation-revolution-1974`: decisive for a Portuguese author, texture
at best for the other five. Same event, different answer per franchise. That is
the whole point of this skill.

## The two directions, and the asymmetry between them

**Nothing renders unless you include it.** A wing's timeline carries a global
event if and only if that wing names it in `include`. There is no arithmetic
default: an event you never rule on is simply absent, and `exclude` gates
nothing at all.

**`exclude`** - considered and refused. It changes no output, so writing one is
not how you keep an event off a page: leaving it out of `include` already did
that. You write it so the next pass knows this ground was covered and does not
re-litigate it. The bar is low: if you cannot write the sentence, refuse it. An
absent event costs a reader nothing. A page cluttered with events that mean
nothing to this author teaches them that the aura is decoration, and then they
stop reading the ones that matter. **Clutter is not neutral, it is corrosive.**

**But "an absent event costs a reader nothing" assumes the timeline is
otherwise furnished.** On a wing whose aura is already thin it is false: the
reader gets a decade of books against blank ground, and your exclusions
helped build it. Run `python scripts/aura_density.py` first. Where the wing
has a dark run of five or more publishing years, an exclusion landing inside
that stretch needs a genuinely confident "this never reached the page" rather
than a shrug - and if the honest answer is that the wing is simply
under-researched, say so in the report and route it to `press-archaeology`,
whose material this really is. You prune the shared layer; you do not get to
leave a wing dark and call it restraint.

**`include`** - the operative list, and the only thing that puts a global event
on a page. The bar is high because every entry is a claim in the author's name.
An event inside the author's lifetime still has to earn its place here; living
through something is not writing out of it. Use it
when the event created the conditions the author's work exists inside and the
books show it. A real candidate: `fantasy-paperback-boom-1965` predates Brandon
Sanderson (born 1975), but it created the commercial category epic fantasy is
written into, and his career is unimaginable without it. Inheritance of that kind
is legitimate. "It was historically important" is not.

When you `include`, say in the note what the author does with the inheritance.

## Output

Write the decision into the **franchise's own file**, never into
`content/events/global.yaml`. The global file must stay franchise-agnostic; the
judgement belongs where the author knowledge is.

```yaml
# content/franchises/<slug>/franchise.yaml
globalEvents:
  include:
    - fantasy-paperback-boom-1965  # predates him; created the category he writes in
  exclude:
    - financial-crisis-2008     # lived through it; no book answers it
```

**Clear any `# inherited from the lifetime default, not yet ruled on` marker you
find.** Those entries were carried over mechanically when this layer moved from
opt-out to opt-in: they render today because the old arithmetic showed them, not
because anyone judged them. Ruling on one means either writing its real note or
moving it to `exclude`. A wing still carrying those markers has not been through
this stage, whatever its include count says.

Keep the note on the line short and specific. It is the evidence for a decision
a future curator will otherwise re-litigate from scratch.

## Hard rules

- **Never edit `global.yaml`.** Adding, removing or re-grading a shared event is
  the `world-events` skill's job and its bar is higher. If an event is wrong for
  *everyone*, say so in the PR and let that skill handle it.
- **Never fabricate a resonance** (CURATION §1). If you cannot evidence the
  link between the event and the work, there is no link.
- **Rule per author, not per franchise-shaped-guess.** A shared universe with
  two authors born 27 years apart does not have one answer.
- **Silence is absence, not a default.** An event you neither include nor
  exclude simply does not render. That is safe but undocumented, so record what
  you considered: an unexamined event and a deliberately refused one look
  identical in the file otherwise.
- **Do not use this to fix a bad event.** If an entry is badly written or
  wrongly graded, that is a `world-events` fix, not an exclusion list.

## Done means

A PR whose body lists, for this franchise: every global event **kept** with its
one-sentence resonance, every event **excluded** with the reason, every
**include** override with what the author does with the inheritance, and the
events left to the default. A run that excludes three events and keeps two,
with five sentences a reader would recognise as true, is a good run. A run
that keeps everything has not made a decision, it has just agreed with the
machine.
