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

        # Global events that actually reach this wing: the engine's lifetime
        # filter, then the wing's own include/exclude ruling.
        ge = fr.get("globalEvents") or {}
        excluded = set(ge.get("exclude") or [])
        included = set(ge.get("include") or [])
        births = [
            int(re.search(r"\d{4}", str(a.get("born"))).group())
            for a in wing_authors
            if re.search(r"\d{4}", str(a.get("born", "")))
        ]
        deaths = [
            int(re.search(r"\d{4}", str(a.get("died"))).group())
            for a in wing_authors
            if re.search(r"\d{4}", str(a.get("died", "")))
        ]
        lo_life = min(births) if births else None
        hi_life = max(deaths) if deaths and len(deaths) == len(wing_authors) else 9999

        reaching = []
        for e in globals_:
            y = year_of(e)
            eid = e.get("id") if isinstance(e, dict) else None
            if not y or eid in excluded:
                continue
            if eid in included or (lo_life is not None and lo_life <= y <= hi_life):
                reaching.append(y)

        by_year = collections.Counter()
        for e in list(fev) + list(life):
            y = year_of(e)
            if y:
                by_year[y] += 1
        for y in reaching:
            by_year[y] += 1

        pub_years = sorted({w["published"] for w in works if isinstance(w, dict) and isinstance(w.get("published"), int)})
        if not pub_years:
            continue
        aura_total = sum(by_year.values())

        # Longest run of consecutive years, inside the publishing span, that
        # contains at least one book and no aura at all.
        run = 0
        worst = (0, None, None)
        for y in range(pub_years[0], pub_years[-1] + 1):
            if by_year.get(y, 0) == 0:
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
