# Orrery content schema (v2)

The canonical reference for everything under `content/`. The app (`rfsbraz/orrery`)
renders exactly what is described here; `scripts/validate.py` enforces it in CI.
This file defines *what the data is*; `docs/CURATION.md` is the working contract
for *how* curation is done (sourcing, verification, gates, and the comment
policy: **content YAML carries data, sources, and data decision logs only -
never pipeline narration or coordination**; `validate.py` warns on violations).

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
| `wizard`      | `startHere` is present in franchise.yaml            | the "where to start" guided onboarding |
| `connections` | any work has `connections` or characters.yaml exists| the connections map + per-work crossover panels |
| `companion`   | the franchise has timeline events                   | reading companion mode for in-progress books |
| `hall`        | always (opt-out only)                               | inclusion in the cross-franchise hall |
| `editions`    | editions.yaml exists                                | exact-edition store links + curated covers |

```yaml
# franchise.yaml (all optional; omitted keys mean auto)
features:
  river: auto        # auto | on | off
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
                                # author is the norm: a wing spans its
                                # author's COMPLETE works (universes/series
                                # are subseries inside it, never the wing
                                # boundary - see franchise-research)
description: >
  One-line essence. May use [[work:...|links]].
authorIds: [stephen-king]       # global author ids (content/authors/)
themePreset: literary-noir
features: {}                    # see Capabilities above; optional
startHere:                      # optional; powers the wizard (see below)
  paths: [...]
sources: [https://...]
```

### globalEvents: which shared events reach this author

Optional, on `franchise.yaml`. `reach: global` means "any franchise **could**
carry this", not "every franchise must".

**A global event renders on a wing if and only if that wing names it in
`include`.** There is no arithmetic default and no implicit membership: silence
means absent.

```yaml
globalEvents:
  include:
    - fantasy-paperback-boom-1965    # predates him; created the category he writes in
  exclude:
    - financial-crisis-2008          # lived through it; no book answers it
```

- **`include`** - the operative list. Every entry is a claim that this event
  reached this author's page, and carries a short note saying how.
- **`exclude`** - **gates nothing.** Nothing renders unless it is included, so
  an exclusion changes no output. It is kept as the record of a judgement
  already made, so a later pass knows the ground was covered and does not
  re-litigate it from scratch.

This used to work the other way: an event rendered on every wing whose author
lifespan covered it, unless that wing excluded it. The lifetime test was cheap
and needed no curation, which made it attractive - and it was quietly wrong,
because it was only ever correct for the events that existed when a wing was
ruled. Adding one to `global.yaml` retroactively opted in every wing already
curated, and nobody re-runs resonance across the catalogue when an event lands.

> This also existed because of a real defect: `portugal-bailout-2011` was added
> a day after the Palahniuk wing was ruled, and rendered on his timeline and on
> four other foreign wings until it was spotted. Wrong content costs more than
> absent content - an unclaimed event is a gap someone can grep for, where a
> wrongly-claimed one just looks like curation.

The judgement lives here rather than in `global.yaml` so that the shared file
stays franchise-agnostic. The `event-resonance` skill owns these decisions.

> This existed because of a real defect: João Tordo, born 1975, opened his page
> in **1910** and walked the reader through both world wars before his first
> novel in 2004.

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
  published: 1974                # YEAR ONLY, a bare integer - never 1974-03-26 (see below)
  subseries: null                # e.g. "The Dark Tower", "Mistborn: Era 1"
  canonTier: core                # core | extended | apocrypha
  publishedAs: "Richard Bachman" # optional; only when the cover name differs
  withAuthorIds: [peter-straub]  # optional collaborators (global author ids)
  authorRole: author             # author | co-author | contributor | editor
  contributionTitle: "The Reach" # optional; the piece contributed, if not the whole book
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

### published is a bare year integer, never a full date

`published: 1974`, not `published: 1974-03-26`. This is enforced by the validator.

The reason is that a full date does not survive the trip into the app. YAML
parses `1974-03-26` as a **string**, and every consumer of `published` is
year-granular arithmetic: the River keys one layer per year, era spans are year
ranges, decade rules and era-reader achievements compare against year numbers.
A string silently loses all of those comparisons - `"2002-09-17" >= 1996` is
`false` - so the work lands on a layer of its own, outside every era, missing
from the achievement that should have counted it. Nothing errors; it just
quietly renders wrong.

This field used to say "full date when confident", and the first new wing
written against it put five works on dated lines. Day precision has no consumer
in the product; if the exact date matters editorially, it belongs in an event or
in `sources`, not here.

### authorRole and canonTier: what belongs in a wing

`authorRole` defaults to `author` and only needs stating when it is something
else. It exists so a wing can hold **honest completionist data without making a
false claim**. A 2009 vampire anthology containing one story by this author is
real and a completionist wants to know about it, but it is not a book they wrote:

```yaml
- id: joao-tordo/contos-de-vampiros
  title: "Contos de Vampiros"
  authorIds: [joao-tordo]
  authorRole: contributor
  contributionTitle: "A Casa em Sintra"
  canonTier: apocrypha
```

The same applies to a book where the author wrote only an introduction
(`contributor`) or assembled the volume (`editor`).

**`canonTier` is the reading spine, not a quality judgement.**

| Tier | Meaning |
|---|---|
| `core` | the works the franchise *is*; the default walk |
| `extended` | genuinely theirs, off the spine (nonfiction, minor collections) |
| `apocrypha` | contributions, limited or unfinished works, periodical pieces |

Tier records the **kind of publication, never the researcher's confidence**.
Uncertainty belongs in a `note:` or `confidence:`, and a work parked in
`extended` because nobody verified it is a bug: it tells every downstream reader
something false about the book's status. The João Tordo audit found five novels
sitting in `extended` for exactly that reason.

> **Known limitation, do not rely on tier to hide anything.** The app currently
> treats `canonTier` as a **display label only**. It filters nothing, so an
> `apocrypha` work still appears in the strata walk and still takes a numbered
> position in the derived publication order. Until the app honours the tier,
> adding contributor entries to a wing changes that wing's default reading order.
> Weigh that before bulk-adding anthologies.

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

> **Editions are a convenience for browsing locally, and nothing more.**
> Orrery exists to experience an author **as they were** - not as publishers
> handled them country by country. A foreign release date is a fact about a
> licensing deal, not about the author's work, so **it never bears on a
> reading order, an era boundary or a `startHere` path.**
>
> The concrete case: the first two Harry Hole novels reached English twelve
> years after the rest, so English readers met the series at book three. That
> is a real and interesting fact about the English market. It is not a reading
> order, and no amount of sourcing would make it one.
>
> It follows that **a translated title must never be the only title a reader
> sees**. Inline references in a translated wing carry the published local
> title for readability, and the app renders the author's own title beside it.
> The edition is the convenience; the original is the substance.

```yaml
- id: terry-pratchett/guards-guards/presenca-2004-pt
  workId: terry-pratchett/guards-guards
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

## Translations (content/i18n/&lt;locale&gt;/)

Curated prose - synopses, era and event descriptions, order rationales, author
bios, franchise descriptions - is authored in a base language and translated
via **overlay files keyed by stable ID**. The engine merges base + overlay
**field by field**, so a partially translated franchise renders the translated
fields in the reader's language and the rest in the base language, rather than
breaking or looking empty.

```
content/i18n/pt-PT/franchises/stephen-king/works.yaml    # synopses only
content/i18n/pt-PT/franchises/stephen-king/events.yaml
content/i18n/pt-PT/franchises/stephen-king/eras.yaml
content/i18n/pt-PT/franchises/stephen-king/orders.yaml   # rationales, debated
content/i18n/pt-PT/franchises/stephen-king/franchise.yaml
content/i18n/pt-PT/authors/stephen-king.yaml             # bio + lifeEvent prose
content/i18n/pt-PT/events/global.yaml
```

Each entry carries the **id** plus only the fields being translated:

```yaml
# content/i18n/pt-PT/franchises/stephen-king/works.yaml
- id: stephen-king/carrie
  synopsis: "Uma rapariga com poderes telecinéticos vinga-se de forma catastrófica na noite do baile."
```

### Nested lists merge by id

Structures that contain a list of id-bearing items - an author's `lifeEvents`,
a franchise's `startHere.paths` - are merged **item by item, keyed by id**. A
translation carries only the prose fields and never restates structure
(`workIds`, `orderId`, `fit`, dates, impact):

```yaml
# content/i18n/pt-PT/authors/agatha-christie.yaml
- id: agatha-christie
  bio: "..."
  lifeEvents:
    - id: christie-disappearance-1926
      title: "O desaparecimento de onze dias"
      description: "..."

# content/i18n/pt-PT/franchises/stephen-king/franchise.yaml
- id: stephen-king
  description: "..."
  startHere:
    paths:
      - id: essentials
        title: "Os essenciais"
        description: "..."
        note: "..."
```

### Coverage

`python scripts/i18n_coverage.py` reports, per locale, which prose files are
fully covered, partial, or missing entirely. CI runs it on every PR.

It exists because of a real failure: translation work was split by franchise,
and the files belonging to **no** franchise - the shared `events/global.yaml`,
co-author bios, character rosters - were silently skipped and shipped in
English. Partial coverage is fine and expected; *unnoticed* coverage gaps are
not. Check the report before declaring a locale done.

### Rules

- **Never translate an `id`, a slug, a `sources` URL, or an author name.** Only
  prose fields.
- **Never translate a work `title`.** A translated title is edition data (see
  editions.yaml) because it must be a real published title, not an invention.
  Era, event, and life-event `title`s are the opposite case - they are curated
  prose written by the curator, so they are translated like any other prose.
- **Keep the inline `[[work:id|text]]` references.** Translate the *display
  text* after the pipe; never the id. `[[work:stephen-king/the-stand|A Dança
  da Morte]]` is correct.
- **Partial is fine and expected.** Translate the highest-value prose first
  (franchise description, era descriptions, high-impact event descriptions,
  then synopses).
- An overlay entry whose id does not resolve is a **CI error** - the validator
  checks every one, so a renamed or deleted work cannot leave a dangling
  translation.

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
- **OpenLibrary covers** - fine to hot-link; credit OpenLibrary. **But see the
  laundering rule below: OpenLibrary is a permitted host, not a blanket
  permission for whatever it happens to be hosting.**
- **Publisher press/media pages** - usually permitted for editorial use;
  cite the page in `*Source`.
- **Never** scrape a retailer's jacket image, never take an image with no
  discoverable licence, and never link something behind a paywall or hotlink
  ban. If you cannot establish the rights, **leave the field empty** - the app
  degrades to typographic covers and text headers by design.

**The rule is about the asset, not the hostname.** A retailer's jacket scan does
not become usable by being uploaded to a permitted host. The João Tordo visual
pass found that **4 of the 6 OpenLibrary covers available for that author were
retailer scrapes with Bertrand and WOOK watermarks burned into the pixels** - so
"it came from OpenLibrary" and "it is a retailer jacket" were true of the same
file. Where the two rules point in opposite directions, **the retailer rule
wins and the slot stays empty.**

Two checks follow from this, and both are mandatory before writing a cover URL:

- **Look at the image.** A watermark passes every HTTP check ever written. No
  automated test substitutes for opening it.
- **Pass `?default=false`** on OpenLibrary lookups. Without it OpenLibrary
  returns HTTP 200 with a blank placeholder, so a naive check reports success on
  books it holds nothing for. A recorded URL that renders nothing is worse than
  an empty slot, because it looks like coverage.

**Expect low coverage outside the anglophone canon, and do not pad it.** For a
Portuguese literary novelist, roughly 20% is the realistic ceiling from open
sources. There, the typographic fallback is not a degraded path, it is the
primary rendering. The highest-leverage fix is licensing rather than sourcing:
for most non-English catalogues a single national publisher holds the entire
backlist, and one editorial-use agreement covers all of it.

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

### theme.art: the wing's visual language for generated sketches

Optional. The palette above styles the *interface*; `art` describes how this
author's **illustrations** should look, so that an era plate drawn today and a
life-event sketch drawn in a year still belong to the same wing. It is read by
`/asset-prompt`, never by the app.

```yaml
art:
  motifs: [fishing boats, whitewashed walls, ex-voto tin hearts, rain on slate]
  atmosphere: >
    Quiet, close, domestic. Weather rather than drama; interiors seen from
    just inside the door.
  lineCharacter: fine, slightly tremulous ink, as if drawn with a dip pen
  backgroundTexture: warm laid paper with a faint umber wash
  accentUse: burnt terracotta on one element only, never as a fill
  avoid: [maritime kitsch, azulejo tiling, fado cliches, sunlit postcard blue]
```

- Every field is prose for a prompt, not an enum. Write it so a competent
  illustrator could follow it without seeing the other wings.
- `avoid` is where a wing's specific cliche gets named. Generic negatives
  (photorealism, text, watermarks) live once in `docs/VISUAL.md` and are added
  to every prompt automatically - do not repeat them here.
- Keep it stable. Changing `art` after a wing has sketches means the new ones
  will not match the old ones, which is the failure this block exists to
  prevent; if it must change, plan to regenerate the whole wing.

### images on eras, events and life events

`eras.yaml` entries, `events.yaml` entries, `global.yaml` events and an author's
`lifeEvents` may each carry an `images` block with the **`sketch`** field:

```yaml
images:
  sketch: assets/valter-hugo-mae/vhm-born-1971.webp   # repo-relative, committed
  sketchCredit: Generated for Orrery (gpt-image-1)
  sketchSource: docs/VISUAL.md#4-asset-specs          # optional: the spec it was made to
```

Unlike `portrait`, `cover` and `header` - which are third-party images we link
to and credit - **a sketch is ours and lives in this repo** under
`assets/<wing-slug>/<entity-id>.webp`, committed alongside the entry that
references it. The app copies `assets/` into its `public/` at build time.

The validator enforces: the path is repo-relative and under `assets/`, the file
**exists** (a missing file fails immediately, where a dead link validates green
forever), the format is `.webp`, and the file is under 320KB. gpt-image-1
returns PNG, so converting is part of filing the asset - a 1024x1024 PNG was
1.77MB and became 153KB as webp. PNG is also excluded by the app's
`.dockerignore`, so a committed PNG would work locally and vanish in production.

`sketchCredit` is required **and must say the image was generated** - the
validator rejects a credit that reads like a source. A reader has to be able to
tell an illustration we commissioned from a photograph we licensed; on a site
whose claim is that the facts are checked, blurring the two is a lie of
omission.

World events in `global.yaml` render on every wing that carries them, so their
sketch is drawn once in the neutral house style on a transparent background and
tinted per wing with that wing's `accent`. Do not give a global event a sketch
that only suits one author.

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
