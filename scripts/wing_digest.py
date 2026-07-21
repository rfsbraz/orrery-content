#!/usr/bin/env python3
"""A compact, one-call view of a wing, instead of every stage reading all of it.

A finished wing is ~11k words of YAML. Each late stage parses the lot to find
the five percent it owns, and pays for that in context on every subsequent tool
call. This prints the shape of the wing in a screenful: what exists, what is
missing, and which works its own stage still has to touch.

Usage
  python scripts/wing_digest.py <slug>                # overview + full work table
  python scripts/wing_digest.py <slug> --for visual   # only what that stage needs
  python scripts/wing_digest.py <slug> --missing cover

Stage views (--for): completeness, press, eras, orders, spoilers, visual,
editions, translation, audit. Anything else prints the overview.

Read the actual YAML before writing to it. This is for orientation and for
deciding what to open, never a substitute for reading the entries you edit.
"""
from __future__ import annotations

import argparse
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The titles here are Portuguese and the console is not UTF-8 on Windows; without
# this, "Irmãos, Ilhas e Ausências" prints as mojibake and an agent reading the
# digest would copy the damage into content.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(*parts):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def flags(w: dict, editioned: set) -> str:
    imgs = w.get("images") or {}
    return "".join([
        "S" if (w.get("synopsis") or "").strip() else "-",
        "C" if imgs.get("cover") else "-",
        "E" if w["id"] in editioned else "-",
        "N" if (w.get("note") or "").strip() else "-",
    ])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("slug")
    p.add_argument("--for", dest="stage", default="")
    p.add_argument("--missing", choices=["cover", "edition", "synopsis", "era"])
    a = p.parse_args()

    base = ("content", "franchises", a.slug)
    works = load(*base, "works.yaml") or []
    eras = load(*base, "eras.yaml") or []
    orders = load(*base, "orders.yaml") or []
    events = load(*base, "events.yaml") or []
    editions = load(*base, "editions.yaml") or []
    fr = load(*base, "franchise.yaml") or {}
    if not works:
        print(f"no wing at content/franchises/{a.slug}/", file=sys.stderr)
        return 2

    editioned = {e.get("workId") for e in editions}
    spans = []
    for e in eras:
        lo, _, hi = str(e.get("period", "")).partition("-")
        try:
            spans.append((int(lo), 9999 if not hi.isdigit() else int(hi)))
        except ValueError:
            pass
    in_era = lambda y: any(lo <= y <= hi for lo, hi in spans)  # noqa: E731

    author = None
    for aid in (works[0].get("authorIds") or []):
        author = load("content", "authors", f"{aid}.yaml")
        break
    life = len((author or {}).get("lifeEvents") or [])

    print(f"# {a.slug}: {len(works)} works, {len(eras)} eras, {len(orders)} orders, "
          f"{len(events)} franchise events, {life} life events, {len(editions)} editions")
    covers = sum(1 for w in works if (w.get("images") or {}).get("cover"))
    print(f"  covers {covers}/{len(works)} | editions {len(editioned & {w['id'] for w in works})}"
          f"/{len(works)} | startHere {'yes' if fr.get('startHere') else 'no'}"
          f" | globalEvents {'ruled' if fr.get('globalEvents') else 'unruled'}")
    orphans = [w for w in works if not in_era(w.get("published", 0))]
    print(f"  outside every era: {len(orphans)}"
          + (f" ({', '.join(w['id'].split('/')[-1] for w in orphans[:6])})" if orphans else ""))

    for e in eras:
        print(f"  era  {e.get('period','?'):<14} {e.get('provenance','?'):<11} {e.get('title','?')}")
    for o in orders:
        print(f"  order {len(o.get('orderedWorkIds') or []):>3} works  {o.get('type','?'):<10} {o.get('name','?')}")

    if a.missing:
        want = {"cover": lambda w: not (w.get("images") or {}).get("cover"),
                "edition": lambda w: w["id"] not in editioned,
                "synopsis": lambda w: not (w.get("synopsis") or "").strip(),
                "era": lambda w: not in_era(w.get("published", 0))}[a.missing]
        rows = [w for w in works if want(w)]
        print(f"\n# missing {a.missing}: {len(rows)}")
        for w in rows:
            print(f"  {w.get('published','?')}  {w['id']}")
        return 0

    stage = a.stage.lower()
    if stage.startswith("visual"):
        rows = [w for w in works if not (w.get("images") or {}).get("cover")]
        print(f"\n# no cover yet: {len(rows)} of {len(works)}")
    elif stage.startswith("edition"):
        rows = [w for w in works if w["id"] not in editioned]
        print(f"\n# no edition yet: {len(rows)} of {len(works)}")
    elif stage.startswith(("spoil", "transl")):
        rows = [w for w in works if (w.get("synopsis") or "").strip()]
        print(f"\n# works carrying prose: {len(rows)}")
    elif stage.startswith("era"):
        rows = orphans
        print(f"\n# works outside every era: {len(rows)}")
    else:
        rows = works
        print(f"\n# all works (flags: S synopsis, C cover, E edition, N note)")

    for w in sorted(rows, key=lambda w: (w.get("published", 0), w["id"])):
        print(f"  {w.get('published','?')}  {flags(w, editioned)}  "
              f"{w.get('canonTier','?'):<9} {w['id'].split('/')[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
