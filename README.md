# Orrery content

The **canon content** for [Orrery](https://github.com/rfsbraz/orrery) (codename) - a contextual reading-order platform. This repo is the curated, version-controlled source of truth for everything the app renders as canon:

- **Franchises** - an author's world, a shared universe, or a series.
- **Works** - the bibliography (the abstract books; editions/covers are metadata).
- **Aura events** - the life, world, and cultural events (impact-weighted) that give each book its context. This is Orrery's whole point: contextual reading, not a checklist.
- **Eras** - creative periods that group the timeline.
- **Reading orders** - official, chronological/in-universe, author-recommended, and curated. (User- and community-created orders live in the app's database, not here - see below.)

It deliberately holds **no app code and no secrets**, so it can be opened to community contribution independently of the app.

## How this is made

**This is an AI-assisted project, and it says so up front.**

Reconstructing an author's complete bibliography, their life, the prizes and
losses and quarrels around the work, and the world events that reached them, is
a genuinely large amount of research. One wing runs to hundreds of dated,
sourced claims. Doing ten of them by hand is a multi-year job for a team that
does not exist here. Agents make it possible at all.

What that does **not** mean is that a model's output goes straight in.

- **Every claim carries a source in the file next to it.** Not a bibliography at
  the end, a citation on the entry. Anything about a living person's health,
  money, legal trouble or family needs two independent sources.
- **A human reads and approves every pull request.** Nothing is canon until a
  person merges it. That is the whole point of the gate, and it does not get
  skipped when the queue is long.
- **`scripts/validate.py` has to be green.** Schema, references, spoiler
  boundaries, asset rules, contrast floors. It is a real gate, and it fails
  builds.
- **The record is the audit.** Every change is a commit with a diff. If a fact
  is wrong you can see when it arrived, what it replaced, and what was cited for
  it.

We are also open about where the machinery fails, because that is more useful
than a reassurance. Agents working on this repo have attributed a tax dispute to
Agatha Christie from an article about Chris Christie, invented a birth date by
over-reading a lead, given a novelist a death that belonged to one of his
characters, and cited backlist sales figures traced to a dozen sites all quoting
each other. Every one was caught before merge, by the sourcing rules, the
validator or a human reading the diff. That is what the gates are for.
[`docs/TOOLING.md`](docs/TOOLING.md) documents the failure modes in full.

### The data belongs to nobody

Everything under `content/` is **[CC0 1.0](LICENSE)**: a full waiver of
copyright and of the EU database right. Take it, fork it, sell it, build on it.
No permission, no attribution, no conditions.

Facts about books are not ours to own, and assembling them in the open means the
work only has to be done once. Portraits, cover images and contributed art are
third-party works with their own credits and are not covered by the waiver, see
[`LICENSE-NOTICE.md`](LICENSE-NOTICE.md).

### Use the tools, or don't

The agents and scripts that built this are in the repo:
`.claude/skills/` and `scripts/`. **You are welcome to use them for your own
contributions**, and equally welcome to write YAML by hand and never touch them.
Both arrive at the same place: a pull request a human reads.

Being open about your method is not a mark against a contribution here. A PR
saying "drafted with an agent, I verified the dates against these two sources,
and I dropped the prize year because I could not confirm it" is a good PR.

See [`docs/TOOLING.md`](docs/TOOLING.md).

### About the art

The illustrations are generated, and they are placeholders with no seniority.

**Human art always wins.** If you draw something that fits a moment on a
timeline, or know of public-domain or openly-licensed work that does, open an
issue with the `art:human-offer` label. It replaces the generated image, it
carries your name in the credit, and the generated file is deleted rather than
kept as an alternative. That holds even when the generated one is decent and the
wing looks finished.

The images exist because a few hundred illustrations could not be commissioned,
not because generation is the preferred outcome. The rule is written down in
[`docs/VISUAL.md`](docs/VISUAL.md) §1b so it survives us being busy.

## Why a separate repo

Content is curated on a different cadence, by different people (eventually community curators), than the app is built. Splitting it means content PRs never touch app code, content gets its own review and schema validation, and the "contribute a reading order" flow is a clean, low-barrier pull request.

## Layout

```
content/
  authors/
    <author-slug>.yaml          # GLOBAL author entities: bio, pseudonyms, life events
  events/
    global.yaml                 # world/culture events shared across all franchises (reach: global)
  franchises/
    <franchise-slug>/
      franchise.yaml            # identity + features (capabilities) + startHere paths
      works.yaml                # bibliography, with STABLE ids: <franchise-slug>/<work-slug>
      eras.yaml                 # creative-period groupings
      events.yaml               # franchise-specific events
      orders.yaml               # additional canon reading orders (the default is derived)
      characters.yaml           # optional: recurring/crossover figures
      editions.yaml             # optional: verified concrete editions (ISBNs, covers)
      theme.yaml                # branding preset (see Orrery CONCEPT §6)
```

## Curation skills

Authored Claude Code skills under `.claude/skills/`, each with its own rules:

- **`franchise-research`** - research an author or universe and emit the whole content bundle.
- **`world-events`** - curate the shared global aura layer, keeping it sparse and impact-weighted (a global event renders on every franchise's timeline, so its bar is much higher). Graded against `scripts/event_density.py`.
- **`press-archaeology`** - dig contemporary press, interviews, obituaries and prize coverage for the dated, sourced facts a bibliography cannot hold, and for corrections to received wisdom. Strict sourcing (two independent sources for anything about a living person's health, finances or legal trouble) and a hard density budget.
- **`completeness-auditor`** - audit a bibliography against primary sources for missing works, wrong first-publication dates, and inconsistent tiering.
- **`visual-metadata`** - source author portraits, franchise headers and covers with rights discipline and mandatory credits.
- **`spoiler-audit`** - place `spoilerAfter` boundaries, preferring a rewrite that needs no boundary over a redaction.
- **`event-resonance`** - decide which shared global events actually reached a specific author, and why. The engine gates them to the author's lifetime for free; this skill rules on the residue.
- **`reading-orders`** - author, audit and keep honest the additional reading orders; the default publication order is derived, never hand-written.
- **`eras`** - creative periods taken from critic, author or community consensus. Fewer, or none, beats coined.
- **`editions`** - verified buyable editions: ISBN discipline, region-strict language codes, honest coverage.
- **`translation`** - locale overlays: prose only, region-strict, with the traps that shipped green CI written down.
- **`visual-language`** - settle a wing's `theme.art`: the motifs, line character and emblem every drawing for that author must obey. Gates all asset generation.
- **`whats-new`** - read-only: what changed in the world since a wing was last curated, and which stages that routes to.
- **`wing-audit`** - the final critic. The seams no single agent sees, plus the content types no other skill owns.

### Completing a whole author

The **[`/author`](.claude/commands/author.md)** command runs
all of the above in dependency order, with the gates between them. Order is not
cosmetic: stages that write the same file must not run in parallel, completeness
must settle the work list before anything annotates works, and the spoiler audit
must run before translation so a spoiler is not fixed twice in two languages.

The **full schema reference is [`docs/SCHEMA.md`](docs/SCHEMA.md)** - field by field, including the capabilities model (which app features a franchise's data activates). The authoring guide and assisted-research tool is the **`franchise-research` skill** at [`.claude/skills/franchise-research/SKILL.md`](.claude/skills/franchise-research/SKILL.md).

**The schema is a framework.** Every advanced layer (aura, characters, connections, editions, start-here paths) is optional per franchise; the app detects what a bundle provides and lights up the matching features. A works-list-only franchise is complete and correct.

## Hard rules (also enforced in review)

- **Never fabricate.** Every non-obvious claim - a date, an order, an event - carries a source. When unsure, mark `confidence: low` and leave a note rather than guessing. Especially for thinly-documented authors (e.g. João Tordo).
- **Work IDs are permanent.** `id: <franchise-slug>/<work-slug>` is referenced by user data in the app database; renaming one orphans that data. Choose slugs deliberately, never change them.
- **Global vs franchise events.** Shared world/culture events go in `events/global.yaml` with `reach: global`; author-life and franchise-specific events stay in the franchise.
- **Tag spoilers.** Anything that could spoil a book carries a `spoilerAfter:` boundary.

## How the app consumes this

The app does **not** read these files at runtime. A sync step (at deploy / in CI) validates the content and **upserts it into Supabase** (`works`, `editions`, `events`, and `reading_orders` where `source = 'canon'`). At runtime the app queries Supabase, so canon orders and user/community orders sit in the same table and query identically - the stable Work IDs here are what user orders reference. See Orrery `docs/CONCEPT.md` §4a.

## Status

Live at [orrery.homeberry.me](https://orrery.homeberry.me). **Ten wings, 483 works, 31 authors**, full pt-PT locale coverage.

Agatha Christie, Stephen King, Terry Pratchett, Robert Jordan, Brandon Sanderson, Chuck Palahniuk, Gillian Flynn, and three Portuguese wings (Valter Hugo Mãe, José Luís Peixoto, João Tordo) which are the sparse-metadata stress case.

A wing is an author and spans their complete works; shared universes are subseries inside it, which is why the Cosmere, the Discworld and the Wheel of Time live under the writers who made them.
