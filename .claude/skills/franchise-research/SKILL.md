---
name: franchise-research
description: Research a book franchise or author for Orrery and emit the git content bundle - author profile + life events, bibliography (works), eras, world/culture events, and known reading orders - as YAML for curator review. Use when adding or refreshing a franchise's canon content in content/franchises/<slug>/.
---

# franchise-research

Research one franchise (an author's world, a shared universe, or a series) and produce the **canon content bundle** Orrery renders: who wrote it and what was happening around them (the "aura"), the full bibliography, the eras that group it, the known reading orders, and - where the franchise earns them - the recurring characters, work connections, and "where to start" paths. Output is git YAML under `content/franchises/<slug>/`, reviewed by a curator via PR before it becomes canon.

**The schema reference is [`docs/SCHEMA.md`](../../../docs/SCHEMA.md) - read it in full before writing YAML.** The examples below are abbreviated; SCHEMA.md is authoritative and `scripts/validate.py` enforces it. Also read the app's `docs/CONCEPT.md` if unfamiliar - especially §4 (data model), §4a (canon vs user content), and §9 (spoilers).

## The framework mindset

Orrery is a framework: **every advanced layer is optional, and the app activates features per franchise based on what the data provides** (the capabilities table in SCHEMA.md). Your job is to judge which layers this franchise *earns*, not to fill every file:

- A sprawling multiverse (King, Cosmere) earns `characters.yaml`, `connections`, and a rich aura.
- A near-linear series (Wheel of Time) may need few connections but a strong aura (the author transition) and a `startHere` with the prequel debate addressed.
- A sparse or non-English author (João Tordo) may ship works + eras + a thin aura and nothing else - that is a *complete, correct* bundle, not a failure. Never pad a layer to make the franchise look fuller; empty is better than invented.

State in your PR description which capabilities the bundle activates and why.

## The DNA: aura over checklist

Orrery is not a reading-order list; it's contextual reading. The value is situating each book in its moment. So research is not just "list the books in order" - it's **capturing the life, world, and cultural weather around each book** so the timeline breathes. Weight events by impact (an author's near-fatal accident vs a minor award) so the timeline has anchors and texture.

## The aura editorial standard

The admission test for every event: **does it pass through the author into the
page?** An event earns its slot only if knowing it changes how a reader reads.
The impact taxonomy, in editorial terms:

- **high = recolors the text.** After learning it, the same sentences read
  differently.
- **med = explains the shelf.** Why the catalog is shaped the way it is.
- **low = texture of the times.** The weather, kept sparse.
- Fails all three -> it does not ship. Every noise event cheapens the real
  anchors (the app renders high-impact events as page-breaking interruptions;
  imagine each one breaking the page and ask if it deserves to).

What readers actually want to know, ranked by how much it changes the reading:

1. **The author's inner weather - the gold tier.** Illness, addiction, grief,
   sobriety, fear, recovery. This is where the aura earns its existence:
   King barely remembering writing one of his own novels; Pratchett's
   embuggerance not as context for late Discworld but AS late Discworld;
   Jordan's amyloidosis being the entire meaning of the final volumes. Most
   high-impact slots should come from this tier. Write it with care - factual,
   humane, never ghoulish.
2. **Why this book exists - origin stories.** The manuscript rescued from the
   bin, the ending written years early and vaulted, the pen name invented
   because publishers capped output. Readers retell these at dinner; they are
   the aura's most shareable material.
3. **World events - rarely, but decisively.** Only where the book ANSWERS the
   event: dispensary work that became a poisoner's expertise, biowarfare
   headlines that became a plague novel, a pandemic the author actually wrote
   into the books. Generic history is filler - roughly one world event in
   twenty is aura-worthy. Keep `global.yaml` thin and mostly low/med; a war
   the author merely lived near is not an anchor on their timeline.
4. **Feuds and reception ruptures - with one filter: did it leave a mark on
   the canon?** An unmasked pseudonym answered with a novel, an author pulling
   a book from print, a twist that scandalized the genre's rule-keepers, an
   establishment snub that reframed a career - all belong. Gossip with no
   fingerprint on the work does not.
5. **Industry context - the completionist's tier.** The publishing forces
   that shaped the shelf (format booms, output rules, estate decisions about
   what "complete" means). Medium impact at most, never anchors.
6. **Trivia - the cut tier.** Awards lists, sales milestones, pub-quiz facts:
   cut, unless the item relocates the reader inside a book (the real hotel
   behind the fictional one), in which case it is really tier 1 or 2 in
   disguise.

## Hard rules

- **Never fabricate.** Books, dates, orders, and events must be verifiable. Cite a source URL per non-obvious claim. When unsure, mark `confidence: low` and leave a `note:` - do not invent. This matters most for sparse authors (e.g. João Tordo: Portuguese literary fiction has thin English coverage - expect gaps and flag them rather than guessing bibliography or order structure).
- **Stable Work IDs are permanent.** Assign each work `id: <franchise-slug>/<work-slug>` and never change it later - user data references these (§4a). Choose slugs carefully the first time.
- **Separate global from franchise-specific events.** World/culture events that any franchise could share (a war, a cultural rupture, a tech shift) go to `content/events/global.yaml` with `reach: global`. Author-life and franchise-specific events stay in the franchise's `events.yaml`.
- **Tag spoilers.** Any event or note that could spoil a book carries a `spoilerAfter:` boundary (the work ID beyond which it's safe to reveal), per §9.
- **Editions vs Works.** Research at the Work level (the abstract book) for orders; capture ISBN/cover/edition detail separately. Orders reference Works only.
- **Aim for a complete bibliography.** The franchise's **default order is publication-chronological over ALL published works** and is *derived* from the works list (not hand-written). So `works.yaml` completeness is the goal - novels, collections, novellas, nonfiction. Do not author the default/publication order by hand; `orders.yaml` holds only the *additional* orders (in-universe, author-recommended, curated).
- **Pen names.** Record pen names on the author (`pseudonyms`) and set `publishedAs` on each work published under one. Pen-name works stay in the author's franchise and appear in the default order. A pen name only gets its own franchise if it's a genuinely distinct brand/persona (curator's call). Meta pen-name lore (a staged "death", a reveal) goes in `events`, not as a data hack.
- **Reference by ID, never by name.** Authors are **global entities** in `content/authors/<slug>.yaml` (so the same person resolves across franchises and past name collisions). Franchises and works reference `authorIds` / `withAuthorIds`. Author-**life** events live on the author entity (`lifeEvents`); franchise `events.yaml` holds only franchise-specific events. In prose (bios, synopses, event/era descriptions, order rationales) link with `[[work:<id>|text]]`, `[[author:<id>|text]]`, and `[[character:<id>|text]]`. Every reference must resolve - `scripts/validate.py` (run in CI) fails the build on dangling ones. Disambiguate name collisions at the slug; add `aka:` for search.
- **Characters are connective tissue, not a wiki.** Add `characters.yaml` only for figures whose recurrence across works is part of how the franchise hangs together. An appearance whose *existence* is a reveal gets `spoilerAfter` on that appearance.
- **Connections are declared on the later work**, pointing back at the earlier one (the later work is the one whose reading is enriched); the app renders the edge both ways. Do not duplicate what `subseries` already threads - connections are for crossovers, sequels across subseries, and shared-cosmology links.
- **startHere paths are curation, not marketing.** Each path must be an entry strategy a real community actually recommends (cite it), tagged honestly with who it fits. Two to five paths; always include a completionist path (usually `orderId: default`).
- **Editions only when verifiable.** Never guess an ISBN. It is fine (normal) to ship no `editions.yaml`; the app falls back to search links and OpenLibrary covers.
- **Achievements are content, not app code.** A franchise may ship its own badges in `achievements.yaml` (ids prefixed `<slug>/`), using the criteria kinds in `docs/SCHEMA.md`. Tie at least one to the aura where the franchise supports it (an era, a signature order) - those are badges only Orrery can offer. Never invent a criteria kind; if a badge needs one, say so in the PR instead.
- **Theming is content too.** `theme.yaml`'s `palette`, `displayFace` (curated set), and `signature` (`beam`/`thread`/`rule`/`none`) are all honored by the app - pick them deliberately per the design law, and never assume another franchise's look is the default.

## Process

1. **Scope the franchise.** Confirm what it is (single-author series, shared universe, multi-author), its boundaries, and its `canonTier` conventions (what counts as core vs extended vs apocrypha - completionists care). Pick the `<franchise-slug>`.
2. **Author(s).** Biography and a timeline of **life events** with dates and impact - the raw material of the aura. For multi-author franchises (e.g. Wheel of Time: Jordan → Sanderson) capture each, and the transition itself is usually a high-impact event.
3. **Bibliography → works.** Every published work - aim for completeness (the default order derives from this): title, publication date, subseries, canon tier, synopsis, `publishedAs` for pen names, `withAuthorIds` for collaborations. Assign stable IDs. **You can leave `externalIds` empty** - the enrichment bot (`scripts/enrich.py`, run by the Enrich CI) fills `openLibrary` IDs from high-confidence matches and opens a PR, flagging anything uncertain for a human.
4. **World & culture events.** For the span the franchise covers, gather the world/cultural/industry events that pass the editorial standard (the book must answer the event - see "The aura editorial standard"). Global ones → `global.yaml`; ones specifically resonant with this franchise → franchise `events.yaml`. Impact-weight everything; expect to reject most candidates.
5. **Eras.** Group the timeline into named eras (creative periods) with themes and a short characterization - the narrative spine of the aura.
6. **Known reading orders.** The default publication-chronological order is derived automatically - don't write it. Find the *additional* established orders: chronological/in-universe, author-recommended, and notable community/curated ones (with their rationale and where they diverge). These become `source: canon` orders in `orders.yaml`; note debated points.
7. **Emit YAML** to `content/franchises/<slug>/` per the schema below, plus any `global.yaml` additions. Summarize gaps and low-confidence items for the curator.

## Output schema

Abbreviated tree; **full field-by-field reference in `docs/SCHEMA.md`.**

```
content/
  authors/
    <author-slug>.yaml               # GLOBAL author entity: bio, pseudonyms, lifeEvents
  events/
    global.yaml                      # shared world/culture events (reach: global)
  achievements.yaml                  # global, franchise-agnostic badges
  franchises/
    <franchise-slug>/
      franchise.yaml                 # identity + features + startHere
      works.yaml                     # required; connections live on works
      eras.yaml
      events.yaml                    # franchise-specific events only
      orders.yaml                    # additional orders (default is derived)
      characters.yaml                # optional; recurring/crossover figures
      editions.yaml                  # optional; verified ISBNs only
      achievements.yaml              # optional; this wing's badges (data, not code)
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

## Field notes for research agents

Hard-won lessons from bundles already shipped (Stephen King was the first).
Read these before starting; they are the difference between a mergeable PR and
a rewrite.

1. **Slug the works before writing anything else.** Every file cross-references
   work IDs, and IDs are immutable once merged. Draft the complete
   `works.yaml` ID list first, sanity-check the slugs (lowercase, hyphenated,
   drop leading articles only when the community does: `the-stand` keeps its
   "the"; be consistent within the franchise), then write orders/events/
   characters against that list. Renaming a slug halfway through poisons every
   file you already wrote.
2. **Completeness beats depth in works.yaml.** The default order derives from
   it, so a missing work is a hole in the franchise's spine. A work entry with
   just id/title/authorIds/published/canonTier and a one-line synopsis is fine;
   you can skip externalIds entirely (the enrichment bot fills OpenLibrary IDs
   and flags uncertain matches for humans). Novels, collections, novellas,
   relevant nonfiction - all of it, each tiered honestly (core / extended /
   apocrypha).
3. **Year-precision dates are fine.** `published: 1987` is better than a
   wrong full date. Use full dates only when a source states one.
4. **The aura needs anchors, not volume.** Ten well-chosen impact-weighted
   events beat forty trivia items. Apply "The aura editorial standard" above
   to every entry: high = recolors the text, med = explains the shelf, low =
   texture of the times, and an event that fails all three does not ship.
   Source events from the ranked tiers (inner weather first, origin stories
   second, world events only where the book answers them, feuds only with a
   mark on the canon). Award seasons are usually not worth an entry at all.
5. **Global vs franchise events: default to franchise.** Only push an event to
   `events/global.yaml` when it is genuinely author-agnostic (a war, a
   pandemic, a publishing-industry shift) AND likely to matter to several
   franchises. Check global.yaml for an existing entry before adding; append at
   the end and never edit others' entries (parallel franchise PRs merge into
   this file, keep your diff append-only).
6. **Non-English and sparse authors: flag, never fill.** For authors with thin
   English-language coverage (the João Tordo case), prefer primary sources in
   the original language (publisher pages, the author's own site, national
   press). Where the record is ambiguous (reissues vs first editions, series
   membership), record what you can verify and leave a `note:` calling out the
   gap. A visibly incomplete bundle with honest notes is mergeable; a plausible
   guess is not.
7. **Portugal-market awareness.** For Portuguese authors, capture the original
   Portuguese titles as canonical `title` values, note translations in the
   synopsis or a `note:`, and expect store coverage via Wook/Bertrand/FNAC
   rather than Amazon. Keep prose in English (the app's UI language) but never
   translate a title that has no published translation.
8. **Orders need receipts.** Every non-derived order must cite where it comes
   from (the author's own site, a canonical community guide, a publisher page).
   Capture the *debate* in `debated:` - contested placements are completionist
   value, not noise. Do not invent a "curated" order yourself; you are
   researching orders that exist.
9. **Spoiler boundaries: pick the damaged work.** `spoilerAfter` is the work
   whose *experience the detail damages* - usually the book where the reveal
   lands, not where the referenced thing first appeared (Father Callahan's
   Dark Tower reappearance is `spoilerAfter: wolves-of-the-calla`, not
   `salems-lot`).
10. **Theme: follow the design law.** CONCEPT §6 is non-negotiable - palette +
    one modern display face + one signature element, readability first, no
    genre costume. Look at `stephen-king/theme.yaml` for the calibration
    ("literary-noir", the Beam). Propose; a curator tunes.
11. **Validate before you finish.** Run `python scripts/validate.py` locally
    and fix every error. A PR that fails CI on dangling references was not
    finished.
    YAML gotcha that has bitten a real bundle: **URLs with query strings break
    flow sequences** - in `sources: [https://site.com/page?x=y]` the `?`
    parses as a mapping-key indicator. Quote every URL in a flow sequence
    (`sources: ["https://site.com/page?x=y"]`) or use block-style lists.
12. **Your PR description is part of the deliverable.** List: capabilities the
    bundle activates, coverage gaps, low-confidence items, contested decisions
    you made (slugging, tiering, franchise boundaries), and sources you leaned
    on hardest. The curator reviews your judgment, not just your YAML.

## Done means

A reviewable PR: the franchise's files populated, global events appended (not duplicated), every non-obvious claim sourced, low-confidence/gap items called out for the curator, and stable IDs assigned deliberately. Canon is only canon after a curator merges it.
