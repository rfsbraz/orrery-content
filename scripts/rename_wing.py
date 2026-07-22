#!/usr/bin/env python3
"""Rename a wing's slug across content, safely.

    python scripts/rename_wing.py cosmere brandon-sanderson --dry-run
    python scripts/rename_wing.py cosmere brandon-sanderson --apply

Work ids are `<wing-slug>/<work-slug>`, so a wing rename rewrites every id it
owns. That is mechanical, but it sits next to something that must NOT be
rewritten: the wing's own name is usually a word that appears throughout the
prose. "The Cosmere section", "the non-Cosmere series", "Discworld novels" -
these are the subject matter, not identifiers, and a blind search-replace turns
them into "the Brandon Sanderson section".

So this only ever rewrites shapes that are unambiguously identifiers:

  * `<slug>/...`            work ids, order ids, inline [[work:...]] targets
  * `id: <slug>`            the franchise's own id, at the start of a line
  * `[[franchise:<slug>]]`  inline franchise links
  * `franchiseId: <slug>`   achievement criteria
  * `orderId: <slug>/...`   covered by the first rule

Bare prose occurrences are left alone, and the run reports how many it saw so
the number can be eyeballed rather than assumed.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def dirs_for(slug: str) -> list[str]:
    return [
        os.path.join(ROOT, "content", "franchises", slug),
        os.path.join(ROOT, "content", "i18n", "pt-PT", "franchises", slug),
        os.path.join(ROOT, "assets", slug),
    ]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    old, new = a.old, a.new

    if not os.path.isdir(os.path.join(ROOT, "content", "franchises", old)):
        print(f"no wing '{old}'", file=sys.stderr)
        return 2
    if os.path.isdir(os.path.join(ROOT, "content", "franchises", new)):
        print(f"'{new}' already exists", file=sys.stderr)
        return 2

    rules = [
        (re.compile(rf"\b{re.escape(old)}/"), f"{new}/"),
        (re.compile(rf"^(\s*)id:\s*{re.escape(old)}\s*$", re.M), rf"\1id: {new}"),
        # Must accept the display-pipe form too: [[franchise:slug|Text]].
        # Matching only the bracket-closing form left three links dangling,
        # which the validator caught and this comment exists to prevent.
        (re.compile(rf"\[\[franchise:{re.escape(old)}(?=[|\]])"), f"[[franchise:{new}"),
        (re.compile(rf"franchiseId:\s*{re.escape(old)}\b"), f"franchiseId: {new}"),
    ]
    # Anything that is the slug but NOT one of the shapes above: prose.
    prose = re.compile(rf"\b{re.escape(old)}\b(?!/)", re.I)

    # URLs are masked out before any rule runs, and restored after.
    #
    # `<slug>/` is our id shape, but it is ALSO a path segment shape, and a
    # source URL belongs to somebody else's namespace. The first run of this
    # script rewrote four live links into 404s, among them
    # `.../the-idea-of-the-cosmere/` -> `.../the-idea-of-the-brandon-sanderson/`
    # and colinsmythe.co.uk/terry-pratchett/discworld/ -> /terry-pratchett/
    # twice over. A dead source is worse than an unrenamed one: the citation
    # still looks supported.
    URL = re.compile(r"https?://\S+")

    changed, edits, prose_left, urls_seen = [], 0, 0, 0
    targets = sorted(
        glob.glob(os.path.join(ROOT, "content", "**", "*.yaml"), recursive=True)
        + glob.glob(os.path.join(ROOT, "docs", "**", "*.md"), recursive=True)
    )
    for path in targets:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        if old not in src.lower():
            continue
        urls = URL.findall(src)
        urls_seen += len(urls)
        out = URL.sub("\x00URL\x00", src)
        for rx, sub in rules:
            out = rx.sub(sub, out)
        it = iter(urls)
        out = re.sub("\x00URL\x00", lambda _: next(it).replace("\\", "\\\\"), out)
        n = sum(1 for _ in re.finditer(re.escape(new), out)) - sum(
            1 for _ in re.finditer(re.escape(new), src)
        )
        prose_left += len(prose.findall(out))
        if out != src:
            changed.append((os.path.relpath(path, ROOT), n))
            edits += n
            if a.apply:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(out)

    for d in dirs_for(old):
        if os.path.isdir(d):
            dest = d.replace(os.sep + old, os.sep + new)
            print(f"  move {os.path.relpath(d, ROOT)} -> {os.path.relpath(dest, ROOT)}")
            if a.apply:
                subprocess.run(["git", "mv", d, dest], cwd=ROOT, check=True)

    print(f"\n  {edits} identifier(s) rewritten across {len(changed)} file(s)")
    print(f"  {prose_left} prose occurrence(s) of '{old}' left untouched (expected: "
          f"the fictional universe is named in synopses and notes)")
    print(f"  {urls_seen} URL(s) held out of the rewrite entirely")
    if not a.apply:
        print("\n  dry run - nothing written. Re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
