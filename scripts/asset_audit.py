#!/usr/bin/env python3
"""What visual assets does this wing have, and what is missing?

Answers the cheap half of "what should we generate next" without spending an
agent on it. Counting files is arithmetic; deciding whether a sketch is worth
drawing is not, so this reports and ranks, and stops there.

    python scripts/asset_audit.py <slug>
    python scripts/asset_audit.py <slug> --next        # just the next job
    python scripts/asset_audit.py --all                # every wing, one line each

Ordering follows the workflow in docs/VISUAL.md: the wing's art language is
settled first, then era plates (the largest surfaces), then life and franchise
events, then shared world events. Generating out of order is how a wing ends up
with sketches that do not match each other.

Exit code 0 always: a wing with no art yet is a state, not a failure.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(*parts):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def has_sketch(entity) -> bool:
    return bool((entity.get("images") or {}).get("sketch"))


def era_span(period):
    per = str(period or "")
    if "-" not in per:
        return None
    lo, hi = per.split("-", 1)
    try:
        return int(lo), (9999 if hi.strip().lower() in ("present", "now") else int(hi))
    except ValueError:
        return None


def audit(slug: str) -> dict:
    base = ("content", "franchises", slug)
    works = load(*base, "works.yaml") or []
    eras = load(*base, "eras.yaml") or []
    events = load(*base, "events.yaml") or []
    theme = load(*base, "theme.yaml") or {}

    authors = []
    for aid in dict.fromkeys(a for w in works for a in (w.get("authorIds") or [])):
        a = load("content", "authors", f"{aid}.yaml")
        if a:
            authors.append(a)

    life = [e for a in authors for e in (a.get("lifeEvents") or [])]

    # Which shared events actually reach this wing: inside a lifetime, and not
    # excluded by the wing's own ruling. A global sketch is drawn once for the
    # catalogue, so this is coverage, not a job list for this wing alone.
    fr = load(*base, "franchise.yaml") or {}
    excluded = set((fr.get("globalEvents") or {}).get("exclude") or [])
    g = load("content", "events", "global.yaml") or {}
    globals_ = (g.get("events") if isinstance(g, dict) else g) or []
    # Match the app: an event is the weather a writer wrote in, so the window is
    # the authors' LIFETIMES, not their publishing span. Deriving it from
    # publication years listed the Second World War as reaching an author born
    # in 1971, which would have sent us drawing assets no reader will ever see.
    def year_of(v):
        s = str(v or "")[:4]
        return int(s) if s.isdigit() else None

    births = [y for y in (year_of(a.get("born")) for a in authors) if y]
    deaths = [year_of(a.get("died")) for a in authors]
    lo = min(births) if births else 0
    hi = 9999 if (not deaths or any(d is None for d in deaths)) else max(deaths)
    reaching = []
    for e in globals_:
        if e.get("id") in excluded:
            continue
        y = year_of(e.get("date"))
        if y is not None and lo <= y <= hi:
            reaching.append(e)

    return {
        "slug": slug,
        "art": bool(theme.get("art")),
        "accent": (theme.get("palette") or {}).get("accent"),
        "portraits": (sum(1 for a in authors if (a.get("images") or {}).get("portrait")), len(authors)),
        "covers": (sum(1 for w in works if (w.get("images") or {}).get("cover")), len(works)),
        "eras": (sum(1 for e in eras if has_sketch(e)), len(eras), [e for e in eras if not has_sketch(e)]),
        "life": (sum(1 for e in life if has_sketch(e)), len(life), [e for e in life if not has_sketch(e)]),
        "events": (sum(1 for e in events if has_sketch(e)), len(events), [e for e in events if not has_sketch(e)]),
        "globals": (sum(1 for e in reaching if has_sketch(e)), len(reaching), [e for e in reaching if not has_sketch(e)]),
    }


def jobs(r: dict) -> list[tuple[str, str, str]]:
    """(asset type, id, why) in generation order. Empty when the wing is done."""
    out = []
    if not r["art"]:
        out.append(("theme.art", r["slug"],
                    "no art language on theme.yaml - settle this FIRST or every "
                    "sketch will belong to a different wing"))
        return out  # nothing else can be generated consistently until this exists
    for e in r["eras"][2]:
        out.append(("era-plate", e.get("id", "?"), f"{e.get('title','?')} ({e.get('period','?')})"))
    for e in r["life"][2]:
        out.append(("life-event", e.get("id", "?"), e.get("title", "?")))
    for e in r["events"][2]:
        out.append(("franchise-event", e.get("id", "?"), e.get("title", "?")))
    for e in r["globals"][2]:
        out.append(("world-event", e.get("id", "?"),
                    f"{e.get('title','?')} - shared, house style, tinted per wing"))
    return out


def line(r: dict) -> str:
    def frac(k):
        return f"{r[k][0]}/{r[k][1]}"
    return (f"{r['slug']:<20} art:{'yes' if r['art'] else 'NO ':<3} "
            f"portrait {frac('portraits')}  covers {frac('covers')}  "
            f"eras {frac('eras')}  life {frac('life')}  "
            f"franchise {frac('events')}  world {frac('globals')}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("slug", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--next", action="store_true", help="print only the next job")
    a = p.parse_args()

    if a.all or not a.slug:
        for d in sorted(glob.glob(os.path.join(ROOT, "content", "franchises", "*"))):
            if os.path.isdir(d):
                print(line(audit(os.path.basename(d))))
        return 0

    if not os.path.isdir(os.path.join(ROOT, "content", "franchises", a.slug)):
        print(f"no wing at content/franchises/{a.slug}", file=sys.stderr)
        return 2

    r = audit(a.slug)
    todo = jobs(r)
    if a.next:
        print(f"{todo[0][0]}  {todo[0][1]}  # {todo[0][2]}" if todo else "nothing to generate")
        return 0

    print(line(r))
    print(f"  accent {r['accent'] or '(none)'} - world-event sketches are tinted with this\n")
    if not todo:
        print("  every slot filled. Re-check against docs/VISUAL.md before adding more.")
        return 0
    print(f"  {len(todo)} asset(s) to generate, in order:")
    for kind, ident, why in todo:
        print(f"    {kind:<16} {ident:<34} {why}")
    print("\n  next: python scripts/asset_audit.py %s --next" % a.slug)
    print("  then: /asset-prompt %s <asset type> <id>" % a.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
