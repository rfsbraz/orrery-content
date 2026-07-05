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
  events/
    global.yaml                 # world/culture events shared across all franchises (reach: global)
  franchises/
    <franchise-slug>/
      franchise.yaml            # identity + theme preset
      authors.yaml              # author(s) + bios
      works.yaml                # bibliography, with STABLE ids: <franchise-slug>/<work-slug>
      eras.yaml                 # creative-period groupings
      events.yaml               # author-life + franchise-specific events
      orders.yaml               # canon reading orders
      theme.yaml                # branding preset (see Orrery CONCEPT §6)
```

The full schema and authoring rules live in the **`franchise-research` skill** at [`.claude/skills/franchise-research/SKILL.md`](.claude/skills/franchise-research/SKILL.md) - it's both the human contribution guide and the assisted-research tool that drafts a franchise bundle for review.

## Hard rules (also enforced in review)

- **Never fabricate.** Every non-obvious claim - a date, an order, an event - carries a source. When unsure, mark `confidence: low` and leave a note rather than guessing. Especially for thinly-documented authors (e.g. João Tordo).
- **Work IDs are permanent.** `id: <franchise-slug>/<work-slug>` is referenced by user data in the app database; renaming one orphans that data. Choose slugs deliberately, never change them.
- **Global vs franchise events.** Shared world/culture events go in `events/global.yaml` with `reach: global`; author-life and franchise-specific events stay in the franchise.
- **Tag spoilers.** Anything that could spoil a book carries a `spoilerAfter:` boundary.

## How the app consumes this

The app does **not** read these files at runtime. A sync step (at deploy / in CI) validates the content and **upserts it into Supabase** (`works`, `editions`, `events`, and `reading_orders` where `source = 'canon'`). At runtime the app queries Supabase, so canon orders and user/community orders sit in the same table and query identically - the stable Work IDs here are what user orders reference. See Orrery `docs/CONCEPT.md` §4a.

## Status

Pre-implementation. No franchises yet. First run: `franchise-research` on Stephen King (prototype data exists to check against).
