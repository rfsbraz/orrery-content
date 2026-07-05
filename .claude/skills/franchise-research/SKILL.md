---
name: franchise-research
description: Research a book franchise or author for Orrery and emit the git content bundle - author profile + life events, bibliography (works), eras, world/culture events, and known reading orders - as YAML for curator review. Use when adding or refreshing a franchise's canon content in content/franchises/<slug>/.
---

# franchise-research

Research one franchise (an author's world, a shared universe, or a series) and produce the **canon content bundle** Orrery renders: who wrote it and what was happening around them (the "aura"), the full bibliography, the eras that group it, and the known reading orders. Output is git YAML under `content/franchises/<slug>/`, reviewed by a curator via PR before it becomes canon.

Read `docs/CONCEPT.md` first if unfamiliar - especially §4 (data model), §4a (canon vs user content), and §9 (spoilers).

## The DNA: aura over checklist

Orrery is not a reading-order list; it's contextual reading. The value is situating each book in its moment. So research is not just "list the books in order" - it's **capturing the life, world, and cultural weather around each book** so the timeline breathes. Weight events by impact (an author's near-fatal accident vs a minor award) so the timeline has anchors and texture.

## Hard rules

- **Never fabricate.** Books, dates, orders, and events must be verifiable. Cite a source URL per non-obvious claim. When unsure, mark `confidence: low` and leave a `note:` - do not invent. This matters most for sparse authors (e.g. João Tordo: Portuguese literary fiction has thin English coverage - expect gaps and flag them rather than guessing bibliography or order structure).
- **Stable Work IDs are permanent.** Assign each work `id: <franchise-slug>/<work-slug>` and never change it later - user data references these (§4a). Choose slugs carefully the first time.
- **Separate global from franchise-specific events.** World/culture events that any franchise could share (a war, a cultural rupture, a tech shift) go to `content/events/global.yaml` with `reach: global`. Author-life and franchise-specific events stay in the franchise's `events.yaml`.
- **Tag spoilers.** Any event or note that could spoil a book carries a `spoilerAfter:` boundary (the work ID beyond which it's safe to reveal), per §9.
- **Editions vs Works.** Research at the Work level (the abstract book) for orders; capture ISBN/cover/edition detail separately. Orders reference Works only.
- **Aim for a complete bibliography.** The franchise's **default order is publication-chronological over ALL published works** and is *derived* from the works list (not hand-written). So `works.yaml` completeness is the goal - novels, collections, novellas, nonfiction. Do not author the default/publication order by hand; `orders.yaml` holds only the *additional* orders (in-universe, author-recommended, curated).
- **Pen names.** Record pen names on the author (`pseudonyms`) and set `publishedAs` on each work published under one. Pen-name works stay in the author's franchise and appear in the default order. A pen name only gets its own franchise if it's a genuinely distinct brand/persona (curator's call). Meta pen-name lore (a staged "death", a reveal) goes in `events`, not as a data hack.
- **Reference by ID, never by name.** Authors are **global entities** in `content/authors/<slug>.yaml` (so the same person resolves across franchises and past name collisions). Franchises and works reference `authorIds` / `withAuthorIds`. Author-**life** events live on the author entity (`lifeEvents`); franchise `events.yaml` holds only franchise-specific events. In prose (bios, synopses, event/era descriptions, order rationales) link with `[[work:<id>|text]]` and `[[author:<id>|text]]`. Every reference must resolve - `scripts/validate.py` (run in CI) fails the build on dangling ones. Disambiguate name collisions at the slug; add `aka:` for search.

## Process

1. **Scope the franchise.** Confirm what it is (single-author series, shared universe, multi-author), its boundaries, and its `canonTier` conventions (what counts as core vs extended vs apocrypha - completionists care). Pick the `<franchise-slug>`.
2. **Author(s).** Biography and a timeline of **life events** with dates and impact - the raw material of the aura. For multi-author franchises (e.g. Wheel of Time: Jordan → Sanderson) capture each, and the transition itself is usually a high-impact event.
3. **Bibliography → works.** Every published work - aim for completeness (the default order derives from this): title, publication date, subseries, canon tier, synopsis, `publishedAs` for pen names, `withAuthors` for collaborations, external IDs (OpenLibrary/Google Books/Wikidata where findable). Assign stable IDs.
4. **World & culture events.** For the span the franchise covers, gather notable world/cultural/industry events. Global ones → `global.yaml`; ones specifically resonant with this franchise → franchise `events.yaml`. Impact-weight everything.
5. **Eras.** Group the timeline into named eras (creative periods) with themes and a short characterization - the narrative spine of the aura.
6. **Known reading orders.** The default publication-chronological order is derived automatically - don't write it. Find the *additional* established orders: chronological/in-universe, author-recommended, and notable community/curated ones (with their rationale and where they diverge). These become `source: canon` orders in `orders.yaml`; note debated points.
7. **Emit YAML** to `content/franchises/<slug>/` per the schema below, plus any `global.yaml` additions. Summarize gaps and low-confidence items for the curator.

## Output schema

```
content/
  authors/
    <author-slug>.yaml               # GLOBAL author entity: bio, pseudonyms, lifeEvents
  events/
    global.yaml                      # shared world/culture events (reach: global)
  franchises/
    <franchise-slug>/
      franchise.yaml                 # references authorIds
      works.yaml
      eras.yaml
      events.yaml                    # franchise-specific events only
      orders.yaml                    # additional orders (default is derived)
      theme.yaml                     # branding preset (see CONCEPT §6)
```

**franchise.yaml**
```yaml
id: stephen-king
name: Stephen King
kind: author            # author | shared-universe | series
description: >
  One-line essence.
authorIds: [stephen-king]
themePreset: pulp-horror
```

**content/authors/&lt;slug&gt;.yaml** (one global file per author)
```yaml
id: stephen-king                   # global, stable; referenced by authorIds everywhere
name: Stephen King
aka: ["Steve King"]                # optional alternate names, for search
born: 1947-09-21
bio: >
  Short factual bio, may use [[work:...|links]].
pseudonyms:                        # optional; the person, published under other names
  - name: Richard Bachman
    note: When/why used; how it was revealed.
lifeEvents:                        # author-life events live here, not in the franchise
  - id: king-van-accident-1999
    date: 1999-06-19
    title: Near-fatal roadside accident
    impact: high                   # low | med | high
    description: >
      What happened and how it colors the work around it.
    spoilerAfter: null             # or a work id
    sources: [https://...]
sources: [https://...]
```

**works.yaml**
```yaml
- id: stephen-king/carrie          # STABLE - never change
  title: Carrie
  authorIds: [stephen-king]
  published: 1974                  # year-precision is fine; full dates when confident
  subseries: null                  # e.g. "The Dark Tower" / "Mistborn: Era 1"
  canonTier: core                  # core | extended | apocrypha
  publishedAs: "Richard Bachman"   # optional; only when the cover name differs
  withAuthorIds: [peter-straub]    # optional; collaborator author ids (must exist)
  synopsis: >
    Spoiler-free premise. May use [[work:...|links]].
  externalIds:
    openLibrary: OL...W
    googleBooks: ...
    wikidata: Q...
  sources: [https://...]
```

**eras.yaml**
```yaml
- id: birth-of-the-master
  title: Birth of the Master
  period: "1974-1979"
  themes: [small-town horror, supernatural powers]
  description: >
    What defined this creative period.
```

**events.yaml** (franchise-specific + author-life)
```yaml
- id: king-car-accident-1999
  date: 1999-06-19
  title: Near-fatal car accident
  scope: author-life               # author-life | world | culture | industry
  reach: franchise                 # franchise (here) | global (put in global.yaml)
  impact: high                     # low | med | high
  description: >
    What happened and how it colors the work around it.
  spoilerAfter: null               # or a work id, per CONCEPT §9
  sources: [https://...]
```

**global.yaml** (shared across all franchises)
```yaml
- id: sept-11-2001
  date: 2001-09-11
  title: September 11 attacks
  scope: world
  reach: global
  impact: high
  description: >
    Neutral, franchise-agnostic summary.
  sources: [https://...]
```

**orders.yaml** — additional orders only. The default publication-chronological / all-works order is derived from `works.yaml`; do NOT list it here.
```yaml
- id: stephen-king/dark-tower-connected
  name: The Dark Tower - connected reading order
  type: curated                    # chronological-inuniverse | author-recommended | curated | community
  source: canon
  rationale: >
    Why a reader might choose this order over the default.
  orderedWorkIds:
    - stephen-king/the-gunslinger
    - stephen-king/the-drawing-of-the-three
  debated: []                      # note contested placements
  sources: [https://...]
```

**theme.yaml** (see CONCEPT §6 - a preset a curator can tweak)
```yaml
preset: pulp-horror
palette: { bg: "#...", accent: "#...", ink: "#..." }
typePairing: { display: "...", body: "..." }
motif: 80s-paperback-grain
```

## Done means

A reviewable PR: the franchise's files populated, global events appended (not duplicated), every non-obvious claim sourced, low-confidence/gap items called out for the curator, and stable IDs assigned deliberately. Canon is only canon after a curator merges it.
