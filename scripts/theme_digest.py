#!/usr/bin/env python3
"""One line per wing of the axes visual languages actually collide on.

`visual-language`'s skill requires reading "the `art:` block of every wing that
already has one" before writing a new one, so a wing's language can be pushed
away from its neighbours deliberately. That requirement is right; reading
twenty full theme.yaml files to satisfy it is not. Measured at twenty wings the
full read is ~126KB (~31,500 tokens), and it grows with the CATALOGUE rather
than with the wing being built - so every future wing pays more, however small
it is.

Collisions live on a handful of axes. This prints those, and only those, in
about 2.5KB. Scan it, then open in full only the one or two wings it shows you
are adjacent - which is where "be explicit about how yours differs" genuinely
needs the prose.

    python scripts/theme_digest.py              # every wing
    python scripts/theme_digest.py --exclude X  # every wing but X (yours)
    python scripts/theme_digest.py --json
"""
import argparse
import glob
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def one_line(s, limit):
    return " ".join((s or "").split())[:limit]


def rows(exclude=None):
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "franchises", "*", "theme.yaml"))):
        slug = os.path.basename(os.path.dirname(path))
        if exclude and slug == exclude:
            continue
        t = yaml.safe_load(open(path, encoding="utf-8")) or {}
        art = t.get("art") or {}
        pal = t.get("palette") or {}
        out.append({
            "wing": slug,
            "preset": t.get("preset"),
            "accent": pal.get("accent"),
            "bg": pal.get("bg"),
            "displayFace": t.get("displayFace"),
            "signature": t.get("signature"),
            "line": one_line(art.get("lineCharacter"), 90),
            "atmosphere": one_line(art.get("atmosphere"), 90),
            "emblem": one_line((art.get("emblem") or {}).get("object"), 70),
        })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exclude", help="skip this slug (the wing you are writing)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    data = rows(a.exclude)
    if a.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"{len(data)} wings with a theme. The axes languages collide on:\n")
    for r in data:
        print(f"{r['wing']}")
        print(f"  preset {r['preset']} | accent {r['accent']} | bg {r['bg']} "
              f"| face {r['displayFace']} | signature {r['signature']}")
        print(f"  line   {r['line']}")
        print(f"  air    {r['atmosphere']}")
        print(f"  emblem {r['emblem']}")

    # Collisions are worth naming outright rather than leaving to the reader.
    print("\nalready claimed:")
    for axis in ("accent", "displayFace", "signature", "preset"):
        seen = {}
        for r in data:
            seen.setdefault(r[axis], []).append(r["wing"])
        dupes = {k: v for k, v in seen.items() if k and len(v) > 1}
        if dupes:
            for k, v in sorted(dupes.items()):
                print(f"  {axis} {k}: {', '.join(v)}")
    print("\nRead a wing's theme.yaml in full only if this shows you are adjacent to it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
