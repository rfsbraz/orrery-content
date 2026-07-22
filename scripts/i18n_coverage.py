#!/usr/bin/env python3
"""Report translation coverage per locale.

Finds reader-facing prose in the base content and checks each locale has an
overlay carrying it. Catches the failure mode that no other check does: content
that belongs to no franchise (shared global events, co-author bios, character
rosters) and so gets missed when translation work is split by franchise.

Usage: python scripts/i18n_coverage.py [--strict]
Exit non-zero with --strict when a locale has any missing file.
"""
import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# file -> the prose fields a reader actually sees
PROSE = {
    "franchise.yaml": ["description"],
    "works.yaml": ["synopsis"],
    # `themes` is a list of short noun phrases rendered under the era title on
    # the era plate. It is prose a reader reads, and leaving it out of this map
    # let four wings ship Portuguese era plates with English themes underneath
    # while the script reported full coverage.
    "eras.yaml": ["title", "description", "themes"],
    "events.yaml": ["title", "description"],
    "orders.yaml": ["name", "rationale"],
    "characters.yaml": ["description"],
}


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def slots(path, fields):
    """Every reader-facing prose slot in a file, as (entry-id, field) keys.

    Granularity is the whole point, and it has been wrong twice.

    First this counted only top-level fields, and reported a locale complete
    while five franchises still had English startHere paths. Nested lists (an
    author's lifeEvents, a franchise's startHere paths) are real prose and are
    now walked.

    Then it counted an ENTRY as covered if ANY of its fields was translated. An
    order carrying a translated `rationale` but an English `name` scored as
    fully done, which is how six order names across three franchises stayed
    English under a "52/52 complete" report.

    So the unit is one field of one entry. A slot is covered only when that
    exact field is translated, and keying by id means an overlay cannot score by
    translating a different entry than the base has.
    """
    data = load(path)
    if data is None:
        return set()
    items = data if isinstance(data, list) else [data]
    if isinstance(data, dict) and "events" in data:
        items = data["events"]
    out = set()
    for i in items:
        if not isinstance(i, dict):
            continue
        # A franchise.yaml is a single mapping with no list index; fall back to
        # the file itself so its one entry still keys stably.
        key = i.get("id") or i.get("slug") or "_"
        for f in fields:
            if i.get(f):
                out.add((key, f))
        for nested in (i.get("lifeEvents") or []):
            if not isinstance(nested, dict):
                continue
            nkey = nested.get("id") or "_"
            for f in ("title", "description"):
                if nested.get(f):
                    out.add((f"{key}/lifeEvents/{nkey}", f))
        sh = i.get("startHere")
        if isinstance(sh, dict):
            for path_ in (sh.get("paths") or []):
                if not isinstance(path_, dict):
                    continue
                pkey = path_.get("id") or "_"
                for f in ("title", "description"):
                    if path_.get(f):
                        out.add((f"{key}/startHere/{pkey}", f))
    return out


def count(path, fields):
    """Number of prose slots in a file (kept for callers wanting a total)."""
    return len(slots(path, fields))


def main():
    strict = "--strict" in sys.argv
    # --json makes this gateable in CI. The human report says "74/82 files
    # covered", which tells you there is work but not WHICH files regressed;
    # comparing that number across branches also breaks the moment a base file
    # is added. Per-file status compares cleanly.
    as_json = "--json" in sys.argv
    status = {}
    locales = [
        os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "content", "i18n", "*"))
        if os.path.isdir(p)
    ]
    if not locales:
        print("No translation locales yet.")
        return

    # every base file carrying prose, as (relative path, fields)
    targets = []
    for fdir in sorted(glob.glob(os.path.join(ROOT, "content", "franchises", "*"))):
        if not os.path.isdir(fdir):
            continue
        slug = os.path.basename(fdir)
        for fname, fields in PROSE.items():
            p = os.path.join(fdir, fname)
            if os.path.exists(p) and count(p, fields):
                targets.append((os.path.join("franchises", slug, fname), fields))
    for p in sorted(glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml"))):
        targets.append((os.path.join("authors", os.path.basename(p)), ["bio"]))
    gpath = os.path.join(ROOT, "content", "events", "global.yaml")
    if os.path.exists(gpath):
        targets.append((os.path.join("events", "global.yaml"), ["title", "description"]))

    failed = False
    for locale in sorted(locales):
        missing, partial, done = [], [], 0
        for rel, fields in targets:
            base = slots(os.path.join(ROOT, "content", rel), fields)
            if not base:
                continue
            ov = os.path.join(ROOT, "content", "i18n", locale, rel)
            if not os.path.exists(ov):
                missing.append(f"{rel} ({len(base)})")
                continue
            have = slots(ov, fields)
            gaps = base - have
            if gaps:
                # Name the fields, not just a ratio. "6/7" sends someone
                # hunting; "name" tells them what to write.
                which = sorted({f for _, f in gaps})
                partial.append(
                    f"{rel} {len(base) - len(gaps)}/{len(base)} (missing: {', '.join(which)})"
                )
                status[f"{locale}/{rel}"] = "partial"
            else:
                done += 1
                status[f"{locale}/{rel}"] = "complete"
        total = len([t for t in targets if slots(os.path.join(ROOT, "content", t[0]), t[1])])
        print(f"\n=== {locale}: {done}/{total} files fully covered ===")
        if missing:
            failed = True
            print("  MISSING:")
            for m in missing:
                print(f"    - {m}")
        if partial:
            print("  PARTIAL:")
            for p in partial:
                print(f"    - {p}")
        if not missing and not partial:
            print("  complete")

    if as_json:
        import json
        print(json.dumps(status, indent=0, sort_keys=True))

    if strict and failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
