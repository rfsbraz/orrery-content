# Orrery content

The **canon content** for [Orrery](https://github.com/rfsbraz/orrery) (codename) - a contextual reading-order platform. This repo is the curated, version-controlled source of truth for everything the app renders as canon:

- **Franchises** - an author's world, a shared universe, or a series.
- **Works** - the bibliography (the abstract books; editions/covers are metadata).
- **Aura events** - the life, world, and cultural events (impact-weighted) that give each book its context. This is Orrery's whole point: contextual reading, not a checklist.
- **Eras** - creative periods that group the timeline.
- **Reading orders** - official, chronological/in-universe, author-recommended, and curated. (User- and community-created orders live in the app's database, not here - see below.)

It deliberately holds **no app code and no secrets**, so it can be opened to community contribution independently of the app.

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

### Completing a whole author

The **[`/complete-author`](.claude/commands/complete-author.md)** command runs
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

Live. First franchise: **Stephen King** (77 works, 4 authors, curated orders, aura, characters, start-here paths). Next wave in progress: Discworld, the Cosmere, The Wheel of Time, Agatha Christie, and João Tordo (the Portuguese-market and sparse-metadata stress case).
