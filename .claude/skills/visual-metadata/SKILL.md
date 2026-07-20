---
name: visual-metadata
description: Source and record the imagery a franchise wing needs - author portraits, franchise headers, and per-work covers - with defensible rights on every one. Use when adding or refreshing the images blocks in content/authors/<slug>.yaml, content/franchises/<slug>/franchise.yaml, or works.yaml.
---

# visual-metadata

Fill the `images` blocks that turn a franchise wing from a list into a shelf:
one **portrait** per author, one **header** per franchise, one **cover** per
work. Output is git YAML, reviewed by a curator via PR.

**Read the "Images (visual metadata)" section of [`docs/SCHEMA.md`](../../../docs/SCHEMA.md)
first** - it is the contract, and `scripts/validate.py` enforces it. This skill
is how to *fill* it without shipping a legal problem.

## Why this matters

Orrery is a museum walk. Without imagery it is text on dark ground: correct,
complete, and dead. Covers are how a reader recognises the shelf they already
own, headers are how a wing announces itself, and a portrait is how the aura
layer stops being abstract. The pictures are not decoration; they are the
difference between reading a catalogue and walking a collection.

But images carry **rights**, and a books site that hotlinks scraped jackets is a
takedown waiting to happen. So the job is not "find the prettiest image". It is
**find a good image whose rights you can state in one line**, and write that
line down.

## The source ranking

Work down this list. Do not skip to a lower tier because it looks nicer.

**1. Open Library covers** - `https://covers.openlibrary.org/b/id/<coverId>-L.jpg`

The default for covers, and the reason the app already treats
`covers.openlibrary.org` as its cover CDN (the service worker caches it). Open
Library hosts publisher jacket art and permits hot-linking; credit is
`"Open Library"` and the source is the OL **work** page you took the id from.

**2. Wikimedia Commons** - the default for portraits and headers.

Every file has a real, checkable licence. Never assume it: read the file's
`extmetadata` and record what it says (see "Reading a Commons licence" below).
Most usable files are CC BY, CC BY-SA, or public domain.

**3. Publisher press / media kits** - only where the page's own terms explicitly
permit editorial use. Cite the terms page in `*Source`, not just the image.

**Never**: Google Images, Goodreads, Amazon or any retailer's jacket file, fan
wikis, Pinterest, or a reverse-image-search result whose origin you cannot name.
An image with no discoverable licence is not a candidate.

## Rights rules (the hard part)

- **Never invent a credit.** If you cannot name who made an image and under what
  licence, you do not have the rights to use it.
- **Never invent a URL.** Fetch every URL you write and confirm it returns an
  image. A 404 in a content PR is a fabrication that happens to be honest.
- **Unclear rights means empty.** A missing cover is a design gap; a stolen
  cover is a legal one. The app degrades to typographic covers and text headers
  by design - that fallback exists precisely so you never have to guess. Leave
  the field out and say so in the PR.
- **Attribution is a field, not a footnote.** `*Credit` must carry everything the
  licence demands - author and licence name at minimum
  (`"Kevin Payravi / WikiPortraits, CC BY-SA 4.0"`). `*Source` points at the
  file's description page, where a reader can verify the claim.
- **Share-alike does not infect the site.** Displaying a CC BY-SA image is not
  creating a derivative work, so BY-SA files are fine; they just require
  attribution like any BY file. Do not reject them out of caution.
- **Watch for personality rights.** Commons flags some portraits
  `Restrictions: personality`. Editorial use on the subject's own author page is
  the intended case; never use such an image in a way that implies endorsement.
- **Never commit binaries.** Images are referenced by URL. `content/` holds no
  image files, ever.

## Covers: keying off editions and ISBNs

The goal is a cover that is really *this work's* cover, not a generic franchise
image repeated. Two paths in:

**Path A - via the work's Open Library id (preferred).** `works.yaml` often
carries `externalIds.openLibrary` (`OL…W`). Query the search API by key to get
the representative cover Open Library itself displays:

```
https://openlibrary.org/search.json?q=key:"/works/OL81626W"&fields=key,title,cover_i,edition_count
```

`cover_i` is the cover id; the image is
`https://covers.openlibrary.org/b/id/<cover_i>-L.jpg`. Prefer this over the
work JSON's `covers[0]`: the work record's `covers` array is sometimes empty
even when a perfectly good edition cover exists, and its first entry is
arbitrary.

**Path B - via an ISBN in `editions.yaml`.** `https://covers.openlibrary.org/b/isbn/<isbn13>-L.jpg`
resolves an edition's own jacket. Use it when a franchise's editions are well
covered on Open Library. **Check the region first**: a `pt-PT` Bertrand ISBN is
usually *not* in Open Library's cover set, so a Portuguese-editions file will
give you almost nothing this way. The Stephen King canary hit exactly this - all
68 editions were `pt-PT`, so every cover came from Path A instead.

**Verify the OL work is the right work.** This is where covers actually go
wrong. Open Library is full of omnibuses, screenplays, and translated records
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
for the image but **do not edit `externalIds`** - that is prose/data outside the
image block. Report it in the PR so the curator or the enrichment bot fixes it.

**Verify every image URL before writing it.** Fetch it and check the status,
content type, and byte size. Open Library returns a tiny placeholder rather than
a 404 for a missing cover, so a size floor (a few kB) is the real test.

## Portraits and headers: dimensions and framing

| Slot | Target ratio | Practical minimum | Notes |
|---|---|---|---|
| `portrait` | 2:3 to 3:4, tall | ~800px wide | Head and shoulders. A crop already framed as a portrait beats a wide press shot the app has to centre-crop blindly. |
| `header` | 3:1 or wider when displayed | ~1600px wide source | Rarely will you find a true panorama. A 4:3 or 3:2 original at high resolution is fine - the app crops a horizontal band, so what matters is that **the subject sits in the middle third vertically** and the source has pixels to spare. |
| `cover` | Whatever the jacket is | Open Library `-L` size | Do not crop or normalise. A cover is a document, not a design element. |

**Look at the image before choosing it.** Download the thumbnail and actually
view it. Metadata cannot tell you that the subject is jammed against the top
edge, or that a tree is in front of the house.

**What makes a good header:** something that reads as the *franchise*, not as
one adaptation. An author's house, a landscape the books live in, a building
that inspired a setting. Avoid film stills and movie logos - they are usually
studio-owned, they date the wing, and they credit the wrong art form.

**Take Wikimedia thumbnail URLs from the API, never hand-build them.** Wikimedia
serves only bucketed widths; a hand-written `1600px-…` URL 400s while the API's
`1920px-…` works. Request `iiurlwidth=1920` and copy the `thumburl` verbatim.
Use the original file URL only when the original is already modestly sized -
a 5712x4284 original as a page header is a 10MB banner.

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
- `Attribution` - when present, this is the **exact string the licensor asks
  for**. Prefer it over composing your own from `Artist`.
- `AttributionRequired` - if `true`, a credit is not optional.
- `Restrictions` - e.g. `personality`. Note it in a YAML comment.
- `ImageDescription` - confirm the file is what its filename claims.

To find candidates, list a category
(`generator=categorymembers&gcmtitle=Category:<Author>&gcmtype=file`) or search
files (`generator=search&gsrnamespace=6`). Send a descriptive User-Agent;
Wikimedia rate-limits anonymous scrapers.

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

## Sparse and non-English franchises

The Stephen King case is the easy one: an anglophone bestseller with near-total
Open Library coverage. Expect worse, and do not treat worse as failure.

- **A Portuguese or otherwise sparse author** may have covers for a handful of
  works and none for the rest. Ship the handful. Partial coverage is a first-
  class outcome; report the fraction in the PR.
- **Search Open Library in the original language too** - the record may exist
  under the published title rather than a translation of it.
- **A living author with no free portrait is normal.** Many authors have no
  Commons photo at all, and no photo is correct where no licence is clear. Do
  not substitute a book cover, a statue, or an AI image for a portrait.
- **Publisher pages** (Wook, Bertrand, Presença for Portugal) are a source for
  *verifying an edition*, not a source of images to hotlink, unless their terms
  say otherwise.

## Process

1. Read `docs/SCHEMA.md` (Images) and the franchise's `works.yaml`,
   `editions.yaml`, and `content/authors/<slug>.yaml`.
2. Resolve every work to an Open Library work id - from `externalIds`, else by
   search - and **verify each match** against the traps above.
3. Pull `cover_i` for each, build the cover URL, and **fetch every one** to
   confirm it is a real image.
4. Find the portrait and the header on Commons; read the licence metadata; look
   at the images.
5. Write the `images` blocks. Quote every URL (they contain `?`, `:`, commas and
   parentheses). Add a YAML comment where a rights nuance needs explaining.
6. Run `python scripts/validate.py` until green.
7. Write the PR body: coverage as n/total, the source and licence breakdown,
   every image rejected on rights grounds, and any data error you found but did
   not fix.

## Hard rules

- **Never fabricate** a URL, a licence, or an attribution. Ever.
- **Touch only image blocks.** Not prose, not ids, not `externalIds`, not
  `sources`. A visual-metadata PR that edits a synopsis is a PR a curator has to
  re-review from scratch.
- **One cover per work, keyed to a real record.** Never repeat a franchise image
  across works to raise the coverage number.
- **Every `*` image field needs its `*Credit`.** The validator enforces this;
  the licence enforces it harder.
- **No em dashes** in anything you write.
- **Quote every URL** in YAML.

## Done means

A green `scripts/validate.py`, every image URL fetched and confirmed to serve a
real image, every credit traceable to a licence you actually read, and a PR body
that states the coverage fraction, the licence breakdown, what you rejected, and
what you found broken but left alone. A wing with honest gaps ships; a wing with
one unlicensed image does not.
