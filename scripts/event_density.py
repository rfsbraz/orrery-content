#!/usr/bin/env python3
"""Report aura-event density against the density budget.

A global event renders on EVERY franchise's timeline, and high-impact events
render as full-bleed interruptions, so the global layer must stay sparse. This
reports the distribution the world-events skill is graded against.

Usage: python scripts/event_density.py
"""
import collections
import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_DECADE_MAX = 3
HIGH_EVERY_N_YEARS = 25


def load(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    years = []
    for f in glob.glob(os.path.join(ROOT, "content", "franchises", "*", "works.yaml")):
        for w in load(f) or []:
            if isinstance(w.get("published"), int):
                years.append(w["published"])
    span = (min(years), max(years)) if years else (0, 0)

    gpath = os.path.join(ROOT, "content", "events", "global.yaml")
    events = (load(gpath) or {}).get("events", []) if os.path.exists(gpath) else []

    by_decade = collections.Counter()
    by_impact = collections.Counter()
    for e in events:
        year = int(str(e.get("date", ""))[:4] or 0)
        by_decade[(year // 10) * 10] += 1
        by_impact[e.get("impact", "?")] += 1

    decades = (span[1] - span[0]) // 10 + 1 if years else 0
    high_budget = max(1, (span[1] - span[0]) // HIGH_EVERY_N_YEARS) if years else 0

    print(f"catalogue span : {span[0]}-{span[1]} ({decades} decades, {len(years)} works)")
    print(f"global events  : {len(events)}")
    print(f"by impact      : {dict(by_impact)}")
    print(f"high budget    : {by_impact['high']} used of ~{high_budget} "
          f"(one per {HIGH_EVERY_N_YEARS} years)")
    if by_impact["high"] > high_budget:
        print("  OVER BUDGET - re-grade the weakest high-impact entries down")

    print("\nper decade (budget %d):" % PER_DECADE_MAX)
    for d in range(span[0] // 10 * 10, span[1] + 1, 10):
        n = by_decade.get(d, 0)
        flag = "  OVER" if n > PER_DECADE_MAX else ("  (empty)" if n == 0 else "")
        print(f"  {d}s  {'#' * n}{'' if n else '-'}{flag}")


if __name__ == "__main__":
    # sys.exit(main()) so a non-zero return actually reaches the shell; bare
    # main() swallowed it and every run looked successful.
    sys.exit(main() or 0)
