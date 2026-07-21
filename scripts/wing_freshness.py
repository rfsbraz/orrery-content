#!/usr/bin/env python3
"""Report which wings are likely to have gone stale, and why.

A wing is curated at a moment in time and the world keeps moving: the author
publishes, wins something, gives an interview that finally explains a book, or
dies. Nothing in this repo notices. This script is the cheap mechanical half of
noticing - it produces leads, never conclusions, and every one of them still has
to be researched by the stage that owns it.

Signals, per wing:

  living         the author has no `died` date, so the career may continue
  latest work    the most recent `published` year on the shelf
  quiet for      years between that and now (a living author with a long quiet
                 stretch is the strongest single lead)
  last touched   when content/franchises/<slug>/ last changed in git
  aura ends      the most recent dated aura entry, which goes stale faster than
                 the bibliography does

A flag here means "go and look", not "something is wrong". A living author can
genuinely publish nothing for five years, and a wing can be perfectly current
and untouched for a year. What this catches is the wing nobody has looked at
since something happened.

Usage: python scripts/wing_freshness.py [--json]
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A living author with no recorded publication for this long is worth a look.
QUIET_YEARS = 2
# Aura that stops this far short of the shelf's end usually means the press
# pass predates the newest books.
AURA_LAG_YEARS = 3


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except OSError:
        return []


def year_in(value):
    m = re.search(r"\d{4}", str(value or ""))
    return int(m.group()) if m else None


def last_touched(slug):
    """Date the wing's content last changed, from git rather than a field.

    Git already records this accurately and for free; a `lastReviewed:` key in
    the content would be process metadata in a data file, which the comment
    policy exists to keep out.
    """
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", f"content/franchises/{slug}/"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return (out.stdout or "").strip() or None
    except Exception:
        return None


def main():
    as_json = "--json" in sys.argv
    today = datetime.date.today()
    authors = {}
    for path in glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml")):
        a = load(path)
        if isinstance(a, list):
            a = a[0] if a else {}
        if isinstance(a, dict) and a.get("id"):
            authors[a["id"]] = a

    rows = []
    for fdir in sorted(glob.glob(os.path.join(ROOT, "content", "franchises", "*"))):
        if not os.path.isdir(fdir):
            continue
        slug = os.path.basename(fdir)
        works = load(os.path.join(fdir, "works.yaml"))
        if not works:
            continue
        fr = load(os.path.join(fdir, "franchise.yaml"))
        if isinstance(fr, list):
            fr = fr[0] if fr else {}

        wing_authors = [authors[i] for i in (fr.get("authorIds") or []) if i in authors]
        living = [a for a in wing_authors if not a.get("died")]

        years = [w["published"] for w in works if isinstance(w, dict) and isinstance(w.get("published"), int)]
        latest = max(years) if years else None

        aura_years = []
        for e in load(os.path.join(fdir, "events.yaml")):
            y = year_in(e.get("date") if isinstance(e, dict) else None)
            if y:
                aura_years.append(y)
        for a in wing_authors:
            for e in a.get("lifeEvents") or []:
                y = year_in(e.get("date"))
                if y:
                    aura_years.append(y)
        aura_end = max(aura_years) if aura_years else None

        quiet = today.year - latest if latest else None
        leads = []
        if living and quiet is not None and quiet >= QUIET_YEARS:
            leads.append(f"living author, nothing published recorded since {latest}")
        if not living and wing_authors and not any(a.get("died") for a in wing_authors):
            leads.append("author death not recorded but no living author either")
        if aura_end and latest and (latest - aura_end) >= AURA_LAG_YEARS:
            leads.append(f"aura stops at {aura_end}, shelf runs to {latest}")
        if not aura_end:
            leads.append("no dated aura at all")

        rows.append(
            {
                "wing": slug,
                "living": bool(living),
                "works": len(works),
                "latest": latest,
                "quiet": quiet,
                "auraEnd": aura_end,
                "touched": last_touched(slug),
                "leads": leads,
            }
        )

    if as_json:
        print(json.dumps(rows, indent=1))
        return 0

    print(f"Wing freshness as of {today.isoformat()} (leads to research, not defects)\n")
    print(f"{'wing':<20}{'author':>8}{'works':>6}{'latest':>8}{'aura':>7}{'touched':>13}")
    for r in rows:
        who = "living" if r["living"] else "dead"
        print(
            f"{r['wing']:<20}{who:>8}{r['works']:>6}{str(r['latest']):>8}"
            f"{str(r['auraEnd']):>7}{str(r['touched']):>13}"
        )
    print()
    flagged = [r for r in rows if r["leads"]]
    for r in flagged:
        print(f"{r['wing']}:")
        for lead in r["leads"]:
            print(f"  - {lead}")
    if flagged:
        print(
            f"\n{len(flagged)} wing(s) carry leads. Route each to the stage that owns it:"
        )
        print("  new or missing works      -> completeness-auditor")
        print("  new life events, press    -> press-archaeology")
        print("  a death                   -> press-archaeology, then eras (obituaries periodise)")
        print("  catalogue span extended   -> world-events, then event-resonance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
