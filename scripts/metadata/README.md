# The metadata stack

Bulk edition and cover lookup for a wing, so the `editions` and
`visual-metadata` stages stop paying a tool call per record.

## Why

A curation run costs roughly **context size x number of tool calls**. Measured
on the Jo Nesbø wing (34 works):

| stage | tool calls | tokens | wall clock |
|---|---|---|---|
| `editions` | 186 | 439k | 33 min |
| `visual-metadata` | 176 | 441k | 24 min |

Together **28% of the whole wing**, and almost all of it one-record-at-a-time
lookups an agent narrated. The same fetching is ~40 HTTP requests inside a
single script run.

## What this does NOT do, and why that matters

**It does not replace the judgement.** Run against the Nesbø wing, the
candidate search surfaced two images the `visual-metadata` agent had already
correctly refused:

- a scan of **Gjenferd's title page**, filed on OpenLibrary as a cover;
- a **Snømannen** jacket carrying a **San Francisco Public Library barcode**.

No cheap signal separates those from a real cover. Not HTTP status, not byte
size, not dimensions. Only looking. Those 176 calls bought that discrimination
and it was worth buying.

So the split is:

| scripts | agent |
|---|---|
| fetch, batch, cache, filter by language and publisher | which market a wing should use |
| check digits, region prefixes, dead URLs, blank placeholders | is this a title page, an omnibus, a barcode |
| download every candidate in one pass | look at them |

Use `--download-covers DIR` and then open the files. The saving is in the
round trips, not in skipping the looking.

## Usage

```bash
# candidate editions per market, one pass
python scripts/metadata/lookup.py jo-nesbo --author "Jo Nesbo" --markets no,en,pt

# pull the candidate covers down so they can be judged in a few reads
python scripts/metadata/lookup.py jo-nesbo --author "Jo Nesbo" \
    --markets no --download-covers .cache/covers/jo-nesbo

# arithmetic on a wing that already has editions.yaml - no model needed
python scripts/metadata/lookup.py jo-nesbo --verify-isbns

# every declared AND derived cover URL, including the ones the app synthesises
python scripts/metadata/lookup.py jo-nesbo --check-covers

python scripts/metadata/lookup.py --providers x   # what is registered
```

`--check-covers` is the one to run before a wing leaves draft. It caught **20
dead cover URLs** on Nesbø: works with no verified `images.cover` fall through
to an ISBN-shaped OpenLibrary guess that 404s for most non-anglophone ISBNs.
`validate.py` cannot see those, and they render as broken images.

## Providers

Modelled on Calibre-Web Automated's `cps/metadata_provider/` (12 providers,
each a class with one search method), which is the arrangement that lets a book
stack add a source without touching its callers. The difference: ours must
**batch**, because CWA looks up one book for a waiting human and we sweep a
34-work wing.

| provider | authoritative for | notes |
|---|---|---|
| `openlibrary` | breadth, and the only ISBN batching here | 20 ISBNs per call |
| `googlebooks` | non-anglophone editions, best cover resolution | **needs an API key in practice** |
| `nb.no` | Norwegian first editions | legal deposit, so silence is evidence |
| `wook` | pt-PT titles, ISBNs, publishers, dates | scraper; **covers are watermarked, do not use them** |

### Google Books needs a key

The unauthenticated endpoint returned **HTTP 429 from two separate networks**
when this was first tested. Get a free key from Google Cloud (enable "Books
API"; 1,000 requests/day by default) and export it:

```bash
export GOOGLE_BOOKS_API_KEY=...
```

Without one the provider still runs, best-effort, and will mostly be throttled.

It is worth having for two things OpenLibrary is weak at: editions published
outside the anglophone trade, and cover resolution. CWA's `google.py` has the
trick, lifted here - strip `&edge=curl` and append `&fife=w800-h900` to get an
800x900 image instead of the ~128px thumbnail. That is the fix for the
`snømannen` cover shipped at 96x151.

## WOOK, and what a scraper is good for

WOOK is the worked scraper example and it makes the point well: **it is
excellent for the data and unusable for the pictures.**

Good for the pt-PT **published title, ISBN, publisher and exact release date** -
a sweep of one author returns those in seconds, and OpenLibrary holds almost
none of it for Portugal.

**Its covers are watermarked.** Every `img.wook.pt` image carries a diagonal
"wook" mark in the bottom-right corner, invisible at thumbnail size and obvious
at `/1000x`. Raising the resolution makes it worse. That is exactly the
"watermarked scrape" the visual-metadata skill names: it passes every automated
check and is not licensable. The provider still returns `cover_url`, because
looking at a jacket is a good way to confirm which edition a record is, but it
belongs in a candidate table and never in `images.cover`.

Two implementation notes worth copying into the next scraper:

- **Read JSON-LD, not the DOM.** WOOK publishes a `@type: Book` block with
  everything needed. Structured data the site exposes deliberately survives
  redesigns that break selectors.
- **Send `core.BROWSER_HEADERS`, not just a User-Agent.** WOOK is behind
  Cloudflare and 403s UA-only requests. Earlier runs concluded "the live site
  403s" and fell back to web.archive.org, which serves a stale catalogue.
- Searching WOOK **by ISBN does not work** - it falls back to unrelated
  recommendations rather than returning nothing, which is worse than an empty
  result because it looks like an answer. Search by author or title.

## Adding a source

1. Subclass `Provider` in `providers.py`. Set `name`, `interval` (seconds
   between requests to that host) and `authoritative_for`.
2. Implement whichever of `by_isbn`, `by_author`, `editions_of` the source
   actually has. Leave the rest - the base class returns empty and every caller
   already handles a provider that cannot answer.
3. Add it to `ALL`. Registration order is preference order for callers that
   merge sources.
4. Write the `authoritative_for` line honestly. Coverage is not uniform, and a
   caller choosing between two sources needs to know which one to believe.

**A provider must never invent a field.** An absent publisher is a fact about
the record; filling it makes the catalogue assert something no source says.

### Scrapers

Welcome, on the same contract - a scraper returning `MetaRecord`s is
indistinguishable to a caller. Keep the parsing inside the provider, set a
slower `interval`, and expect to maintain it. CWA carries `amazon.py` and
`scholar.py` on exactly those terms. Send the browser User-Agent from
`core.UA`: several publisher and library catalogues 403 a bare request and
serve a browser normally, which is recorded in CURATION.md's trap registry.

### National libraries

`nb.no` is the worked example. The pattern generalises and is worth repeating
per market: Portugal's BNP settled the *Intruso* title mapping on the French
wing, and Germany's DNB is what CWA carries as `dnb.py`. Where deposit is
mandatory, **absence is evidence** rather than a gap - that is how *Blod på
snø* was settled as 2015 against English Wikipedia's 2014.

## Behaviour worth knowing

- **Caching** to `.cache/metadata/`, one week. A 404 is cached as an answer, so
  a re-run does not pay for it twice.
- **Rate limiting** is per host and process-wide, so concurrent providers
  cannot collectively earn a 429.
- **`None` is a result, not an exception.** A provider that raised on a missing
  record would turn a normal absence into a dead run mid-sweep.
- **Work-level language is a union.** OpenLibrary's search rows report every
  language across all editions, so `['ger','pol','nob','swe']` does not mean a
  Norwegian edition with a Norwegian cover exists. Go through `editions_of`.
- **`/b/isbn/<isbn>-M.jpg` is a guess; `/b/id/<cover_i>-L.jpg` is a real
  image.** Never synthesise the first and call it verified.
