# Pipeline runs

One row per `/author` run, written by `pipeline-audit` as its last act. One run
tells you which stage was expensive *that time*; three tell you which stage is
*always* expensive, and only the second is worth rewriting a skill for.

| date | wing | works | tokens | calls | stages | largest finding |
|---|---|---|---|---|---|---|
| 2026-07-26 | john-shirley | 84 | 2,494,974 | 679 | 11 | `visual-metadata` at 170 calls / 1,942 tok per call, the death-by-fetches shape, on a stage whose skill already says to batch. Two footprint violations: `franchise-research` wrote `theme.art`, `press-archaeology` wrote the art grammar onto 8 events. |
| 2026-07-27 | anna-sewell | 1 | 1,790,368 | 458 | 10 | `lookup.py --author` returned 1911 contaminated candidate rows across "52 works", inflating both `editions` (74 calls for 3 editions) and `visual-metadata` (66 calls for 3 images). Second consecutive wing hitting it. Zero footprint violations. |
| 2026-07-27 | jk-rowling | 37 | 3,063,563 | 1,201 | 13 (+3 follow-ups) | Cross-book spoiler leaks found by fix-cascade, not audit: wing-audit (opus/xhigh, reads the whole wing end to end) flagged only Order of the Phoenix; Half-Blood Prince surfaced only because the OotP follow-up noticed it in passing, requiring a third agent dispatch to sweep the series (121,519 tokens / 48 calls across the two follow-ups). spoiler-audit's own opus/high pass had explicitly logged both books as "confirmedSafeUnchanged". Propose wing-audit's brief require sweeping sibling entries for the same failure-mode pattern the moment one instance is found, rather than flagging the single instance and letting a follow-up discover the sweep was needed. Zero footprint violations (clean sequencing on all three known collision pairs: event-resonance/reading-orders, spoiler-audit/visual-metadata, art-rotation/visual-metadata); zero pipeline-narration-in-comments violations. |
| 2026-07-28 | miguel-de-cervantes | 8 | 2,076,399 | 800 | 13 | wing-audit (opus/xhigh) caught two BLOCKING factual errors no earlier stage's cross-check found, despite each fact being individually sourced in its own file: press-archaeology's captivity lifeEvent (bfbdcbb) wrongly credited El cerco de Numancia to the Algiers captivity alongside El trato de Argel, when only the latter draws on it; and the bio, era and lifeEvent each gave the 1592/1597 imprisonments a different cause. Both harmonized post-merge by the orchestrator directly on the wing-audit branch (b775834), both locales, alongside two smaller tightenings (07a2c28 comment-sanctuary cleanup; f571d27 fixed reading-orders' own order-of-magnitude slip - "decades" for a 168-year gap - and a spoiler-safety verb). Zero footprint violations found across all 13 stages (one trivial exception noted: press-archaeology's bfbdcbb also fixed a 1-line dead source URL in works.yaml, outside its declared footprint but immaterial); every triggered stage left a commit-level record, including wing-audit itself, which has no handoff file and is recorded only in its own fix commits. |
| 2026-07-28 | robert-bryndza | 25 | 2,489,107 | 963 | 13 | Corrections don't propagate sideways: `press-archaeology` fixed "sold a million copies within five months" to "within a year" in 3 files but never touched `eras.yaml`, which had independently written the same wrong figure from the same About-page source one stage earlier - only `wing-audit` caught the drift. Separately, `editions`' synopsis-match notes reintroduced 3 details `spoiler-audit` had deliberately cut (devils-way's near-drowning, coco-pinchard-the-consequences's remarriage, chasing-shadows's identity), because `editions` runs after `spoiler-audit` and never reads its rewrites - inert today (`edition.note` renders nowhere) but a live trap. Zero footprint violations; opus spend (`eras`, `spoiler-audit`, `wing-audit`) matched real catches. |

## What two runs already show

**Cost is not shelf-size-sensitive.** A 1-work wing cost **72%** of an 84-work
wing. No stage came near the ~1.2% a proportional cost would predict; the
best-scaling one, `editions`, still cost 58% while making *more* calls.

**Two stages are anti-correlated with wing size** - they cost *more* on the
smaller wing:

| stage | john-shirley | anna-sewell | tokens | calls |
|---|---|---|---|---|
| `visual-language` | 137,438 / 17 | 157,127 / 35 | +14% | +206% |
| `art-rotation` | 149,668 / 21 | 163,455 / 42 | +109% | +200% |

The evidenced mechanism, from `visual-language`'s own run record, is a
catalogue-wide sweep: it checked its `lineCharacter` "against all 19 other
wings". That cost scales with the **catalogue**, not the wing, so it grows on
every future wing no matter how small. `art-rotation`'s doubling has the same
shape but is not yet confirmed to the same standard.

This is the sharpest thing the ledger has produced, and it is only visible
across runs - a single run would have read those two as ordinary mid-cost
stages.

**Skipping well is cheaper than running everything.** The Sewell run skipped
three stages on judgement and one silently. `eras` was the largest single
saving of the run - written directly because a one-book career cannot have
creative periods, which is arithmetic rather than discovery, against 195,614
tokens when the same stage ran as an agent on Shirley. That saving came from
the orchestrator's own initiative and is not yet written into any skill.

## Findings, and what was done about them

Eleven findings came out of the two runs. All eleven are now closed, seven of
them by changing a skill or a script rather than by asking anyone to remember
something.

| # | finding | outcome |
|---|---|---|
| 1 | `visual-language` reads every wing's `theme.yaml` to place itself against the catalogue - a cost that grows with the catalogue, not the wing | `scripts/theme_digest.py`: the collision axes in ~8.5KB against ~126KB, then read in full only the wing it shows you are adjacent to |
| 2 | Eleven catalogue-wide validations in one wing build where ten could have been scoped | `--slug` bullet in the shared tooling block now carries the measured cost |
| 3 | `visual-metadata` sources `images.header` into `franchise.yaml`, which nothing read | Kept, and the app now renders it (orrery#131). The stage was right and the app was behind |
| 4 | `eras` cost 195,614 tokens as an agent on an 84-work wing and ~0 written directly on a 1-work one | `author.md` bypasses the stage when the shelf is one or two works, where the answer is arithmetic |
| 5 | `translation` is wing-scoped but `world-events` appends to a shared file, so a run can leave `global.yaml` short a locale | `translation`'s scope now explicitly includes any shared file the run touched |
| 6 | Global events were being written that no author in the catalogue could reach | `world-events` now asks whether any author actually reaches an entry before committing it |
| 7 | A stage skipped without a record is indistinguishable from a stage that failed | `pipeline-audit` gained a silent-skip detector; the silence is the failure, not the judgement |
| 8 | `lookup.py --author` returned 1,911 contaminated candidate rows across two consecutive wings | `by`/`same_author` columns, an `--author-only` flag, and a stderr warning naming the contaminating authors |
| 9 | OpenLibrary's ASCII-only URL construction dropped diacritics and Norwegian titles | Fixed in `providers.py`, with a regression test that captures the provider's real URL rather than rebuilding it |
| 10 | Six wings name a `displayFace` or `signature` the app does not implement, so their argued branding renders as the default | Two implemented (`instrument-serif`, `filament`, orrery#131); the validator's sets now track `lib/theme.ts`. Four remain, blocked on decisions rather than on work |
| 11 | `Franchise.images` was set by 15 wings but absent from the app's interface and rendered nowhere | Declared and rendered, with the credit, since several are CC BY (orrery#131) |

**A correction to finding 10 as first written.** It was recorded as the app
discarding branding "with nothing reporting it". That was wrong: `validate.py`
had been warning on all eight values by name, on every run, with the
consequence spelled out. The failure was never detection - it was that the
warning sat among 77 others and no one reads a 77-line list. So the fix is two
things, not one: the sets now track the app, and an unscoped run rolls its
warnings up by kind. The rollup earns its place immediately - **41 of the 77
are a single class** (pipeline narration in content comments), which is more
than half the catalogue's standing debt hiding in plain sight as sixty-odd
unrelated-looking lines.

The general lesson is worth more than the specific fix: a check nobody reads is
not a check, and a long warning list is how a correct check becomes invisible.
