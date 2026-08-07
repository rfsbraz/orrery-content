#!/usr/bin/env python3
"""Report how well each wing's aura tracks its publishing career.

The aura is meant to be sparse, but sparse is not the same as absent. A wing
whose only aura entries cluster on its biographical peaks leaves the working
middle of a career dark: a reader walks a decade of books with no context at
all, which reads as a data gap rather than as an editorial choice.

This measures two things per wing:

  ratio       aura entries per published work (volume)
  dark run    the longest run of consecutive ACTIVE publishing years with no
              aura entry at all (distribution)

Volume is usually fine. Distribution is where wings actually fail, so the
dark run is the number to read. Reports only; a genuinely quiet stretch is a
legitimate answer, but it should be a decision somebody made rather than a
gap nobody noticed.

Usage: python scripts/aura_density.py
"""
import collections
import glob
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A dark stretch this long inside an active career is worth a look. Five years
# is roughly "two or three books with nothing around them" for a working
# novelist, which is the point a reader notices the silence.
DARK_RUN_LIMIT = 5


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except OSError:
        return []


def year_of(entry):
    if not isinstance(entry, dict):
        return None
    m = re.search(r"\d{4}", str(entry.get("date", "")))
    return int(m.group()) if m else None


def covered_years_of(entry):
    """Years this entry counts as non-dark for the gap check.

    An entry with a dateRange (e.g. "1954-1958") describes an ongoing
    situation across that whole span, not a single instant - crediting only
    its bare `date` undercounts real coverage and can report a dark run that
    isn't there. Confirmed live on umberto-eco: a 1954-1958 lifeEvent only
    registered at 1954, leaving 1955-1958 to read as dark. `aura_total`
    stays keyed on the single anchor year (one entry, one count) - this is
    only about which years the dark-run scan treats as covered.
    """
    if not isinstance(entry, dict):
        return set()
    span = str(entry.get("dateRange", ""))
    m = re.match(r"(\d{4})-(\d{4})", span)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo <= hi:
            return set(range(lo, hi + 1))
    y = year_of(entry)
    return {y} if y else set()


def main():
    authors = {}
    for path in glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml")):
        a = load(path)
        if isinstance(a, list):
            a = a[0] if a else {}
        if isinstance(a, dict) and a.get("id"):
            authors[a["id"]] = a

    # global.yaml wraps its list in an `events:` key. Iterating the mapping
    # walked the string "events" instead, so EVERY wing counted zero globals
    # and every dark run in this report was overstated - press-archaeology
    # tuned a wing against it and called a 5-year run borderline when it was 4.
    _g = load(os.path.join(ROOT, "content", "events", "global.yaml"))
    globals_ = _g.get("events", []) if isinstance(_g, dict) else (_g or [])
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
        fev = load(os.path.join(fdir, "events.yaml"))

        wing_authors = [authors[i] for i in (fr.get("authorIds") or []) if i in authors]
        life = [e for a in wing_authors for e in (a.get("lifeEvents") or [])]

        # Global events that actually reach this wing. Per docs/SCHEMA.md: "A
        # global event renders on a wing if and only if that wing names it in
        # `include`. There is no arithmetic default and no implicit
        # membership: silence means absent." - matches the app's own
        # relevantGlobalEvents (lib/content/index.ts), which filters purely
        # on `include` and never consults author lifetimes. An earlier
        # version of this script fell back to lifetime arithmetic when an
        # event wasn't explicitly ruled on, which silently inflated the
        # reported aura count for any wing whose event-resonance stage
        # hadn't yet explicitly excluded every in-lifetime global event
        # (caught live on both fernando-pessoa and james-patterson).
        ge = fr.get("globalEvents") or {}
        included = set(ge.get("include") or [])

        reaching = []
        for e in globals_:
            y = year_of(e)
            eid = e.get("id") if isinstance(e, dict) else None
            if not y or eid not in included:
                continue
            reaching.append(y)

        by_year = collections.Counter()
        covered = set()
        for e in list(fev) + list(life):
            y = year_of(e)
            if y:
                by_year[y] += 1
            covered |= covered_years_of(e)
        for y in reaching:
            by_year[y] += 1
            covered.add(y)

        pub_years = sorted({w["published"] for w in works if isinstance(w, dict) and isinstance(w.get("published"), int)})
        if not pub_years:
            continue
        aura_total = sum(by_year.values())

        # Longest run of consecutive years, inside the publishing span, that
        # contains at least one book and no aura at all. A year is "covered"
        # if any entry's date or dateRange reaches it, not just an entry's
        # single anchor date.
        run = 0
        worst = (0, None, None)
        for y in range(pub_years[0], pub_years[-1] + 1):
            if y not in covered:
                run += 1
                if run > worst[0]:
                    worst = (run, y - run + 1, y)
            else:
                run = 0

        rows.append(
            {
                "slug": slug,
                "works": len(works),
                "aura": aura_total,
                "span": f"{pub_years[0]}-{pub_years[-1]}",
                "dark": worst,
            }
        )

    # A stage builds ONE wing, so it should read one row. Printing all nine
    # buries its own number, invites it to tune against a neighbour's, and
    # costs context for nothing. Pass a slug to scope it.
    scope = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
    if scope:
        known = {r["slug"] for r in rows}
        if scope not in known:
            print(f"no wing '{scope}' - known: {', '.join(sorted(known))}", file=sys.stderr)
            return 2
        rows = [r for r in rows if r["slug"] == scope]

    print("Aura density per wing (entries = franchise events + author life events + globals reaching the wing)\n")
    print(f"{'wing':<20}{'works':>6}{'aura':>6}{'per work':>10}{'span':>12}   longest dark run")
    flagged = []
    for r in rows:
        d, a, b = r["dark"]
        ratio = r["aura"] / r["works"] if r["works"] else 0
        dark = f"{d} yrs ({a}-{b})" if d else "none"
        mark = "  <--" if d >= DARK_RUN_LIMIT else ""
        print(f"{r['slug']:<20}{r['works']:>6}{r['aura']:>6}{ratio:>10.2f}{r['span']:>12}   {dark}{mark}")
        if d >= DARK_RUN_LIMIT:
            flagged.append(r)

    if flagged:
        print(
            f"\n{len(flagged)} wing(s) have {DARK_RUN_LIMIT}+ consecutive publishing years with no aura."
        )
        print("Route to press-archaeology (the author's own record) before world-events:")
        print("a global event is thin gruel for an author-specific silence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
