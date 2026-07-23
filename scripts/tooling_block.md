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
  reference crosses wings - only the warning list narrows),
  `aura_density.py <slug>`, `wing_digest.py <slug>`, `asset_audit.py <slug>`,
  `stage_plan.py <slug>`. `event_density.py` has no slug on purpose: it measures
  the shared `global.yaml` budget, which is catalogue-wide by nature.
- **Build the URL instead of searching for it.** Publisher product pages and
  catalogue records follow patterns. A search whose only output is a URL you
  could have constructed costs thousands of tokens for nothing. Search when you
  need to discover *that* something exists; fetch when you know where it is.

None of this licenses thinner research. It buys the same evidence for less, so
that the budget goes on judgement instead of on transport.
