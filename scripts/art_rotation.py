#!/usr/bin/env python3
"""What does this wing's art rotation actually look like?

    python scripts/art_rotation.py <slug>
    python scripts/art_rotation.py <slug> --check     # exit 1 on a violation

docs/VISUAL.md §4a asks every sketch to be composed against its neighbours, and
caps any one composition type at a third of a wing. That is arithmetic, but it
is arithmetic over a whole wing, and until now there was nowhere to do it: the
rotation was planned in a branch-local `.orrery/` file that is deleted before
merge, so the artifact needed to write asset 21 evaporated exactly when the wing
was finished. The Mãe wing shipped seven of eleven as the same close still-life
with nobody able to see it.

So the rotation is DERIVED, not stored. Every prompt is posted as a comment on
its own asset issue and states the four rotation fields it chose, which makes
the issues the single source of truth and this a query rather than a duplicate
that drifts.

Reads the wing's entities for timeline order and the GitHub issues for what was
chosen, then prints the table, the counts, and anything it could not parse -
because a rotation table with three assets silently missing is worse than no
table, and silence is how the still-life problem survived review in the first
place.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "rfsbraz/orrery-content"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A third, expressed the way §4a expresses it.
CAP_FRACTION = 1 / 3


def load(*parts):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def year_of(v):
    s = str(v or "")[:4]
    return int(s) if s.isdigit() else None


def wing_assets(slug: str):
    """(kind, id, title, year) for every asset slot, in timeline order.

    Era plates are listed but excluded from the composition count: §4b fixes
    their composition and they render on their own half-page, so counting them
    would dilute the cap the events actually need.
    """
    base = ("content", "franchises", slug)
    eras = load(*base, "eras.yaml") or []
    events = load(*base, "events.yaml") or []
    works = load(*base, "works.yaml") or []

    out = []
    for e in eras:
        y = year_of((e.get("period") or "").split("-")[0])
        out.append(("era-plate", e.get("id"), e.get("title"), y or 0))

    seen = set()
    for w in works:
        for aid in w.get("authorIds") or []:
            if aid in seen:
                continue
            seen.add(aid)
            a = load("content", "authors", f"{aid}.yaml") or {}
            for e in a.get("lifeEvents") or []:
                out.append(("life-event", e.get("id"), e.get("title"),
                            year_of(e.get("date")) or 0))

    for e in events:
        out.append(("franchise-event", e.get("id"), e.get("title"),
                    year_of(e.get("date")) or 0))

    return sorted(out, key=lambda r: (r[3], r[0]))


# Two accepted forms. The canonical one is what .claude/commands/asset-prompt.md
# now mandates; the prose one is what the first regeneration pass wrote, and
# re-editing sixteen comments to satisfy a parser would be the tail wagging the
# dog.
CANONICAL = re.compile(
    r"composition\s*=\s*(?P<composition>[^|\n]+)\|"
    r"\s*distance\s*=\s*(?P<distance>[^|\n]+)\|"
    r"\s*cast\s*=\s*(?P<cast>[^|\n]+)\|"
    r"\s*carrier\s*=\s*(?P<carrier>[^|\n]+)",
    re.I,
)
PROSE = re.compile(
    r"\*\*composition type (?P<composition>.+?)\*\*.*?"
    r"\*\*distance (?P<distance>.+?)\*\*.*?"
    r"\*\*tonal cast (?P<cast>.+?)\*\*.*?"
    r"\*\*orrery motif carried by (?P<carrier>.+?)\*\*",
    re.I | re.S,
)


def parse_rotation(body: str):
    for pattern in (CANONICAL, PROSE):
        m = pattern.search(body or "")
        if m:
            return {k: " ".join(v.split()) for k, v in m.groupdict().items()}
    return None


def fetch_issues(slug: str):
    """{entity-id: (issue number, rotation dict or None)} in one API call.

    One GraphQL query rather than a list call plus one comment call per issue:
    a twenty-asset wing would otherwise be twenty-one round trips to render a
    table.
    """
    query = """
    query($q: String!) {
      search(query: $q, type: ISSUE, first: 100) {
        nodes {
          ... on Issue {
            number
            title
            comments(last: 1) { nodes { body } }
          }
        }
      }
    }
    """
    q = f'repo:{REPO} is:issue in:title "[art] {slug}:"'
    try:
        raw = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"q={q}"],
            capture_output=True, text=True, check=True, encoding="utf-8",
        ).stdout
    except FileNotFoundError:
        print("gh is not installed - this reads the rotation from GitHub issues",
              file=sys.stderr)
        return None
    except subprocess.CalledProcessError as exc:
        print(f"gh failed: {(exc.stderr or '').strip()[:300]}", file=sys.stderr)
        return None

    out = {}
    for node in json.loads(raw)["data"]["search"]["nodes"]:
        if not node:
            continue
        # "[art] <slug>: <type> - <entity-id>", optionally followed by a
        # parenthetical note. The note is not decoration: "(redraw, off-style)"
        # is how a re-commissioned asset is marked. An earlier version of this
        # regex anchored the id to end-of-line, silently dropped that one issue,
        # and reported the wing as eleven events instead of twelve - which
        # moved a composition type from at-the-cap to over-it. A parser that
        # drops rows quietly is exactly the failure this script exists to end.
        title = re.sub(r"\s*\([^)]*\)\s*$", "", node["title"])
        m = re.search(r"-\s*([A-Za-z0-9._-]+)\s*$", title)
        if not m:
            continue
        comments = node["comments"]["nodes"]
        body = comments[0]["body"] if comments else ""
        out[m.group(1)] = (node["number"], parse_rotation(body))
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    p.add_argument("--check", action="store_true",
                   help="exit 1 if the §4a cap is broken or a neighbour repeats")
    a = p.parse_args()

    assets = wing_assets(a.slug)
    if not assets:
        print(f"no wing at content/franchises/{a.slug}/", file=sys.stderr)
        return 2

    issues = fetch_issues(a.slug)
    if issues is None:
        return 2

    rows, missing, unparsed = [], [], []
    for kind, eid, title, year in assets:
        found = issues.get(eid)
        if not found:
            missing.append((kind, eid))
            continue
        number, rot = found
        if not rot:
            unparsed.append((eid, number))
            continue
        rows.append((year, kind, eid, number, rot))

    print(f"\n{a.slug} - art rotation, from the issue history\n")
    head = f"{'year':<6}{'type':<16}{'asset':<38}{'#':<6}{'composition':<20}{'dist':<8}carrier"
    print(head)
    print("-" * len(head))
    for year, kind, eid, number, rot in rows:
        print(f"{year:<6}{kind:<16}{eid[:36]:<38}{number:<6}"
              f"{rot['composition'][:18]:<20}{rot['distance'][:6]:<8}{rot['carrier'][:40]}")

    events = [r for r in rows if r[1] != "era-plate"]
    counts = Counter(r[4]["composition"].lower() for r in events)
    cap = max(1, int(len(events) * CAP_FRACTION))

    print(f"\ncomposition types across {len(events)} event sketches "
          f"(era plates excluded, §4b fixes theirs; cap {cap}):\n")
    problems = []
    for name, n in counts.most_common():
        flag = "  OVER THE CAP" if n > cap else ""
        if flag:
            problems.append(f"'{name}' takes {n} of {len(events)} event sketches, over the cap of {cap}")
        print(f"  {name:<24}{n:>3}  {100 * n // max(len(events), 1):>3}%{flag}")

    # Neighbours matter as much as totals: a wing can satisfy every count and
    # still read as pairs, which is what §4a is actually guarding against.
    for prev, cur in zip(events, events[1:]):
        for field in ("composition", "distance", "carrier"):
            if prev[4][field].lower() == cur[4][field].lower():
                problems.append(
                    f"{cur[2]} repeats the {field} of {prev[2]} ('{cur[4][field]}')")

    if unparsed:
        print(f"\n{len(unparsed)} asset(s) whose prompt states no rotation - "
              f"NOT counted above, so the numbers are a floor:")
        for eid, number in unparsed:
            print(f"  {eid} (#{number})")
    if missing:
        print(f"\n{len(missing)} asset(s) with no issue at all:")
        for kind, eid in missing:
            print(f"  {kind:<16}{eid}")

    if problems:
        print(f"\n{len(problems)} rotation problem(s):")
        for x in problems:
            print(f"  - {x}")
    else:
        print("\nrotation holds: no type over the cap, no neighbour repeats.")

    if a.check and (problems or unparsed or missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
