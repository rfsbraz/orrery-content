# Orrery content schema (v2)

The canonical reference for everything under `content/`. The app (`rfsbraz/orrery`)
renders exactly what is described here; `scripts/validate.py` enforces it in CI.
The `franchise-research` skill teaches agents how to *fill* this schema; this file
defines *what it is*.

Two principles frame all of it:

1. **IDs are the source of truth; names are display-only.** Work IDs
   (`<franchise-slug>/<work-slug>`), author IDs, and character IDs are immutable
   forever. User data references them, so renaming one orphans real people's
   shelves. Nothing resolves by name.
2. **The schema is a framework, not a mandate.** Every advanced layer
   (aura events, eras, characters, connections, editions, start-here paths) is
   optional. The app detects what a franchise provides and lights up the matching
   features (its *capabilities*, see below). A sparse franchise with just a works
   list is a first-class citizen: it gets the derived publication order and a
   clean museum page, nothing broken, nothing half-empty.

## Directory layout

```
content/
  authors/
    <author-slug>.yaml          # GLOBAL author entities (bio, pseudonyms, lifeEvents)
  events/
    global.yaml                 # shared world/culture events (reach: global)
  franchises/
    <franchise-slug>/
      franchise.yaml            # identity, authorIds, features, startHere
      works.yaml                # the bibliography (required)
      orders.yaml               # additional reading orders (optional)
      eras.yaml                 # creative periods (optional)
      events.yaml               # franchise-specific events (optional)
      characters.yaml           # recurring characters / crossover figures (optional)
      editions.yaml             # concrete editions: ISBNs, covers (optional)
      theme.yaml                # branding (optional; app has a neutral default)
```

Only `franchise.yaml` and `works.yaml` are required.

## Capabilities: how content activates app features

The app computes a capability set per franchise. Default is `auto`: a feature
activates when the data that powers it exists. `franchise.yaml` can force any of
them `on` or `off` (e.g. a curator may want the River view off while the aura is
still thin, even though events exist).

| Capability    | Auto-activates when...                              | Powers |
|---------------|-----------------------------------------------------|--------|
| `river`       | the franchise has timeline events (aura)            | the atmospheric River view |
| `orderDiff`   | 2+ reading orders exist (derived default counts)    | side-by-side order comparison |
| `wizard`      | `startHere` is present in franchise.yaml            | the "where to start" guided onboarding |
| `connections` | any work has `connections` or characters.yaml exists| the connections map + per-work crossover panels |
| `companion`   | the franchise has timeline events                   | reading companion mode for in-progress books |
| `hall`        | always (opt-out only)                               | inclusion in the cross-franchise hall |
| `editions`    | editions.yaml exists                                | exact-edition store links + curated covers |

```yaml
# franchise.yaml (all optional; omitted keys mean auto)
features:
  river: auto        # auto | on | off
  orderDiff: auto
  wizard: auto
  connections: auto
  companion: auto
  hall: auto
  editions: auto
```

## franchise.yaml

```yaml
id: stephen-king
name: Stephen King
kind: author                    # author | shared-universe | series
description: >
  One-line essence. May use [[work:...|links]].
authorIds: [stephen-king]       # global author ids (content/authors/)
themePreset: literary-noir
features: {}                    # see Capabilities above; optional
startHere:                      # optional; powers the wizard (see below)
  paths: [...]
sources: [https://...]
```

### startHere: the "where to start" configuration

The wizard is content-driven: the franchise declares *paths* (curated entry
recommendations), each tagged with who it fits. The app asks the reader two
questions (experience with the author, appetite for commitment) and scores the
paths by tag match. No app code changes per franchise - a franchise without
`startHere` simply has no wizard.

```yaml
startHere:
  paths:
    - id: essentials
      title: The essentials
      description: >
        Five landmark books that show the full range. If these land, everything
        else is open.
      workIds:                   # EITHER an explicit short list of works...
        - stephen-king/the-shining
        - stephen-king/it
      orderId: null              # ...OR point at an order from orders.yaml
      fit:
        experience: [new]        # new | returning | completionist
        commitment: [taste, arc] # taste (a few books) | arc (a series/thread) | complete (everything)
      note: >
        Optional curator aside shown with the recommendation.
```

Rules:
- Each path has exactly one of `workIds` (a short curated list) or `orderId`
  (an order in `orders.yaml`, or the literal `default` for the derived
  publication order).
- `fit.experience` and `fit.commitment` are lists; a path can serve several
  audiences. Cover the matrix loosely; the app falls back to the best partial
  match, so gaps are fine.

## content/authors/&lt;slug&gt;.yaml (global)

Unchanged from v1. One file per human being, referenced by `authorIds` /
`withAuthorIds` everywhere. Author-life events live here (`lifeEvents`), because
they follow the person across franchises.

```yaml
id: stephen-king
name: Stephen King
aka: ["Steve King"]
born: 1947-09-21
died: null
bio: >
  Short factual bio, may use [[work:...|links]].
pseudonyms:
  - name: Richard Bachman
    note: When/why used; how it was revealed.
lifeEvents:
  - id: king-van-accident-1999
    date: 1999-06-19
    title: Near-fatal roadside accident
    impact: high                 # low | med | high
    description: >
      What happened and how it colors the work around it.
    spoilerAfter: null           # or a work id (see Spoilers)
    sources: [https://...]
sources: [https://...]
```

## works.yaml

```yaml
- id: stephen-king/carrie        # STABLE forever - never rename
  title: "Carrie"
  authorIds: [stephen-king]
  published: 1974                # year precision fine; full date when confident
  subseries: null                # e.g. "The Dark Tower", "Mistborn: Era 1"
  canonTier: core                # core | extended | apocrypha
  publishedAs: "Richard Bachman" # optional; only when the cover name differs
  withAuthorIds: [peter-straub]  # optional collaborators (global author ids)
  synopsis: >
    Spoiler-free premise. May use [[work:...|links]].
  connections:                   # optional; work-to-work links (crossovers,
    - stephen-king/the-stand     # sequels, shared characters/cosmology)
  externalIds:
    openLibrary: OL81626W        # enrichment bot fills these; leave empty if unsure
    googleBooks: null
    wikidata: null
  sources: [https://...]
```

`connections` is **directional but rendered both ways**: declare the connection
on the *later* work pointing back at the earlier one (the later work is the one
whose reading is enriched). The app renders the edge on both works. A connection
whose *existence* is itself a spoiler belongs in `characters.yaml` appearances
with a `spoilerAfter` instead, or as an event.

## characters.yaml (optional)

Recurring figures whose appearances across works are part of the franchise's
connective tissue. This is what powers the connections map's character layer and
`[[character:<id>]]` references in prose.

```yaml
- id: stephen-king/randall-flagg  # STABLE; prefixed by franchise slug
  name: Randall Flagg
  aka: ["The Walkin Dude", "The Man in Black"]
  description: >
    Spoiler-free essence of who this is. May use [[work:...|links]].
  appearsIn:
    - workId: stephen-king/the-stand
      note: Primary antagonist.
    - workId: stephen-king/the-eyes-of-the-dragon
      note: The court magician.
      spoilerAfter: null          # set when THIS appearance is a reveal:
                                  # hidden until the reader passes that work
  sources: [https://...]
```

Rules:
- `appearsIn[].workId` must resolve. An appearance with `spoilerAfter` is hidden
  from readers who have not read that boundary work (and shielded for anonymous
  visitors), because sometimes *the fact a character shows up at all* is the
  spoiler.
- Keep the roster tight: figures that genuinely thread works together, not a
  full character wiki.

## editions.yaml (optional)

Concrete published editions. Works power orders; editions power buying,
covers, and **published translated titles**. Only add editions you can verify
(a real ISBN from a real source); never guess an ISBN. Sparse is fine: the app
falls back to search links and OpenLibrary covers when a work has no edition.

```yaml
- id: discworld/guards-guards/presenca-2004-pt
  workId: discworld/guards-guards
  isbn13: "9789722336840"
  language: pt-PT                # BCP-47; see "Language codes" below
  title: "Guardas! Guardas!"     # the title AS PUBLISHED in that language
  translator: "Ana Saldanha"     # optional; credited translator
  format: paperback              # hardcover | paperback | ebook | audiobook
  publisher: Editorial Presença
  year: 2004
  coverUrl: null                 # optional; else derived from ISBN/OLID
  note: Optional curator aside.
  sources: ["https://www.wook.pt/..."]
```

### Published titles are edition data, not translation

A work's `title` is its **original** title and never changes. A translated
title belongs to the edition that published it, because it is a fact about a
real book someone can buy. **Never invent one**: if no Portuguese edition of a
work exists, that work simply has no `pt-PT` edition, and the app shows the
original title. Inventing a translated title fabricates a book that does not
exist - the one thing a completionist site can never do.

The app uses `title` when the reader's locale matches the edition's language,
showing the original alongside it.

### Language codes

Use **BCP-47 with the region when the region matters for books**:

- `pt-PT` and `pt-BR` are **different editions with different translations,
  titles, and ISBNs**. Never tag a Brazilian edition `pt` or `pt-PT`: a Lisbon
  reader would be sent to a book they cannot buy locally. Same rule for
  `en-GB` vs `en-US` where titles genuinely differ.
- Where the region is irrelevant, a bare code (`fr`, `de`, `it`) is fine.

## orders.yaml

Additional orders only. The default (publication-chronological over ALL works)
is derived from `works.yaml`; never write it by hand.

```yaml
- id: stephen-king/dark-tower-connected
  name: The Dark Tower - connected reading order
  type: curated                  # chronological-inuniverse | author-recommended | curated
  source: canon
  rationale: >
    Why a reader might choose this order. May use [[work:...|links]].
  orderedWorkIds: [stephen-king/the-gunslinger, ...]
  debated:
    - "Contested placements, with the argument for each side."
  sources: [https://...]
```

## eras.yaml

```yaml
- id: the-golden-decade
  title: The Golden Decade
  period: "1980-1989"
  themes: [addiction, small towns, childhood]
  description: >
    What defined this creative period. May use [[work:...|links]].
```

## events.yaml (franchise) and events/global.yaml (shared)

```yaml
# franchise events.yaml
- id: king-bachman-outed-1985
  date: 1985
  title: The Bachman secret breaks
  scope: culture                 # author-life | world | culture | industry
  reach: franchise               # franchise here; global events -> global.yaml
  impact: med
  description: >
    What happened and why it matters to the reading.
  spoilerAfter: null
  sources: [https://...]
```

`global.yaml` holds `reach: global` events shared by every franchise (wars,
cultural ruptures, industry shifts). Append, never duplicate; check for an
existing entry before adding one.

**What earns an event a slot** is editorial, not structural - see "The aura
editorial standard" in the `franchise-research` skill: high = recolors the
text, med = explains the shelf, low = texture of the times; an event that does
none of the three does not ship.

## Spoilers (cross-cutting)

Any event, character appearance, or note that could spoil carries
`spoilerAfter: <work-id>`: the work beyond which it is safe. Semantics in the
app:

- A signed-in reader who has **read** the boundary work sees the content plainly.
- Anyone else (including anonymous visitors) gets a shielded teaser they can
  deliberately reveal.
- `spoilerAfter: null` (or omitted) means safe for everyone.

Pick the boundary as *the work whose experience the detail damages*, not the
work where the detail appears.

## achievements.yaml (global) and franchises/&lt;slug&gt;/achievements.yaml

Achievements are **data** (CONCEPT §7): a declarative `criteria` the app
evaluates over a reader's progress plus the canon. Adding a badge is a content
PR; only a brand-new criteria *kind* needs app work.

- `content/achievements.yaml` holds franchise-agnostic badges (any reader of
  any franchise can earn them).
- `content/franchises/<slug>/achievements.yaml` holds that wing's badges, with
  ids prefixed by the franchise slug so they never collide.

```yaml
- id: stephen-king/golden-decade      # franchise badges: "<slug>/<badge>"
  name: Into the Golden Decade
  description: Read 5 works from Stephen King's Golden Decade (1980-1989).
  icon: "🌗"                          # emoji
  tier: silver                        # bronze | silver | gold
  category: context                   # completion | streak | context | social | discovery | curation
  criteria:
    kind: era_reader                  # see the kinds below
    franchiseId: stephen-king
    eraId: the-golden-decade
    count: 5
```

Criteria kinds the app implements (the validator rejects anything else, and
resolves every franchise/order/era reference inside them):

| kind | fields | earned when |
|---|---|---|
| `read_count` | `count`, optional `franchiseId` | that many works read (optionally within one franchise) |
| `franchise_complete` | `franchiseId` | every work in the franchise read |
| `order_complete` | `orderId` | every work in that reading order read |
| `punctual_read` | `withinYears` | any work read within N years of publication |
| `era_reader` | `franchiseId`, `eraId`, `count` | that many works from one era read |

## Images (visual metadata)

Orrery is a museum; it needs pictures. Images are **referenced by URL, never
uploaded to this repo** (no binaries in content), and every one must be
legally displayable - see "Image rights" below.

Any of these entities may carry an `images` block; all fields are optional:

```yaml
# content/authors/<slug>.yaml
images:
  portrait: "https://upload.wikimedia.org/.../Terry_Pratchett.jpg"
  portraitCredit: "Luigi Novi, CC BY 3.0"
  portraitSource: "https://commons.wikimedia.org/wiki/File:..."

# franchise.yaml
images:
  header: "https://..."            # a wide banner for the wing
  headerCredit: "..."
  headerSource: "https://..."

# works.yaml (per work) - a cover the app can use when no edition cover exists
images:
  cover: "https://covers.openlibrary.org/b/id/12345-L.jpg"
  coverCredit: "OpenLibrary"
  coverSource: "https://openlibrary.org/works/..."

# editions.yaml already has coverUrl for a SPECIFIC edition's jacket
```

### Image rights (hard rule)

Only reference images you can justify:

- **Wikimedia Commons / Wikipedia** - check the file's licence; most are CC BY,
  CC BY-SA, or public domain. **Record the licence and the author in
  `*Credit`.** This is the best source for author portraits.
- **OpenLibrary covers** - fine to hot-link; credit OpenLibrary.
- **Publisher press/media pages** - usually permitted for editorial use;
  cite the page in `*Source`.
- **Never** scrape a retailer's jacket image, never take an image with no
  discoverable licence, and never link something behind a paywall or hotlink
  ban. If you cannot establish the rights, **leave the field empty** - the app
  degrades to typographic covers and text headers by design.

## theme.yaml

See the app's CONCEPT §6 (the design law). Personality through palette + one
display face + one signature; readability floor is non-negotiable. All three
levers are content: the app supplies only the curated *set* each choice picks
from.

```yaml
preset: literary-noir
palette: { bg: "#15110d", surface: "#1f1913", ink: "#ece3d4", muted: "#9a8f7e", accent: "#b04a34" }
displayFace: fraunces
signature: beam
notes: >
  The intent in one paragraph, so future curators keep the restraint.
```

- `palette` keys: `bg`, `surface`, `ink`, `muted`, `accent` (each becomes a CSS
  custom property on the franchise's pages).
- `displayFace`: one of the app's curated serifs - `fraunces`, `spectral`,
  `sourceSerif`. An unknown value falls back to the default rather than
  breaking the page. Adding a face is a deliberate app-side design decision;
  propose one in the PR if a franchise genuinely needs it.
- `signature`: the one signature element - `beam` (a bold accent rail the works
  string along), `thread` (a quiet hairline; the default), `rule` (a firm
  architectural line), or `none`.

## Validation

`python scripts/validate.py` (run by CI on every PR) enforces:
- required files, stable-ID prefixes, no duplicate IDs
- every reference resolves: authorIds, withAuthorIds, order workIds, connections,
  character appearances, startHere paths, spoilerAfter boundaries, and inline
  `[[type:id|text]]` links (work, author, franchise, character)
- enum discipline: canonTier, impact, scope, order type, features keys/values,
  fit tags, edition formats
- global.yaml events carry `reach: global`

If the validator and this document ever disagree, fix one of them in the same PR
that exposed it.
