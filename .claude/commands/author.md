---
description: Populate a new author wing or update an existing one - inspect the wing's state, plan only the stages it needs, run each curation agent in dependency order with explicit handoffs, and merge a verified result to main.
argument-hint: <author or franchise> [--slug <slug>] [--stages <s1,s2>] [--locales pt-PT,...]
---

# /author

Bring the wing for **$ARGUMENTS** to a complete, sourced, verified, illustrated
and translated state - whether it exists yet or not.

Each stage is an agent with its own skill file, and **those skill files are the
source of truth for how the work is done.** `docs/CURATION.md` is the working
contract every stage runs under; `docs/SCHEMA.md` is the data contract. This
command owns only what no single agent can see: **which stages this wing needs,
what order they run in, what they hand each other, and what has to be true
before the next one starts.**

You are the orchestrator. You do not do the stages' work. You plan from the
wing's real state, sequence the agents, carry the handoffs, verify the
artefacts, and collect the curator's decisions.

**Bringing existing wings up to date with the world is `/refresh`.** It shares
every stage here and adds only `whats-new`; it differs in the question it asks
(what changed since we last looked, across the catalogue) rather than in how
the work is done. Use it for recurring maintenance; use this command to build
or complete a wing.

## Plan from state, not from a script

The pipeline is the same for a new author and an update - what differs is which
stages fire. Before launching anything:

1. **Resolve the slug** (`content/franchises/<slug>/`; reuse an existing one,
   else lowercase-hyphenated, accents stripped; ids are permanent).
2. **Record the baseline**: `python scripts/validate.py`,
   `python scripts/i18n_coverage.py`, `python scripts/event_density.py`,
   `python scripts/aura_density.py`. Every later claim of progress is measured
   against these numbers.
3. **Read the wing** (all of it, if it exists) and **build the stage list**
   from the trigger table:

| Stage runs when | Stage |
|---|---|
| the wing exists and you do not already know what changed since it was last curated | `whats-new` (read-only; routes the rest) |
| the wing does not exist, or its structure is being redrawn | `franchise-research` (scaffold) |
| always on a full run; on update, when the bibliography is suspect or last verified before new works could exist | `completeness-auditor` |
| always on a full run; on update, when the aura is thin, flat, or has never had a press pass | `press-archaeology` |
| the author extends the catalogue's span, or publishes in a decade `global.yaml` leaves empty | `world-events` |
| eras carry `provenance: none`, unsourced boundaries, or works orphaned outside every span | `eras` |
| discovery for orders/entry paths has never actually run, works changed since orders were written, or startHere predates the current order set | `reading-orders` |
| `world-events` ran, or `globalEvents` include/exclude has never been ruled on | `event-resonance` |
| any prose was added or changed upstream | `spoiler-audit` |
| works were added, covers/editions coverage is stale against the work list, or slots are empty with no documented reason | `visual-metadata`, `editions` |
| any prose was added or changed (runs last) | `translation` (per locale) |
| a full run; or any run that touched three or more layers | `wing-audit` |

`--stages` overrides the plan; say in the report that it did.

**A stage skipped because its inputs are unavailable is a result; a stage run
without its inputs is damage.** `press-archaeology`, `eras` and `reading-orders`
are discovery stages whose skills forbid coining - run blind, they convert a
missing input into invented canon that looks identical to researched canon. If
web search or an archive is unavailable, skip the stage, record why in the run
report, and leave the wing honestly flagged. Never leave the record of the skip
in the content files themselves (see the comment policy in CURATION.md).

## The two rules that matter most

**1. Stages that write the same file must not run in parallel.** Learned
expensively: completeness and visual-metadata once ran concurrently on the same
`works.yaml`, and the naive merge would have shipped covers for only the
pre-audit works while looking complete.

**2. Agents cannot see each other's work. You are the channel.** Every stage
writes a handoff; every stage reads the ones before it. A stage that does not
know 18 works were just added will silently skip them, and the gap will look
like completion.

## File footprints

Parallel groups are parallel *because* their members touch different files.

| Skill | Writes |
|---|---|
| `franchise-research` | everything (scaffold, runs alone) |
| `completeness-auditor` | `works.yaml` |
| `press-archaeology` | `authors/<id>.yaml`, `events.yaml` |
| `world-events` | `events/global.yaml` |
| `eras` | `eras.yaml` |
| `event-resonance` | `franchise.yaml` (`globalEvents`) |
| `reading-orders` | `orders.yaml`, `franchise.yaml` (`startHere`) |
| `spoiler-audit` | cross-cutting: works, events, characters, authors, orders |
| `visual-metadata` | `works.yaml` (images), `franchise.yaml` (header), `authors/<id>.yaml` |
| `editions` | `editions.yaml` |
| `translation` | `content/i18n/<locale>/**` only |
| `whats-new` | read-only, plus repairing a rotted source URL in place |
| `wing-audit` | read-only, plus trivial mechanical fixes |

Collisions that are easy to miss: **`event-resonance` and `reading-orders` both
write `franchise.yaml`** (run them sequentially, resonance first - startHere
needs the final order set to point at), and **`spoiler-audit` and
`visual-metadata` both write `works.yaml`**. Never pair either.

## Model and effort per stage

Set these on the `Agent` call. **Skill frontmatter carries no model field and
nothing reads one** - writing it there would be inert data that looks like
configuration, which is the failure this pipeline documents everywhere else.

Tier by **failure mode, not by how much searching a stage does.** The
expensive stages here are the ones deciding *what not to write*, and their
errors are silent and green.

| Stage | Model | Effort | Why |
|---|---|---|---|
| `franchise-research` | sonnet | high | Sets ids and tiers that are permanent. |
| `completeness-auditor` | sonnet | high | First-publication vs the edition that sold is subtle source-criticism; a wrong year silently reorders every reader's walk. |
| `press-archaeology` | sonnet | high | Two independent sources on living people's health, money and legal trouble. Judgment, not lookup. |
| `world-events` | sonnet | medium | Small output, high bar: every entry renders on every wing. |
| `event-resonance` | haiku | medium | Genuinely narrow. The engine already filtered by lifetime; the agent writes one sentence or excludes, and the default is exclude. |
| `eras` | opus on a first build, else sonnet | high | The largest editorial claim we make, rendered full-bleed as if received. Telling received framing from our own opinion is the hardest call in the repo - but that call is made once. Adding a sourced era to a settled scheme is sonnet work. |
| `reading-orders` | sonnet | high | Admission tests plus the prequel spoiler vector. |
| `spoiler-audit` | opus | high | Asymmetric and permanent: a false negative ruins a first read forever, and the agent must reason about what a reader has *not* read yet. |
| `visual-metadata` | sonnet | low | Mostly mechanical fetching, but a watermarked scrape or an omnibus cover passes every automated check. Cut effort, not tier. |
| `editions` | sonnet | medium | Check digits are arithmetic; a valid-but-wrong ISBN is a reader's money. |
| `translation` | sonnet | high | pt-PT register is subtle and this layer has shipped Brazilianisms before. |
| `whats-new` | sonnet | medium | Bounded discovery, but a missed death or a missed book silently ages the whole wing. |
| `wing-audit` | opus | xhigh | The critic. Its entire value is catching what every other stage missed. |

**Prefer lowering `effort` over lowering the tier.** Sonnet at low effort is
usually cheaper and safer than a smaller model at default: you keep the
judgment and cut the deliberation. Reserve haiku for work whose failures are
loud.

**Opus is the budget.** On the Valter Hugo Mãe build the three Opus stages were
26% of the tokens and comfortably over half the cost, and `eras` alone burned
425k because it ran twice. Before setting `opus`, ask what specifically goes
wrong at sonnet/high: for `spoiler-audit` and `wing-audit` the answer is
concrete and permanent, so they stay. `eras` earns it on a first build, where
the periodisation is being decided; it does not earn it on a re-run that is
adding one sourced era to a scheme already settled.

## Cost is context times tool calls

Every tool call re-sends the agent's whole context, so an agent's cost is
roughly its context multiplied by how many calls it makes. That reframes what
is expensive: on the Valter Hugo Mãe build, 14 agent runs made **983 tool
calls** at ~3.7k tokens each. The pages fetched were not the expense; fetching
them one per call was. Shared docs are ~9k tokens all told and re-reading them
is a rounding error - do not optimise there.

Four rules follow, and they cut far more than trimming prompts does:

1. **Batch the fetching.** `scripts/fetch.py` takes many URLs in one call,
   caches to `.cache/fetch/` so a later stage inherits what an earlier one paid
   for, sends the browser User-Agent the trap registry requires, and prints a
   bounded extract (`--grep`, `--max-chars`) instead of a whole page. The
   editions stage made 144 sequential fetches; that is one call's worth of work.
   Tell every stage that searches or verifies links to use it.
2. **Orient with `scripts/wing_digest.py <slug> --for <stage>` before reading
   the wing.** It renders a finished wing in ~2.4KB against ~98KB of YAML, and
   answers "which works still lack a cover / an edition / an era" directly.
   Read the actual entries you are about to edit; do not read the other 90%.
3. **Never resume an agent to correct it.** A resume replays the entire
   transcript: the two corrections on that build cost 434k, *more* than the
   original runs. Spawn a fresh, narrow agent with just the delta and the
   evidence, and say what not to reopen.
4. **Prefer a constructed URL to a search.** Publisher product pages follow a
   pattern. A WebSearch that only finds a URL you could have built costs
   several thousand tokens for nothing.

## Cheap checks before expensive stages

A stage that runs and correctly changes nothing has still been paid for:
`world-events` cost 188k to return a defended zero-diff. Before launching any
stage whose trigger is a judgement rather than a fact, spend the two thousand
tokens that would settle it - `event_density.py` for an empty decade,
`aura_density.py` for a dark run, `wing_digest.py --missing cover|edition|era`,
a `grep` of `global.yaml` for the region in question. Decide from the numbers,
then launch or record the skip. **Skipping a stage on evidence is a result and
belongs in the run report.**

Your own context is part of this too: you re-send it on every call for the
whole run. Read with `grep -n -A5` and the digest rather than opening whole
files, and keep stage prompts to what the agent cannot infer from its skill.

**The haiku-shaped job is verification, not curation.** A sweep that fetches
every `sources` URL and every image URL in a wing and reports dead links,
blank OpenLibrary placeholders, wrong ISBN region prefixes and failed check
digits needs no taste, parallelises freely, and fails loudly. Run it as a
cheap final pass before integration; do not hand it any editorial decision.

## Stage order

Within one run, stages that fire execute in this order:

1. **`franchise-research`** - scaffold only (new wing or restructure). Gate:
   validator green, capability set is a deliberate choice.
2. **`completeness-auditor`** - before anything that annotates works, because
   it changes how many exist. Gate: **the work list is final.** A late work
   costs a re-run of stages 3-7.
3. **Enrichment, parallel**: `press-archaeology` · `world-events` · `eras`.
   Gate: validator green, all merged into the stage branch,
   `event_density.py` re-run if `world-events` ran, and `aura_density.py`
   re-run: a wing with a dark run of five or more publishing years has not
   finished this stage, whatever the entry count says.
4. **Franchise judgement, sequential**: `event-resonance`, then
   `reading-orders`. Gate: every `globalEvents`, order and path id resolves.
5. **`spoiler-audit`**, alone - after all prose exists, before translation
   (translation copies prose; a spoiler fixed after must be fixed twice and
   the second fix is the one that gets forgotten). Gate: validator green;
   when in doubt this stage redacts and says so.
6. **Artefacts, parallel**: `visual-metadata` · `editions` - after the work
   list and all prose are final. Read stage 2's handoff: newly added works are
   exactly what gets missed. Gate: validator green, every image URL fetched
   and confirmed real.
7. **`translation`**, one agent per locale - last, because it copies whatever
   the earlier stages settled. Gate: `i18n_coverage.py` shows no regression
   against the baseline, **and** every stale overlay named in a handoff was
   re-synced (coverage cannot see staleness).
8. **`wing-audit`** - the critic. Its output is the next round of work, routed
   to the owning skill. It does not do everyone's job.

## The handoff contract

Each stage writes `.orrery/<slug>/<stage>.yaml` on its branch before finishing:

```yaml
stage: completeness-auditor
summary: "77 works -> 95"
produced:
  newWorkIds: [stephen-king/elevation]
  changedProse: [stephen-king/insomnia]
  changedDates: [stephen-king/the-eyes-of-the-dragon]
forStages:
  visual-metadata: "18 new works need covers"
  translation: "18 synopses need pt-PT"
openQuestions:
  - "Eyes of the Dragon redated 1987 -> 1984; this reorders the default order."
```

**Every agent's first instruction is to read `.orrery/<slug>/` in full; its
last is to write its own file and confirm it parses** (`validate.py` errors on
an unparseable handoff - one stage once wrote invalid YAML and the next stage's
silent gap looked like completion). Pass the relevant `forStages` lines into
the next agent's prompt too; a file it must remember to read is weaker than a
brief it cannot miss.

Handoffs are branch-local working state, not canon: **delete `.orrery/` before
the final merge.** Process history lives in the run report, commit messages and
git - never in content-file comments.

## Worktrees and merge

One worktree per agent, branched from that stage's base:
`git worktree add ../wt-<slug>-<stage> -b <slug>/<stage> <base>`.

Integration is yours - do not delegate it:

1. Merge every stage branch in pipeline order into one integration branch.
   **Re-read every branch tip immediately before final validation** - agents
   keep committing after they report done (one carried 17 lines of real
   `editions.yaml` after its completion notice). The check is
   `git merge-base --is-ancestor <branch> <integration>` on every stage branch.
2. `validate.py`, `i18n_coverage.py`, `event_density.py`,
   `aura_density.py` - clean, no regression, and **read the warnings**,
   including the comment-policy scan and any dark run.
3. **Build the app against the merged content and run its suite.** The content
   validator cannot catch an app-side break, and twice it has not.
4. **Check the rendered pages with `node scripts/render-check.mjs`** (in the
   app repo), never with a browser. The pages are statically generated, so
   every word and every image URL a reader gets is in the markup: the script
   fetches each wing in each locale and reports dead routes, `<img>` sources
   that do not resolve, declared `lang` mismatches, base-language leakage and
   pages that render almost no text. Serve
   `node .next/standalone/server.js` with `.next/static` copied in first -
   `next start` does not apply the proxy under `output: standalone`.
   **Do not drive a browser to verify content** (see CURATION.md §5).
5. Delete `.orrery/`, merge to `main` directly (content is validator-gated
   data; review adds latency - the standing rule), push, bump the app's
   content submodule, and keep the deployment current.

## Verify the agents, not just the content

The full doctrine is `docs/CURATION.md` §5 - check artefacts, not reports;
falsify guards; grep the app for the code that reads any field you rely on;
treat suspiciously complete numbers as a reason to look harder; diff even
"nothing changed" results. It is not optional and every clause on it was paid
for. Two command-level specifics:

- **Re-verify convenience data handed down a handoff** - a fact from an
  upstream stage is a lead, not a source.
- **A wing that reports 100% on everything has almost certainly hidden
  something.**

## The run report (the deliverable to the curator)

Collect from every handoff into one report, delivered to the curator at the
end - not buried across branches, and never written into content files:

- what ran, what was skipped and why, and what each stage changed;
- every rejection with its reason;
- corrections to received wisdom, flagged loudly if the wrong version was live;
- `openQuestions` merged into one decision list: ordering changes, naming and
  grouping, scope, rights judgement calls, and anything an agent flagged as
  its own weakest decision. **Never quietly ratify those.**

## Done means

The bibliography is verified against primary sources and its gaps documented
rather than invisible. The aura is sparse, dated and sourced. Eras and entry
paths are received rather than coined. Spoilers are bounded with the asymmetry
respected. Imagery is licensed and credited, or honestly absent. Every locale
is at full coverage and renders correctly. The app builds and its tests pass
against the merged content, the wing is on `main`, and the deployment matches.
The curator has one short list of decisions that were genuinely theirs to make.

**The honest artefact of a complete author includes the covers that do not
exist, the dates the record will not settle, and the archives that would not
open.**
