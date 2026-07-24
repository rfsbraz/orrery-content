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

# --- docs/LAYOUT.md's rotation budget: the organisation axis ----------------
# The 16 organisation slugs. Kept here as a query-time reference; LAYOUT.md is
# the source of truth.
ORGANISATIONS = {
    "beside", "full-bleed-vista", "immersion", "floating-object",
    "artifact-spread", "diptych", "strip", "marginalia", "medallion",
    "split-counterpoint", "layered-stack", "mosaic", "interlude",
    "passage", "chapter-gate", "epigraph",
}
# `beside` defaults absent-organisation events (LAYOUT.md: "an event with none
# renders as beside"), so it is the implicit value everywhere the field is
# unset - not "no data".
DEFAULT_ORGANISATION = "beside"

# AMBIGUOUS IN THE SOURCE: LAYOUT.md states two different ceilings for the
# same slug in the same sentence - "no single organisation may exceed ~40% of
# a wing's events, and `beside` specifically should sit around half, not
# three-quarters." Taken literally, "around half" already breaks a 40% cap.
# Resolved here by reading the general 40% cap as applying to every
# organisation OTHER than `beside` (which the same sentence explicitly allows
# to "be the plurality"), and giving `beside` its own higher ceiling at the
# "not three-quarters" line, with ~50% as the target rather than a hard
# boundary. A human should re-read this against LAYOUT.md if the two numbers
# were meant to compose differently.
ORG_CAP_FRACTION = 0.40
BESIDE_CAP_FRACTION = 0.75
BESIDE_TARGET_FRACTION = 0.50
# "Capped at 1-2 per wing" - an absolute count, not a fraction.
IMMERSION_MAX = 2
# "one per era" - checked against the wing's actual era count, not a fraction.
# "Used sparingly" for `interlude` names no number at all; this is a judgement
# call (see the report), set generously so it flags only a wing that has
# clearly stopped treating it as a rare device.
INTERLUDE_CAP_FRACTION = 0.15
# "Capped at 2-3 per wing" - an absolute count, like IMMERSION_MAX. `epigraph`
# is the only organisation that costs nothing to produce (no prompt, no
# generation, no issue), which is exactly why its cap needs enforcing rather
# than trusting: an unlimited free organisation gets reached for as filler.
EPIGRAPH_MAX = 3


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
    """(kind, id, title, year, organisation) for every asset slot, in timeline order.

    Era plates are listed but excluded from the composition count: §4b fixes
    their composition and they render on their own half-page, so counting them
    would dilute the cap the events actually need. They are also excluded from
    the organisation count for the same reason - an era plate IS the
    `chapter-gate` slot by construction (LAYOUT.md: "this is the era-plate
    slot, not an event"), one per era already, so folding it into the events'
    organisation budget would double-count a cap that is structural, not
    authored.

    `organisation` is read straight from the event's own content field where
    present - the primary, reliable source, unlike the composition axis below
    which only exists in the issue comment history. An event that has not been
    graded onto the grammar yet has no field at all, which is not "unknown":
    LAYOUT.md defaults an ungraded event to `beside`.
    """
    base = ("content", "franchises", slug)
    eras = load(*base, "eras.yaml") or []
    events = load(*base, "events.yaml") or []
    works = load(*base, "works.yaml") or []

    out = []
    for e in eras:
        y = year_of((e.get("period") or "").split("-")[0])
        out.append(("era-plate", e.get("id"), e.get("title"), y or 0,
                    e.get("organisation") or "chapter-gate"))

    seen = set()
    for w in works:
        for aid in w.get("authorIds") or []:
            if aid in seen:
                continue
            seen.add(aid)
            a = load("content", "authors", f"{aid}.yaml") or {}
            for e in a.get("lifeEvents") or []:
                out.append(("life-event", e.get("id"), e.get("title"),
                            year_of(e.get("date")) or 0,
                            e.get("organisation")))

    for e in events:
        out.append(("franchise-event", e.get("id"), e.get("title"),
                    year_of(e.get("date")) or 0, e.get("organisation")))

    return sorted(out, key=lambda r: (r[3], r[0]))


# Two accepted forms. The canonical one is what .claude/commands/asset-prompt.md
# now mandates; the prose one is what the first regeneration pass wrote, and
# re-editing sixteen comments to satisfy a parser would be the tail wagging the
# dog.
#
# The trailing `organisation=` group is optional and NOT yet written by
# asset-prompt.md (that command is out of scope for this pass) - it exists so
# a wing's rotation comments can carry the organisation axis too, once the
# prompt writer starts stating it, without a second regex format. Until then
# `organisation` is `None` here and `wing_assets`' content-field read (or the
# `beside` default) is what actually resolves it.
CANONICAL = re.compile(
    r"composition\s*=\s*(?P<composition>[^|\n]+)\|"
    r"\s*distance\s*=\s*(?P<distance>[^|\n]+)\|"
    r"\s*cast\s*=\s*(?P<cast>[^|\n]+)\|"
    r"\s*carrier\s*=\s*(?P<carrier>[^|\n]+)"
    r"(?:\|\s*organisation\s*=\s*(?P<organisation>[^|\n]+))?",
    re.I,
)
PROSE = re.compile(
    r"\*\*composition type (?P<composition>.+?)\*\*.*?"
    r"\*\*distance (?P<distance>.+?)\*\*.*?"
    r"\*\*tonal cast (?P<cast>.+?)\*\*.*?"
    r"\*\*orrery motif carried by (?P<carrier>.+?)\*\*",
    re.I | re.S,
)
# A third form, because two writers given the SAME brief produced two different
# layouts on the same afternoon: "Rotation for this asset: **peopled scene /
# middle / neutral mid grey / a ceiling diffuser**". Supporting it is cheaper
# than re-editing eighteen comments, and it is the clearest possible argument
# for the canonical `Rotation:` line that asset-prompt.md now mandates.
SLASHED = re.compile(
    r"rotation[^:\n]*:\s*\*\*(?P<composition>[^/*]+)/(?P<distance>[^/*]+)/"
    r"(?P<cast>[^/*]+)/(?P<carrier>[^*]+)\*\*",
    re.I,
)


def parse_rotation(body: str):
    for pattern in (CANONICAL, PROSE, SLASHED):
        m = pattern.search(body or "")
        if m:
            # `organisation` is an optional group (CANONICAL only) and comes
            # back as None when the line doesn't carry it - leave it None
            # rather than crashing on `.split()`, since callers treat a
            # missing organisation as "fall back to the content field".
            return {k: (" ".join(v.split()) if v is not None else None)
                    for k, v in m.groupdict().items()}
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
    for kind, eid, title, year, _content_org in assets:
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

    # A verdict over nothing is not a verdict. The first version of this script
    # printed "rotation holds" for a wing where all eighteen prompts had failed
    # to parse: it had checked zero assets and cleared them in the same breath,
    # which is the exact shape of reassuring output this tool exists to remove.
    # Coverage gates the verdict now.
    covered, total = len(rows), len(assets)
    if unparsed or missing:
        problems.append(
            f"only {covered} of {total} assets could be read "
            f"({len(unparsed)} unparsed, {len(missing)} with no issue) - "
            f"the counts above are a floor, not a verdict")

    if problems:
        print(f"\n{len(problems)} rotation problem(s):")
        for x in problems:
            print(f"  - {x}")
    elif covered == total and events:
        print(f"\nrotation holds across all {total} assets: "
              f"no type over the cap, no neighbour repeats.")
    else:
        print("\nnothing could be checked.")

    # --- the organisation axis (docs/LAYOUT.md's rotation budget) -----------
    # Unlike composition, this does NOT need an issue to resolve: the
    # `organisation` field lives on the event's own content, so coverage here
    # is never gated on the issue tracker the way composition is. An issue's
    # `Rotation:` line is only consulted as a fallback for an event that has
    # neither, and an event with neither at all defaults to `beside`
    # (LAYOUT.md: "an event with none renders as beside") - never "unknown".
    era_count = sum(1 for kind, *_ in assets if kind == "era-plate")
    org_rows = []
    for kind, eid, title, year, content_org in assets:
        if kind == "era-plate":
            continue
        issue_org = None
        found = issues.get(eid)
        if found:
            _, rot = found
            if rot:
                issue_org = rot.get("organisation")
        org_rows.append((year, kind, eid, content_org or issue_org or DEFAULT_ORGANISATION))

    total_org = len(org_rows)
    org_counts = Counter(org for *_, org in org_rows)
    org_problems = []

    print(f"\norganisation types across {total_org} event sketches "
          f"(era plates excluded - each already IS the `chapter-gate` slot, "
          f"one per era by construction, not a choice made per event):\n")
    for name, n in org_counts.most_common():
        cap = max(1, int(total_org * (BESIDE_CAP_FRACTION if name == "beside" else ORG_CAP_FRACTION)))
        over = n > cap
        flag = "  OVER THE CAP" if over else ""
        if over:
            org_problems.append(
                f"organisation '{name}' takes {n} of {total_org} events, over the cap of {cap}")
        print(f"  {name:<24}{n:>3}  {100 * n // max(total_org, 1):>3}%{flag}")

    immersion_n = org_counts.get("immersion", 0)
    if immersion_n > IMMERSION_MAX:
        org_problems.append(
            f"organisation 'immersion' is used {immersion_n} times, over LAYOUT.md's "
            f"cap of {IMMERSION_MAX} per wing")

    chapter_gate_n = org_counts.get("chapter-gate", 0)
    if chapter_gate_n > era_count:
        org_problems.append(
            f"organisation 'chapter-gate' is used {chapter_gate_n} times among events, "
            f"more than the wing's {era_count} era(s) - LAYOUT.md caps it at one per era")

    epigraph_n = org_counts.get("epigraph", 0)
    if epigraph_n > EPIGRAPH_MAX:
        org_problems.append(
            f"organisation 'epigraph' is used {epigraph_n} times, over LAYOUT.md's "
            f"cap of {EPIGRAPH_MAX} per wing - it is free to produce, so the cap is "
            f"what keeps it from becoming filler"
        )

    interlude_n = org_counts.get("interlude", 0)
    interlude_cap = max(1, int(total_org * INTERLUDE_CAP_FRACTION))
    if interlude_n > interlude_cap:
        org_problems.append(
            f"organisation 'interlude' is used {interlude_n} times, over a "
            f"judgement-call cap of {interlude_cap} ({INTERLUDE_CAP_FRACTION:.0%} of "
            f"events) - LAYOUT.md only says 'used sparingly', no number given "
            f"(see the comment above INTERLUDE_CAP_FRACTION)")

    # Same discipline as the composition axis: a wing can clear every count and
    # still read as pairs down the page, which is exactly what LAYOUT.md's "no
    # two consecutive events share an organisation" line is guarding against.
    for prev, cur in zip(org_rows, org_rows[1:]):
        if prev[3] == cur[3]:
            org_problems.append(
                f"{cur[2]} repeats organisation '{cur[3]}' from its neighbour {prev[2]}")

    if org_problems:
        print(f"\n{len(org_problems)} organisation-rotation problem(s):")
        for x in org_problems:
            print(f"  - {x}")
    elif org_rows:
        print(f"\norganisation rotation holds across all {total_org} events: "
              f"no organisation over its cap, no neighbour repeats.")
    else:
        print("\nno events to check on the organisation axis.")

    if a.check and (problems or org_problems or unparsed or missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
