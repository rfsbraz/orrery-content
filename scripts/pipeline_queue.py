#!/usr/bin/env python3
"""The pipeline work queue: what to build next, what needs prompts, what is ready to file.

Three questions the wing-build loop keeps asking GitHub by hand, as one tool:

  next-author   the oldest REQUESTED wing (`[wing] X`, label content:new-franchise)
                that is neither built nor already in progress on a branch/PR.

  needs-prompt  the open `asset:needs-prompt` issues, GROUPED BY WING. This
                grouping is the point, not a convenience: a wing's art is
                composed as one whole-wing pass so the sequence tells a story -
                the pacing contour, the rotation of organisations, the recurring
                motif (docs/VISUAL.md 4a, docs/LAYOUT.md). Writing prompts one
                issue at a time is exactly how a wing ends up seven-elevenths
                identical still-lifes. So this hands you a wing at a time.

  art-ready     the open `asset:ready` issues, grouped by wing, ready for
                `art_intake.py --wing <slug> --apply`.

Reads GitHub through `gh`. Set ORRERY_CONTENT_REPO to point at another repo.
Output is human-readable by default, `--json` when something downstream parses it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("ORRERY_CONTENT_REPO", "rfsbraz/orrery-content")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Author names carry accents (Saramago, García Márquez); the Windows console
# defaults to cp1252 and would crash or mangle them. Same fix fetch.py needed.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# `[art] <wing>: <type> - <entity>`, the title issue_sync.py writes for a
# wing-scoped asset...
ART_TITLE = re.compile(r"^\[art\]\s*(?P<wing>[^:]+):\s*(?P<type>[a-z-]+)\s*-\s*(?P<entity>.+?)\s*$")
# ...and `[art] world-event - <entity>` for a shared global event, which files
# to assets/global/ and belongs to no wing.
ART_GLOBAL = re.compile(r"^\[art\]\s*(?P<type>world-event)\s*-\s*(?P<entity>.+?)\s*$")

# The bucket name for catalogue-wide world-event assets (not a real wing).
GLOBAL_BUCKET = "world-events (global)"
# `[wing] <Author Name>` requests carry a proposed slug in the body.
SLUG_IN_BODY = re.compile(r"[Pp]roposed slug:\s*`?([a-z0-9][a-z0-9-]+)`?")


def gh_json(*args: str):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {(r.stderr or '').strip()[:300]}")
    return json.loads(r.stdout or "[]")


def slugify(name: str) -> str:
    # Python's str.lower() maps U+0130 (LATIN CAPITAL LETTER I WITH DOT ABOVE,
    # the Turkish "dotted I") to "i" + a COMBINING DOT ABOVE, not plain "i" -
    # the well-known dotless-i/dotted-I trap. That combining mark isn't
    # [a-z0-9], so it becomes a spurious hyphen ("Istanbul" -> "istanbul" but
    # "İstanbul" -> "i-stanbul") instead of collapsing cleanly like every
    # other accented character already does here. Normalize it first so both
    # spellings of the same word produce the same slug.
    name = name.replace("İ", "i")
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def wing_built(slug: str) -> bool:
    """A wing exists once its franchise.yaml is on the checked-out tree (main)."""
    return os.path.isfile(os.path.join(ROOT, "content", "franchises", slug, "franchise.yaml"))


def group_by_wing(label: str) -> dict[str, list[dict]]:
    issues = gh_json(
        "issue", "list", "--repo", REPO, "--state", "open",
        "--label", label, "--limit", "500", "--json", "number,title",
    )
    groups: dict[str, list[dict]] = {}
    for it in issues:
        m = ART_TITLE.match(it["title"])
        g = ART_GLOBAL.match(it["title"])
        if m:
            wing, typ, ent = m.group("wing").strip(), m.group("type"), m.group("entity")
        elif g:
            wing, typ, ent = GLOBAL_BUCKET, g.group("type"), g.group("entity")
        else:
            wing, typ, ent = "(unparsed)", "", it["title"]
        groups.setdefault(wing, []).append({"number": it["number"], "type": typ, "entity": ent.strip()})
    for v in groups.values():
        v.sort(key=lambda e: e["number"])
    return groups


# --- next-author ------------------------------------------------------------

def next_author(as_json: bool) -> int:
    issues = gh_json(
        "issue", "list", "--repo", REPO, "--state", "open",
        "--label", "content:new-franchise", "--limit", "300",
        "--json", "number,title,body,createdAt,labels",
    )
    prs = gh_json(
        "pr", "list", "--repo", REPO, "--state", "open", "--limit", "300",
        "--json", "number,headRefName,title",
    )
    branches = [(p.get("headRefName") or "") for p in prs]

    rows = []
    for it in sorted(issues, key=lambda x: x.get("createdAt", "")):
        name = re.sub(r"^\[wing\]\s*", "", it["title"]).strip()
        m = SLUG_IN_BODY.search(it.get("body") or "")
        slug = m.group(1) if m else slugify(name)
        names = {l.get("name") for l in (it.get("labels") or [])}
        if wing_built(slug):
            status = "built"
        elif f"wing/{slug}" in branches or any(slug in b for b in branches):
            status = "in-progress"
        elif "question" in names:
            # An open question about scope/identity/schema must be resolved
            # before the wing is built - otherwise the build bakes in the wrong
            # answer. Not eligible as NEXT until the label comes off.
            status = "question"
        else:
            status = "todo"
        rows.append({
            "number": it["number"], "name": name, "slug": slug,
            "created": (it.get("createdAt") or "")[:10], "status": status,
        })

    nxt = next((r for r in rows if r["status"] == "todo"), None)
    blocked = [r for r in rows if r["status"] == "question"]

    if as_json:
        print(json.dumps({"next": nxt, "blockedOnQuestion": blocked, "queue": rows}, indent=1))
        return 0

    label = {"built": "built", "in-progress": "in progress",
             "question": "question!", "todo": "todo"}
    print(f"Requested wings ({len(rows)}), oldest first:\n")
    for r in rows:
        star = "  <== NEXT" if nxt and r["number"] == nxt["number"] else ""
        print(f"  #{r['number']:<4} {r['created']}  {label[r['status']]:<12} {r['name']}  (`{r['slug']}`){star}")
    print()
    if blocked:
        print("Blocked on an open question (resolve before building):")
        for r in blocked:
            print(f"  #{r['number']} {r['name']} - answer the question on the issue and remove the `question` label")
        print()
    if nxt:
        print(f"Next to build: #{nxt['number']} {nxt['name']}  (slug `{nxt['slug']}`)")
        print(f"  Open a draft PR (Tracks #{nxt['number']}) on branch wing/{nxt['slug']} first, then run the /author pipeline.")
    else:
        print("No unbuilt requests are ready - the queue is clear or everything left is blocked on a question.")
    return 0


# --- needs-prompt / art-ready -----------------------------------------------

def print_groups(groups: dict[str, list[dict]], *, batch_note: str, per_wing_cmd) -> None:
    if not groups:
        print("  (none)")
        return
    # wings with the most work first - the biggest story to compose
    for wing in sorted(groups, key=lambda w: (-len(groups[w]), w)):
        entries = groups[wing]
        print(f"\n{wing}  ({len(entries)} issue(s))")
        cmd = per_wing_cmd(wing)
        if cmd:
            print(f"  {cmd}")
        for e in entries:
            typ = f"{e['type']:<16}" if e["type"] else ""
            print(f"    #{e['number']:<5} {typ} {e['entity']}")
    if batch_note:
        print(f"\n{batch_note}")


def needs_prompt(as_json: bool) -> int:
    groups = group_by_wing("asset:needs-prompt")
    if as_json:
        print(json.dumps(groups, indent=1))
        return 0
    n_wings = len(groups)
    n_issues = sum(len(v) for v in groups.values())
    print(f"Needs prompt: {n_issues} issue(s) across {n_wings} wing(s), grouped for a whole-wing pass.")
    print_groups(
        groups,
        batch_note=(
            "Do ONE wing at a time, all its prompts in a single pass, so the sequence tells a\n"
            "story: grade the whole wing's rotation and pacing first (`art_rotation.py --check <wing>`),\n"
            "then write every prompt against its neighbours (docs/VISUAL.md 4a). Prompts written one\n"
            "issue at a time cannot honour the contour and drift into monotony."
        ),
        per_wing_cmd=lambda w: (
            "# world-events: one neutral sketch each, tinted per wing by the app (VISUAL.md); no per-wing rotation"
            if w == GLOBAL_BUCKET
            else f"# compose: art_rotation.py --check {w}   then write all {len(groups[w])} prompts together"
        ),
    )
    return 0


def art_ready(as_json: bool) -> int:
    groups = group_by_wing("asset:ready")
    if as_json:
        print(json.dumps(groups, indent=1))
        return 0
    n_wings = len(groups)
    n_issues = sum(len(v) for v in groups.values())
    print(f"Art ready: {n_issues} issue(s) across {n_wings} wing(s), ready to file.")
    print_groups(
        groups,
        batch_note="File each wing with: art_intake.py --wing <slug> --apply  (dry-run without --apply first).",
        per_wing_cmd=lambda w: (
            "# file: art_intake.py --apply   (catalogue-wide world-events; no --wing)"
            if w == GLOBAL_BUCKET
            else f"# file: art_intake.py --wing {w} --apply"
        ),
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("next-author", "needs-prompt", "art-ready"):
        s = sub.add_parser(name)
        s.add_argument("--json", action="store_true")
    a = p.parse_args()
    if a.cmd == "next-author":
        return next_author(a.json)
    if a.cmd == "needs-prompt":
        return needs_prompt(a.json)
    if a.cmd == "art-ready":
        return art_ready(a.json)
    return 2


if __name__ == "__main__":
    sys.exit(main())
