#!/usr/bin/env python3
"""Decide whether an asset issue has everything it was asked for.

    python scripts/art_gate.py 433              # report
    python scripts/art_gate.py 433 --github     # + machine output for Actions

Called by `.github/workflows/art-ready.yml` on every comment, and runnable by
hand when an issue looks stuck and the label disagrees with the eye.

The whole judgement lives in `issue_assets.read`; this is the thin CLI around
it, so the gate the Action enforces and the reading intake performs cannot
drift apart. Exit code is 0 when ready and 1 when not, and `--github` writes
`ready`, `found` and `required` to `$GITHUB_OUTPUT` so the workflow can branch
without parsing stdout.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issue_assets as IA  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("number", type=int)
    p.add_argument("--repo", default=IA.REPO)
    p.add_argument("--github", action="store_true",
                   help="also write ready/found/required to $GITHUB_OUTPUT")
    a = p.parse_args()

    v = IA.read_number(a.number, a.repo)

    print(f"#{v['number']}: {'READY' if v['ready'] else 'not ready'} - {v['why']}")
    if v["spec"]:
        print(f"  entry    {v['spec'].get('key')}")
        print(f"  required {v['required']}")
        for i, dest in enumerate(IA.slot_dests(v["spec"]), start=1):
            got = v["selected"][i - 1] if i <= len(v["selected"]) else None
            print(f"  slot {i}   {dest}  <- {got or '(waiting)'}")
    if not v["has_prompt"]:
        print("  NOTE: no prompt found on this issue at all. Every image is being "
              "counted, because there is no round to be after.")

    if a.github and os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"ready={'true' if v['ready'] else 'false'}\n")
            f.write(f"found={len(v['images'])}\n")
            f.write(f"required={v['required']}\n")
            # Single-line: a multi-line value would need a heredoc delimiter and
            # this is only ever one sentence.
            f.write(f"why={v['why']}\n")

    return 0 if v["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
