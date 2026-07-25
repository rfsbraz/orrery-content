# Karin Slaughter - visual metadata handoff

## Cover coverage: 28/43

Source: Open Library, via `scripts/metadata/lookup.py karin-slaughter --author
"Karin Slaughter" --json` (one call, ~40 requests) for 25 of the 28, plus
targeted `search.json` and `editions.json` calls for three titles the author-
search page missed entirely (The Silent Wife, The Unremarkable Heart and
Other Stories, Blonde Hair Blue Eyes - the latter two actually resolved to no
usable cover; only Silent Wife got one). No hand-fetching of individual
candidate pages beyond that. Every one of the 28 final URLs was fetched with
`?default=false` on a fresh (non-cached) pass and confirmed to serve a real
image, and all 28 were tiled into a contact sheet and looked at.

Two catches from actually looking at the images, not just the HTTP check:

- **Broken**: the top-ranked candidate (cover id 9843704) rendered as a scan
  of a page of prose, not a jacket. Replaced with cover id 6424942 (Delacorte
  Press 2010), the correct dust-jacket image, same ISBN family.
- **The Unremarkable Heart and Other Stories**: its only Open Library edition
  (a Playaway preloaded-audio device) points at a blank "no image available"
  placeholder that still returns HTTP 200 past `?default=false`. Left bare
  rather than shipped.

## Deliberate absences (15), with reason

- **The Secrets We Hide**: not yet published; no jacket exists to fetch.
- **Martin Misunderstood, Thorn in My Side, Necessary Women, The Mean Time,
  The Truth About Pretty Girls, Go Deep, Remmy Rothstein Toes the Line, Cold
  Cold Heart, The Blessing of Brokenness, Short Story (the Koryta crossover),
  Snatched, Busted, Last Breath**: real, verified Open Library editions
  (checked by ISBN and by work record) exist for all of these, none carry
  jacket art. This matches the skill's expectation for paperback-exclusive
  bonus chapters and digital-only shorts.
- **The Unremarkable Heart and Other Stories**: see above (placeholder, not
  absence-of-record).

No omnibus, audiobook-jacket, or watermarked/retailer-scraped image was used
anywhere in the 28; all are trade hardcover/paperback jackets from William
Morrow, Delacorte, HarperCollins or their imprints. Two are the only edition
Open Library holds and happen to be large-print jackets (The Last Widow,
HarperLuxe; This Is Why We Lied, a large-print banner is visible on the
cover) - noted in-file as comments rather than silently passed off as a
standard trade jacket.

## Portrait: yes

Karin Slaughter 2012 studio portrait (Alison Rosa), Wikimedia Commons,
`{{Cc-by-sa-3.0-de}}` with an OTRS/VRT permission ticket on file confirming
the copyright holder's release. Chosen over six press-event photos (BookExpo
2019, Helsinki Book Fair 2009, a 2010 German reading) because it is already
framed as a head-and-shoulders portrait rather than a wide event shot the app
would have to blind-crop.

## Franchise header: yes

Kudzu smothering trees, photographed in Piedmont Park, Atlanta (Scott Ehardt,
public domain). Chosen over a Covington/Newton County courthouse square shot
(Slaughter's hometown, matches the Grant County motif) because that photo's
frame includes a storefront dressed for "The Vampire Diaries" - an unrelated
show's set dressing in the one open, high-resolution image found of that
square. Kudzu is the wing's own named motif (theme.yaml `art.motifs`) and the
photo location (Atlanta) ties both halves of the catalogue rather than
favoring Grant County or Will Trent alone.

## Nothing for editions/translation

No `editions.yaml` exists for this wing (per the scaffold), so no per-edition
`coverUrl` was touched; every cover above lives on the work's own
`images.cover`, the field the app actually reads.
