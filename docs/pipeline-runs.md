# Pipeline runs

One row per `/author` run, written by `pipeline-audit` as its last act. One run
tells you which stage was expensive *that time*; three tell you which stage is
*always* expensive, and only the second is worth rewriting a skill for.

| date | wing | works | tokens | calls | stages | largest finding |
|---|---|---|---|---|---|---|
| 2026-07-26 | john-shirley | 84 | 2,494,974 | 679 | 11 | `visual-metadata` at 170 calls / 1,942 tok per call, the death-by-fetches shape, on a stage whose skill already says to batch. Two footprint violations: `franchise-research` wrote `theme.art`, `press-archaeology` wrote the art grammar onto 8 events. |
| 2026-07-27 | anna-sewell | 1 | 1,790,368 | 458 | 10 | `lookup.py --author` returned 1911 contaminated candidate rows across "52 works", inflating both `editions` (74 calls for 3 editions) and `visual-metadata` (66 calls for 3 images). Second consecutive wing hitting it. Zero footprint violations. |

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
