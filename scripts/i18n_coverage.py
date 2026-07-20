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
    "eras.yaml": ["title", "description"],
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


def count(path, fields):
    """Count prose-bearing entries, including NESTED prose.

    Nested lists (an author's lifeEvents, a franchise's startHere paths) are
    real reader-facing prose. Counting only top-level fields reported a locale
    as complete while five franchises still had English startHere paths, which
    is exactly the blindness this script exists to prevent.
    """
    data = load(path)
    if data is None:
        return 0
    items = data if isinstance(data, list) else [data]
    if isinstance(data, dict) and "events" in data:
        items = data["events"]
    n = 0
    for i in items:
        if not isinstance(i, dict):
            continue
        if any(i.get(f) for f in fields):
            n += 1
        for nested in (i.get("lifeEvents") or []):
            if isinstance(nested, dict) and (nested.get("title") or nested.get("description")):
                n += 1
        sh = i.get("startHere")
        if isinstance(sh, dict):
            for path_ in (sh.get("paths") or []):
                if isinstance(path_, dict) and (path_.get("title") or path_.get("description")):
                    n += 1
    return n


def main():
    strict = "--strict" in sys.argv
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
            base_n = count(os.path.join(ROOT, "content", rel), fields)
            if not base_n:
                continue
            ov = os.path.join(ROOT, "content", "i18n", locale, rel)
            if not os.path.exists(ov):
                missing.append(f"{rel} ({base_n})")
                continue
            ov_n = count(ov, fields)
            if ov_n < base_n:
                partial.append(f"{rel} {ov_n}/{base_n}")
            else:
                done += 1
        total = len([t for t in targets if count(os.path.join(ROOT, "content", t[0]), t[1])])
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

    if strict and failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
