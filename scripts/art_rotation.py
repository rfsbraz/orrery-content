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

# --- The pacing contour: order, not frequency -------------------------------
# Every cap above answers "how often". None of them answers "in what order", so
# a wing can clear every single one and still be six loud cells running
# followed by a flat stretch. That is the failure exhibition designers name
# outright - alternate higher-intensity spaces with lower-intensity ones, or
# the reader never gets to process anything - and it is invisible to a counter.
#
# JUDGEMENT CALL: LAYOUT.md does not grade the organisations by intensity, so
# this table is derived from their own render specs. An organisation that takes
# the screen and stops the page is loud; one whose device is emptiness is
# quiet; the workhorses are mid. Re-read it against LAYOUT.md if a spec changes.
LOUD, MID, QUIET = "loud", "mid", "quiet"
INTENSITY = {
    "immersion": LOUD,          # "the total stop"
    "full-bleed-vista": LOUD,   # "the breath" - a wide scene with no text zone
    "chapter-gate": LOUD,       # "a strong visual reset"
    "mosaic": LOUD,             # "public noise"
    "diptych": MID,
    "split-counterpoint": MID,
    "layered-stack": MID,
    "artifact-spread": MID,
    "strip": MID,
    "beside": MID,
    "medallion": MID,
    "floating-object": MID,
    "passage": QUIET,           # compressed time, deliberately shallow
    "interlude": QUIET,         # "the emptiness is the device"
    "marginalia": QUIET,        # "the footnote"
    "epigraph": QUIET,          # no artwork at all
}

# Roughly what fraction of a phone viewport each organisation occupies.
# MEASURED, not guessed: rendered on the app's own layout-grammar demo page at
# 390px wide (margins included) and divided by an 844px viewport. Approximate
# by nature - a cell's height also depends on how long its prose is - which is
# fine, because the only thing this table has to do is turn "two loud cells
# eight events apart" (invisible to the reader, fine) into "two loud cells the
# reader sees at once" (the actual failure). Mobile on purpose: it is the
# tighter viewport and the one the monotony complaint came from.
VIEWPORT_SHARE = {
    "split-counterpoint": 1.24,
    "diptych": 1.07,
    "artifact-spread": 0.73,
    "chapter-gate": 0.57,
    "layered-stack": 0.55,
    "full-bleed-vista": 0.51,
    "floating-object": 0.51,
    "mosaic": 0.49,
    "epigraph": 0.45,
    "strip": 0.45,
    "medallion": 0.45,
    "beside": 0.42,
    "immersion": 0.40,
    "passage": 0.36,
    "interlude": 0.34,
    "marginalia": 0.17,
}
DEFAULT_SHARE = 0.42  # an unknown organisation is assumed to read like `beside`

# A rupture needs rest on at least one side, so two loud cells may not touch.
MAX_CONSECUTIVE_LOUD = 1
# A plateau is the other failure: same intensity for long enough that the page
# stops having a shape. Five in a row is a run of besides with nothing between.
MAX_FLAT_RUN = 4
# One phone viewport. The print equivalent is the spread - the unit the reader
# takes in at once, which is what a designer actually composes against, and
# which a whole-wing count cannot see.
SCREENFUL = 1.0
MAX_LOUD_PER_SCREENFUL = 1


def pacing_problems(org_rows) -> tuple[list[str], str]:
    """The contour checks, and a one-line sparkline of the wing's shape.

    `org_rows` is (year, kind, id, organisation) in timeline order - the same
    rows the frequency caps are counted from, read as a SEQUENCE instead.

    Three failures, none of which a frequency cap can see:

    1. Two loud cells touching. A rupture earns its weight from the quiet
       around it; back to back they cancel.
    2. A flat run - the same intensity for MAX_FLAT_RUN+1 events. This is the
       original complaint in its purest form: nothing is over any cap, and the
       page still has no shape.
    3. Two loud cells inside one screenful. The whole-wing counts treat two
       vistas as far apart if there are events between them; the reader's eye
       does not, if those events are short enough to fit on the same screen.
    """
    problems: list[str] = []
    if not org_rows:
        return problems, ""

    orgs = [r[3] for r in org_rows]
    ids = [r[2] for r in org_rows]
    levels = [INTENSITY.get(o, MID) for o in orgs]

    # Both run checks read the same grouping: consecutive events at the same
    # intensity, as (level, first index, last index).
    runs: list[tuple[str, int, int]] = []
    start = 0
    for i in range(1, len(levels) + 1):
        if i == len(levels) or levels[i] != levels[start]:
            runs.append((levels[start], start, i - 1))
            start = i

    for level, lo, hi in runs:
        n = hi - lo + 1
        # 1. loud cells touching
        if level == LOUD and n > MAX_CONSECUTIVE_LOUD:
            problems.append(
                f"{n} loud cells run back to back ({', '.join(ids[lo:hi + 1])}) - a "
                f"rupture earns its weight from the quiet around it, so at most "
                f"{MAX_CONSECUTIVE_LOUD} may touch")
        # 2. flat runs
        if n > MAX_FLAT_RUN:
            problems.append(
                f"{n} consecutive '{level}' cells ({ids[lo]} .. {ids[hi]}) - a plateau "
                f"of {MAX_FLAT_RUN + 1}+ reads as a stack however varied the "
                f"organisations inside it are")

    # 3. loud cells sharing a screenful
    shares = [VIEWPORT_SHARE.get(o, DEFAULT_SHARE) for o in orgs]
    flagged: set[tuple[int, int]] = set()
    for i in range(len(orgs)):
        acc = 0.0
        window = []
        for j in range(i, len(orgs)):
            acc += shares[j]
            window.append(j)
            if acc >= SCREENFUL:
                break
        louds = [k for k in window if levels[k] == LOUD]
        if len(louds) > MAX_LOUD_PER_SCREENFUL:
            pair = (louds[0], louds[1])
            if pair in flagged:
                continue
            flagged.add(pair)
            problems.append(
                f"{ids[louds[0]]} and {ids[louds[1]]} are both loud and land within one "
                f"screenful of each other ({sum(shares[k] for k in window):.2f} viewports "
                f"across {len(window)} cells) - far apart in the counts, together on the page")

    bar = {LOUD: "#", MID: "=", QUIET: "."}
    return problems, "".join(bar[l] for l in levels)


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

    # --- the pacing contour (order, not frequency) --------------------------
    pace_problems, contour = pacing_problems(org_rows)
    if contour:
        print(f"\npacing contour, first event to last "
              f"(# loud, = mid, . quiet - see INTENSITY):\n\n  {contour}\n")
    if pace_problems:
        print(f"{len(pace_problems)} pacing problem(s):")
        for x in pace_problems:
            print(f"  - {x}")
    elif org_rows:
        print("pacing holds: no two loud cells touching or sharing a screenful, "
              "no plateau.")

    if a.check and (problems or org_problems or pace_problems or unparsed or missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
