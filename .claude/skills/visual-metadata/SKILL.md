---
name: visual-metadata
description: Source and record the imagery a franchise wing needs - author portraits and per-work covers - with defensible rights on every one. Use when adding or refreshing the images blocks in content/authors/<slug>.yaml or works.yaml.
---

# visual-metadata

Fill the `images` blocks that turn a franchise wing from a list into a shelf:
one **portrait** per author, one **cover** per work. Output is git YAML,
reviewed by a curator via PR.

**No `franchise.images.header`.** It used to be a third deliverable here;
removed 2026-08-07 (orrery#169) after six separate wing builds confirmed the
same thing - roughly two dozen wings had one, and no page in the app has ever
read it. Do not source or set one; docs/SCHEMA.md no longer documents the
field.

This skill runs under [`docs/CURATION.md`](../../../docs/CURATION.md) - the
prime directives, comment policy, gates, shared trap registry and verification
doctrine apply throughout and are not repeated here.

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
  reference crosses wings - only the warning list narrows). This one is
  measured and still gets missed: one wing build ran eleven catalogue-wide
  validations where ten could have been scoped, each re-reading 40+ untouched
  wings to prove one file parses,
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

## Why this matters

Orrery is a museum walk; without imagery it is text on dark ground - correct,
complete, and dead. But images carry **rights**, and a books site that
hotlinks scraped jackets is a takedown waiting to happen. The job is not "find
the prettiest image". It is **find a good image whose rights you can state in
one line**, and write that line down.

## The source ranking

Work down this list. Do not skip to a lower tier because it looks nicer.

**1. Open Library covers** - `https://covers.openlibrary.org/b/id/<coverId>-L.jpg`

The default for covers, and the reason the app already treats
`covers.openlibrary.org` as its cover CDN (the service worker caches it). Open
Library hosts publisher jacket art and permits hot-linking; credit is
`"Open Library"` and the source is the OL **work** page you took the id from.
**Always check covers with `?default=false`** (CURATION §4) - a missing cover
otherwise answers 200 with a blank placeholder. Verify with the
`?default=false` URL even if you write the plain URL into the YAML.

**2. Wikimedia Commons** - the default for portraits. Every file
has a real, checkable licence. Never assume it: read the file's `extmetadata`
and record what it says (see "Reading a Commons licence" below). Most usable
files are CC BY, CC BY-SA, or public domain.

**2b. Wikidata, as a discovery layer, not a rights source.** An author's
Wikidata entity can carry a `P18` (image) claim pointing at a Commons file
that never made it into the English Wikipedia infobox - editors sometimes
tag a better or more recent photo on Wikidata without touching the article.
`https://www.wikidata.org/wiki/Special:EntityData/<Q-id>.json`, read `P18`,
then treat whatever it names as an ordinary Commons file (tier 2) - fetch its
own `extmetadata` and record the licence from there, never from the Wikidata
claim alone.

**2c. Non-English Wikipedia infoboxes**, checked directly, not assumed to
match the English article. A language edition close to the author's own
context (Irish for an Irish author, French/German for wide European
coverage) sometimes carries a different infobox image than English Wikipedia
or Wikidata's `P18` - an editor local to that language found or was given a
photo the English-language editing community never saw. Same rule as
everywhere else: whatever image it names is an ordinary Commons file, read
its own licence, never assume from the language edition using it that it is
clear.

**3. Openverse, full aggregation, never a raw Flickr search.**
`https://api.openverse.org/v1/images/?q=<name>&license_type=all-cc` indexes
CC-licensed Flickr plus over a dozen other providers (Europeana, Smithsonian
Open Access, museum and science-collection feeds, WordPress Photo Directory,
among others) behind one API with machine-readable licence metadata per
result - search it as one source, not as "Flickr with extra steps": a hit
can come from any indexed provider, and the provider name is in the result.
A convention or signing photo an amateur photographer uploaded to Flickr
under CC BY/BY-SA often never makes it to Commons at all, which is why this
is usually the highest-yield tier for a living author Commons has nothing
on. **Verify the licence on the result itself, not on Openverse's say-so** -
source platforms mislabel licences often enough that this is not optional,
the same discipline as reading a Commons file's own `extmetadata` rather
than trusting a caption.

**3b. Literary festival and book-fair official photography**, where the
festival runs its own Flickr/media account under a stated CC licence. Many
major festivals (Edinburgh International Book Festival, Hay Festival,
Cheltenham Literature Festival among them) photograph every visiting author
and release a portion of it CC BY or CC BY-NC specifically so press and
partner sites can reuse it - search Openverse and Flickr's own site scoped
to the festival's account name, and separately check whether the festival
has ever run a Wikimedia photo-a-thon (search Commons categories like
`Wikimedia UK` or `Women in Red` alongside the festival's name; these
partnerships exist specifically to get living authors, disproportionately
women, onto Commons and are a real, recurring source rather than a one-off).
**CC BY-NC is not usable** (this app's imagery must be reusable in a
commercial context per the licences already accepted elsewhere) - check the
specific term on each result, do not assume every festival photo is BY-NC or
that every one is fine.

**3c. Wikinews.** Original Wikinews content, including any photo its own
reporters took during an interview, is CC BY 2.5 by the project's own
default licence - worth a direct search
(`https://en.wikinews.org/w/index.php?search=<name>`) for any author who has
been interviewed by a Wikinews reporter in person, a narrow but real case.

**4. Library of Congress Prints & Photographs Online Catalog**, for authors
whose working life predates reliable Commons coverage.
`https://www.loc.gov/pictures/search/?q=<name>` - read the record's own rights
statement field (`No known restrictions` or explicit public domain only;
`Rights status not evaluated` is not a green light, it is an unanswered
question). Strong for historical/dead authors - weak to absent for anyone
whose career is mostly post-2000.

**5. Publisher / author official press or media pages** - only where the
page's own terms explicitly permit editorial use, and the terms text is what
you cite, not the mere presence of a "press" or "media" URL. A living,
actively-publicised author (a current bestseller list regular, someone who
tours) is exactly the case Commons and Flickr are least likely to already
cover, because their photographer is a paid professional who releases the
image through the publisher, not to the commons. Check **three** URLs, not
one, before concluding a publisher has nothing usable: the author's own site
(a `/press` or `/media` page with an explicit "for editorial use" headshot
download is common for this exact profile), the publisher's own author bio
page, and the publisher's **separate press room** (often at a different path
entirely - `/press-room`, `/media-center`, a dedicated newsroom subdomain -
built for journalists, distinct from the reader-facing author page, and
more likely to state reuse terms plainly). Also worth a check for a genre
with named prizes: an awards body (a crime-writing dagger, a genre-specific
prize) sometimes publishes its own winner/shortlist photography with press
terms attached, which is a fourth kind of URL, not a publisher one, don't
skip it because the search starts from "publisher." Cite the terms page
itself in `*Source`, not just the image URL - if the page does not say
editorial/press use is permitted, it is not a candidate regardless of how
official it looks.

**Museum/gallery "open access" collections (Smithsonian, Getty Open Content,
a small marked-open subset of the UK National Portrait Gallery) are a source
only for the specific images an institution has explicitly flagged open or
public domain** - most of a gallery's holdings, including most author
portraits in the NPG's own collection, remain copyrighted regardless of
being viewable on the institution's site. Do not infer permission from
"a museum put it online"; look for the institution's own open-licence or
public-domain marking on that specific record.

**Never**: Google Images, Goodreads, Amazon or any retailer's jacket file, fan
wikis, Pinterest, or a reverse-image-search result whose origin you cannot
name. An image with no discoverable licence is not a candidate.

## Rights rules (the hard part)

- **Never invent a credit.** If you cannot name who made an image and under
  what licence, you do not have the rights to use it.
- **Fetch every URL you write** and confirm it returns an image. A 404 in a
  content PR is a fabrication that happens to be honest (CURATION §1).
- **Unclear rights means empty.** A missing cover is a design gap; a stolen
  cover is a legal one. The app degrades to a typographic cover by design -
  that fallback exists precisely so you never have to guess. Leave the field
  out and say so in the PR.
- **Attribution is a field, not a footnote.** `*Credit` must carry everything
  the licence demands - author and licence name at minimum
  (`"Kevin Payravi / WikiPortraits, CC BY-SA 4.0"`). `*Source` points at the
  file's description page, where a reader can verify the claim.
- **Share-alike does not infect the site.** Displaying a CC BY-SA image is not
  creating a derivative work; BY-SA files just require attribution like any BY
  file. Do not reject them out of caution.
- **Watch for personality rights.** Commons flags some portraits
  `Restrictions: personality`. Editorial use on the subject's own author page
  is the intended case; never imply endorsement.
- **Never commit binaries.** Images are referenced by URL. `content/` holds no
  image files, ever.

## Covers: keying off editions and ISBNs

**What you write here is what the reader sees.** `works.yaml`'s `images.cover`
is the highest-ranked cover source the app has after an edition-specific
`coverUrl`, precisely because it is the only one a human has looked at.
Everything below it is a guessed URL.

That was not always true, and the story is worth carrying: for months
`coverFor()` did not read `images.cover` at all (the app's `Work` type did not
model the field), so every cover this skill had ever fetched and eyeballed was
ignored in favour of `/b/isbn/<isbn>`, a URL nobody had ever loaded. It
surfaced only when a Portuguese page rendered three broken images, because
OpenLibrary holds no cover for most non-anglophone ISBNs. **Fixed now, but the
lesson generalises: when a stage's output is inert, nothing fails.** If you add
or rely on a field, confirm something in the app reads it.

The goal is a cover that is really *this work's* cover, not a generic
franchise image repeated. Two paths in:

**Path A - via the work's Open Library id (preferred).** `works.yaml` often
carries `externalIds.openLibrary` (`OL…W`). Query the search API by key to get
the representative cover Open Library itself displays:

```
https://openlibrary.org/search.json?q=key:"/works/OL81626W"&fields=key,title,cover_i,edition_count
```

`cover_i` is the cover id; the image is
`https://covers.openlibrary.org/b/id/<cover_i>-L.jpg`. Prefer this over the
work JSON's `covers[0]`: that array is sometimes empty even when a good
edition cover exists, and its first entry is arbitrary.

**Path B - via an ISBN in `editions.yaml`.** `https://covers.openlibrary.org/b/isbn/<isbn13>-L.jpg`
resolves an edition's own jacket. Use it when a franchise's editions are well
covered on Open Library. **Check the region first**: a `pt-PT` Bertrand ISBN
is usually *not* in Open Library's cover set. The Stephen King canary hit
exactly this - all 68 editions were `pt-PT`, so every cover came from Path A.

Two ISBN traps worth knowing:

- **Open Library merges pt-BR and pt-PT under one work record** (CURATION §4,
  prefix table included) - an ISBN lookup keyed off a Portuguese work can hand
  you a Brazilian jacket. A Brazilian cover on a `pt-PT` work is the visual
  version of the invented-translated-title error the schema forbids.
- **Sweep at author level when a title search fails.** A work that returns
  nothing by title can still sit in the author's works list under a variant or
  all-caps title. `https://openlibrary.org/authors/<OL…A>/works.json?limit=100&offset=N`
  paginates the whole bibliography; in the King run it was the only way to
  find *Ur* (filed as `UR`), and it is how you prove a gap is real rather than
  a search failure - which is what makes "no cover" a defensible answer.

**Verify the OL work is the right work.** This is where covers actually go
wrong: Open Library is full of omnibuses, screenplays, and translated records
that match a title search. Real failures found in one franchise:

| Symptom | Example |
|---|---|
| The id points at an **omnibus** | `Novels (Black House / Talisman)`, `The Bill Hodges Trilogy (…)` |
| The id points at a **different work by another author** | "Misery" resolved to the William Goldman stage adaptation |
| The OL work **title is a translation** | The Waste Lands' record is titled `A Torre Negra` |
| `first_publish_year` is **junk** | 1925, 1960, 1978 on books published decades later |

So: check the author list, check `edition_count` (the canonical record usually
has dozens; an omnibus has one to three), and when in doubt fetch
`https://openlibrary.org/works/<id>/editions.json?limit=6` and read the actual
edition titles and publishers. A translated OL title is fine to use - the
*cover* is still that work's cover. A wrong work is not.

If `works.yaml` has a **wrong** `externalIds.openLibrary`, use the correct id
for the image but **do not edit `externalIds`** - report it in the PR so the
curator or the enrichment bot fixes it.

**Verify every image URL before writing it** - fetch with `?default=false`,
check status, content type and byte size. **Then look at every single one.**
An HTTP check cannot see what is *in* the pixels, and two failure modes only a
human eye catches:

- **Retailer scrapes** (CURATION §4). Open Library accepts user uploads lifted
  straight from a retailer with the watermark burned in - the Tordo run found
  **4 of 6** covers carried visible Bertrand or WOOK marks. Laundering through
  a permitted host changes nothing; reject it and look for another edition.
- **Degraded library scans.** Barcodes, spine stickers, library stamps and
  creased dust jackets. Not a rights problem, but shabby in a museum. When the
  work has other editions, pull the whole edition list
  (`/works/<id>/editions.json?limit=40`), collect every `covers` id, and pick
  a clean one - preferring the original publisher and the work's own language.
  Five of the eighteen King latecomers were replaced this way.

A **labelled contact sheet** makes this practical: download the candidates,
tile them into one image with the slug under each, and read it in a single
pass. Sixteen covers audit in one look instead of sixteen.

## Portraits: dimensions and framing

| Slot | Target ratio | Practical minimum | Notes |
|---|---|---|---|
| `portrait` | 2:3 to 3:4, tall | ~800px wide | Head and shoulders. A crop already framed as a portrait beats a wide press shot the app has to centre-crop blindly. |
| `cover` | Whatever the jacket is | Open Library `-L` size | Do not crop or normalise. A cover is a document, not a design element. |

**Look at the image before choosing it.** Download the thumbnail and actually
view it. Metadata cannot tell you that the subject is jammed against the top
edge, or that a tree is in front of the house.

**Take Wikimedia thumbnail URLs from the API, never hand-build them.**
Wikimedia serves only bucketed widths; a hand-written `1600px-…` URL 400s
while the API's `1920px-…` works. Request `iiurlwidth=1920` and copy the
`thumburl` verbatim. Use the original file URL only when it is already
modestly sized.

## Reading a Commons licence

One API call gives you everything you need to fill the credit honestly:

```
https://commons.wikimedia.org/w/api.php?action=query&format=json
  &titles=File:<Exact File Name>
  &prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920
```

From `extmetadata`, read:

- `LicenseShortName` - e.g. `CC BY-SA 4.0`. This goes in the credit.
- `Artist` - the photographer (HTML; take the text).
- `Attribution` - when present, the **exact string the licensor asks for**.
  Prefer it over composing your own from `Artist`.
- `AttributionRequired` - if `true`, a credit is not optional.
- `Restrictions` - e.g. `personality`. Note it in a YAML comment.
- `ImageDescription` - confirm the file is what its filename claims.

To find candidates, list a category
(`generator=categorymembers&gcmtitle=Category:<Author>&gcmtype=file`) or
search files (`generator=search&gsrnamespace=6`). Send a descriptive
User-Agent; Wikimedia rate-limits anonymous scrapers.

## What to do when rights are unclear

In order:

1. Look for the same subject elsewhere on Commons - a second photo of the same
   author or place is common.
2. Consider a **different but honest** subject: a public-domain photograph, a
   building rather than a person, a landscape the books inhabit.
3. Check whether the publisher has a press page with explicit editorial terms.
4. **Leave the field out**, and write one line in the PR naming what you
   rejected and why. A rejected image documented is worth more to the curator
   than a filled field they have to audit.

Never fill a slot with a lower-confidence image because the wing looks empty
without one. Empty is a supported state.

**Leave the gap where the next agent will find it.** A bare slot with no
explanation gets re-searched by every later run. Put a short YAML comment on
the entry saying what you looked for and why it came up empty - a data
decision log, exactly the kind of comment the comment policy (CURATION §2)
permits:

```yaml
- id: stephen-king/six-stories
  title: "Six Stories"
  # No cover: a 1100-copy Philtrum Press limited edition with no Open Library
  # record (checked by title search and by sweeping all 611 works on King's
  # author record). Nothing else is licensable, so the slot stays empty.
```

A comment is the right vehicle: it is inside your remit, whereas adding a
`note:` field edits content a curator owns. Some categories are *expected* to
come up empty - limited editions and chapbooks, Kindle-only novellas,
self-published serials, anything never finished. Finding no cover for those is
a correct result, not a failed search.

## Sparse and non-English franchises

The Stephen King case is the easy one: an anglophone bestseller with
near-total Open Library coverage. Expect worse, and do not treat worse as
failure.

- **A Portuguese or otherwise sparse author** may have covers for a handful of
  works and none for the rest. Ship the handful; partial coverage is a
  first-class outcome. Report the fraction in the PR.
- **Search Open Library in the original language too** - the record may exist
  under the published title rather than a translation of it.
- **A living author with no free portrait is normal**, and no photo is correct
  where no licence is clear. Do not substitute a book cover, a statue, or an
  AI image for a portrait.
- **Publisher pages** (Wook, Bertrand, Presença for Portugal) are a source for
  *verifying an edition*, not a source of images to hotlink, unless their
  terms say otherwise.

**An empty slot is safe; a broken URL is not.** These are not the same
outcome, though both look like "no cover". A work with no `images.cover`
renders as the designed typographic tile. A work with a cover URL that 404s
renders as the browser's broken-image icon **and stays that way**: the
fallback tile is wired to the img's `onError`, which never fires for an image
that already failed before hydration on a statically rendered page. So a URL
you did not actually load is worse than no URL at all. Fetch every one, follow
the 302 to the CDN, and if it does not resolve to a real image, leave the
field out.

## Process

1. Read `docs/SCHEMA.md` (Images) and the franchise's `works.yaml`,
   `editions.yaml`, and `content/authors/<slug>.yaml`.
2. Resolve every work to an Open Library work id - from `externalIds`, else by
   title search, else by sweeping the author's works list - and **verify each
   match** against the traps above.
3. Pull `cover_i` for each, build the cover URL, **fetch every one with
   `?default=false`**, then **build a contact sheet and look at all of them**:
   reject retailer watermarks outright, replace degraded library scans from
   the work's other editions.
4. Find the portrait on Commons; read the licence metadata; look at the image.
5. Write the `images` blocks. Quote every URL. Comment any slot deliberately
   left bare, and any rights nuance that needs explaining.
6. Run `python scripts/validate.py` until green. Check that the number of
   unique cover URLs equals the number of covered works - a duplicate means a
   franchise image got repeated or a work resolved to the wrong record.
7. Write the PR body: coverage as n/total, the source and licence breakdown,
   every image rejected on rights grounds, every slot left bare and why, and
   any data error you found but did not fix.

## Hard rules

- **Touch only image blocks.** Not prose, not ids, not `externalIds`, not
  `sources`. A visual-metadata PR that edits a synopsis is a PR a curator has
  to re-review from scratch.
- **One cover per work, keyed to a real record.** Never repeat a franchise
  image across works to raise the coverage number.
- **Every `*` image field needs its `*Credit`.** The validator enforces this;
  the licence enforces it harder.

## Done means

A green `scripts/validate.py`, every image URL fetched with `?default=false`
and confirmed to serve a real image, **every image looked at** and cleared of
retailer watermarks, every credit traceable to a licence you actually read,
every deliberate gap commented in place, and a PR body that states the
coverage fraction, the licence breakdown, what you rejected, and what you
found broken but left alone. A wing with honest gaps ships; a wing with one
unlicensed image does not.
