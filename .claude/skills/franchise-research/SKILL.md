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

## Process

1. **Scope the franchise.** Confirm what it is (single-author series, shared universe, multi-author), its boundaries, and its `canonTier` conventions (what counts as core vs extended vs apocrypha - completionists care). Pick the `<franchise-slug>`.
2. **Author(s).** Biography and a timeline of **life events** with dates and impact - the raw material of the aura. For multi-author franchises (e.g. Wheel of Time: Jordan → Sanderson) capture each, and the transition itself is usually a high-impact event.
3. **Bibliography → works.** Every work: title, publication date, subseries, canon tier, synopsis, external IDs (OpenLibrary/Google Books/Wikidata where findable). Assign stable IDs.
4. **World & culture events.** For the span the franchise covers, gather notable world/cultural/industry events. Global ones → `global.yaml`; ones specifically resonant with this franchise → franchise `events.yaml`. Impact-weight everything.
5. **Eras.** Group the timeline into named eras (creative periods) with themes and a short characterization - the narrative spine of the aura.
6. **Known reading orders.** Find the established orders: publication, chronological/in-universe, author-recommended, and notable community/curated ones (with their rationale and where they diverge). These become `source: canon` orders; note debated points.
7. **Emit YAML** to `content/franchises/<slug>/` per the schema below, plus any `global.yaml` additions. Summarize gaps and low-confidence items for the curator.

## Output schema

```
content/
  events/
    global.yaml                      # shared world/culture events (reach: global)
  franchises/
    <franchise-slug>/
      franchise.yaml
      authors.yaml
      works.yaml
      eras.yaml
      events.yaml                    # franchise-specific + author-life events
      orders.yaml
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

**authors.yaml**
```yaml
- id: stephen-king
  name: Stephen King
  born: 1947-09-21
  bio: >
    Short factual bio.
  sources: [https://...]
```

**works.yaml**
```yaml
- id: stephen-king/carrie          # STABLE - never change
  title: Carrie
  authorIds: [stephen-king]
  published: 1974-04-05
  subseries: null                  # e.g. "The Dark Tower" / "Mistborn: Era 1"
  canonTier: core                  # core | extended | apocrypha
  synopsis: >
    Spoiler-free premise.
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

**orders.yaml**
```yaml
- id: stephen-king/publication
  name: Publication order
  type: official-publication       # see CONCEPT §4 for the type list
  source: canon
  rationale: >
    Why a reader might choose this order.
  orderedWorkIds:
    - stephen-king/carrie
    - stephen-king/salems-lot
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
