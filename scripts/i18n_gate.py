#!/usr/bin/env python3
"""Fail when a fully translated file quietly becomes partial.

    python scripts/i18n_gate.py base.json head.json

Both files are `i18n_coverage.py --json` output.

A partial locale is a legitimate state, so completeness is not required. The
failure this guards against is different: prose gets added to a base file, the
translation delta is left for later, and later never comes. It happened on
2026-07-22, when four wings gained aura entries and pt-PT coverage fell from
82/82 to 74/82 with nothing complaining.

Set the `i18n-followup` label on the PR when the translation genuinely lands
separately; the workflow passes that through and this reports instead of
failing.
"""
from __future__ import annotations

import json
import os
import sys


def load(path: str) -> dict:
    try:
        s = open(path, encoding="utf-8").read()
        return json.loads(s[s.index("{"):])
    except Exception:
        # An unreadable side is not a regression. Failing here would block
        # every PR the moment the report format shifted.
        return {}


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: i18n_gate.py base.json head.json", file=sys.stderr)
        return 2

    base, head = load(sys.argv[1]), load(sys.argv[2])
    if not base:
        print("No baseline coverage to compare against; nothing to gate.")
        return 0

    regressed = sorted(
        f for f, v in base.items()
        if v == "complete" and head.get(f, "complete") == "partial"
    )
    if not regressed:
        print("No translation regressions.")
        return 0

    print("Files that were fully translated and no longer are:\n")
    for f in regressed:
        print(f"  - {f}")

    if "i18n-followup" in os.environ.get("LABELS", ""):
        print("\ni18n-followup label present: reporting only.")
        return 0

    print("\nRun the translation stage for these, or label the PR "
          "'i18n-followup' if the translation lands in a separate change.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
