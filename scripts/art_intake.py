#!/usr/bin/env python3
"""Collect finished art off GitHub issues and wire it into content.

    python scripts/art_intake.py              # dry run: what is waiting
    python scripts/art_intake.py --apply      # download, convert, patch
    python scripts/art_intake.py --wing demo  # only one wing's ready assets

The other half of `issue_sync.py`. An issue labelled `asset:ready` has an image
attached; this takes it the rest of the way: download, chroma-key, convert to a
capped webp, write the `images.sketch` field on the right entry, and close the
issue. One `gh` call lists everything pending, so the whole queue costs one
round trip regardless of how deep it is.

It writes files and stops there. `main` is protected and every content change
goes through a pull request that Rodrigo merges himself, so this never commits
and never pushes: branch, PR, wait.

The `asset:` block in the issue body says exactly which file and entry the
image belongs to. It is parsed, never inferred - an image with no block is
refused rather than filed somewhere plausible, because a sketch written onto
the wrong entry is invisible until a human happens to look at that page.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
REPO = "rfsbraz/orrery-content"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml  # noqa: E402

sys.path.insert(0, SCRIPTS)
# One reading of an asset issue, shared with `art_gate.py` and the `Art ready`
# workflow: which images belong to the CURRENT round, how many the entry needs,
# and where each one is filed. Having intake re-implement any of that is how it
# used to file the previous round's image as the correction to itself.
import issue_assets as IA  # noqa: E402


def gh(*args: str, check: bool = True) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


def pending() -> list[int]:
    """Issue numbers labelled `asset:ready`. Numbers only: each one is then
    re-read through `issue_assets.fetch`, which uses the REST comment endpoint
    because only that exposes `author_association` - and the trust check is not
    optional on a public repo."""
    raw = gh("issue", "list", "--repo", REPO, "--label", "asset:ready",
             "--state", "open", "--limit", "200", "--json", "number")
    return [i["number"] for i in json.loads(raw or "[]")]


def set_field(path: str, entry_id: str, field: str, value: str) -> bool:
    """Write `field` on the entry with id `entry_id`, in place.

    Line surgery, not a YAML round-trip. Both alternatives were tried and both
    lose: `yaml.safe_dump` discards every comment, and ruamel's round-trip mode
    reproduced ZERO of this repo's 191 content files byte-identically and threw
    on 133 of them. The comments here are curated sources, so a writer that
    reflows them is not usable at any price.

    The entry's line range is computed explicitly rather than by searching
    forward from the id, because a naive forward search finds the NEXT entry's
    `images:` block and merges two records. That produced invalid YAML in three
    of four shapes when this was first written.
    """
    full = os.path.join(ROOT, path)
    with open(full, encoding="utf-8") as f:
        lines = f.read().split("\n")

    rx = re.compile(rf"^(\s*(?:-\s+)?)id:\s*{re.escape(entry_id)}\s*$")
    start = next((n for n, ln in enumerate(lines) if rx.match(ln)), None)
    if start is None:
        return False

    # Sibling properties sit at the column where `id:` itself begins.
    prop = lines[start].index("id:")
    pad = " " * prop

    # The entry ends at the first non-blank line indented LESS than its own
    # properties; that is the next list item or the end of the document.
    end = len(lines)
    for n in range(start + 1, len(lines)):
        if not lines[n].strip():
            continue
        if len(lines[n]) - len(lines[n].lstrip()) < prop:
            end = n
            break

    leaf = field.split(".")[-1]
    img = next((n for n in range(start + 1, end)
                if lines[n].rstrip() == f"{pad}images:"), None)
    if img is None:
        lines[start + 1:start + 1] = [f"{pad}images:", f"{pad}  {leaf}: {value}"]
    else:
        lrx = re.compile(rf"^{pad}  {re.escape(leaf)}:")
        at = next((n for n in range(img + 1, end) if lrx.match(lines[n])), None)
        if at is None:
            lines[img + 1:img + 1] = [f"{pad}  {leaf}: {value}"]
        else:
            lines[at] = f"{pad}  {leaf}: {value}"

    with open(full, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--keep-temp", action="store_true")
    p.add_argument("--wing", metavar="SLUG",
                   help="only process assets for this wing (e.g. `demo`), so a "
                        "run for one wing does not sweep up every other wing's "
                        "ready assets into the same content branch")
    a = p.parse_args()

    issues = pending()
    if not issues:
        print("  nothing waiting (no open issue labelled asset:ready)")
        return 0

    done, failed, skipped = 0, 0, 0
    processed: list[tuple[int, bool]] = []
    for num in issues:
        v = IA.read_number(num, REPO)
        spec = v["spec"]
        if a.wing and (spec or {}).get("wing") != a.wing:
            skipped += 1
            continue
        if not spec:
            print(f"  #{num} REFUSED - no `asset:` block in the body")
            failed += 1
            continue
        # The label is a claim; this is the check. `asset:ready` is set by the
        # workflow, by a human, or by a stale run, and only one of those three
        # counted the images. Filing three of a four-image entry leaves a slot
        # silently empty, which nothing downstream can detect.
        if not v["ready"]:
            print(f"  #{num} REFUSED - {v['why']}")
            failed += 1
            continue

        dests = IA.slot_dests(spec)
        # `slots` carries a per-slot `file:` line with the flags the entry's
        # illustration type implies (VISUAL.md §3b). Falling back to bare
        # `--chroma` only for an issue filed before that existed - and never
        # inventing flags, because --chroma on an opaque type is a hard error
        # and on an artifact type would dissolve the drawn edge away.
        slot_flags = []
        for i, s in enumerate(spec.get("slots") or [], start=1):
            raw = (s.get("file") if isinstance(s, dict) else None) or ""
            slot_flags.append(raw.split() or ["--chroma", "--slot", str(i)])
        while len(slot_flags) < len(dests):
            slot_flags.append(["--chroma", "--slot", str(len(slot_flags) + 1)])

        print(f"  #{num} {spec.get('key')}  ({v['required']} image(s))")
        for i, (url, dest) in enumerate(zip(v["selected"], dests), start=1):
            print(f"        slot {i} <- {url[:66]}")
            print(f"               -> {dest}  [{' '.join(slot_flags[i - 1])}]")
        if not a.apply:
            continue

        wrote = []
        broke = False
        for i, (url, dest) in enumerate(zip(v["selected"], dests), start=1):
            tmp = os.path.join(ROOT, ".cache", f"intake-{num}-{i}.png")
            os.makedirs(os.path.dirname(tmp), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
                f.write(r.read())

            out = os.path.join(ROOT, dest)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            r = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "prepare_asset.py"), tmp,
                 spec["wing"], spec["entry"], *slot_flags[i - 1]],
                capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                print(f"        FAILED slot {i} prepare_asset: {(r.stderr or r.stdout).strip()[:200]}")
                broke = True
            elif not os.path.exists(out):
                print(f"        FAILED slot {i} - prepare_asset wrote no file at {dest}")
                broke = True
            if not a.keep_temp and os.path.exists(tmp):
                os.remove(tmp)
            if broke:
                break
            wrote.append(dest)

        if broke:
            failed += 1
            continue
        # A DEMO asset has no content entry to write to. The demo wing exists
        # only in the app (`lib/demo/timeline.ts`) to exercise every layout
        # organisation at once, so there is no YAML row for a sketch path to
        # land on - and inventing one would put a fake author in the canon.
        # Everything before this point still ran, which is the whole point:
        # the demo issues are how the prompt -> image -> chroma -> dissolve ->
        # webp -> correct-filename path gets proven end to end without
        # touching real content.
        if spec.get("demo"):
            print(f"        demo asset - files written, no content entry to update")
            done += 1
            processed.append((num, True))
            continue
        # Slot 1 is the entry's `images.sketch`; the rest are found by the app
        # from that path (`<id>-2.webp`, ... - see components/river/shared.tsx
        # `imageSlots`), so only the first is written to content.
        if not set_field(spec["file"], spec["entry"], spec["field"], wrote[0]):
            print(f"        FAILED - no entry '{spec['entry']}' in {spec['file']}")
            failed += 1
            continue
        # `sketch` without `sketchCredit` fails validation, so writing one
        # without the other leaves the wing red and the issue un-closable.
        # The validator wants the credit to say the image was generated.
        set_field(spec["file"], spec["entry"], "images.sketchCredit",
                  "Generated for Orrery (gpt-image-1)")
        print(f"        wired in ({len(wrote)} slot(s))")
        done += 1
        processed.append((num, False))

    wrote_content = any(not demo for _, demo in processed)
    if a.apply and wrote_content:
        v = subprocess.run([sys.executable, os.path.join(SCRIPTS, "validate.py")],
                           capture_output=True, text=True, encoding="utf-8")
        print(f"\n  validate exit={v.returncode}")
        if v.returncode != 0:
            print("  NOT closing any issue - validate is red, fix before committing")
            print((v.stdout or "")[-1500:])
            return 1

    # The demo issues carry no content, so there is nothing to branch or
    # validate for them - but every processed issue still needs closing once
    # its result is committed (the demo assets to the app, real assets via a
    # content PR Rodrigo merges). List exactly the ones this run handled, never
    # every issue it looked at.
    if a.apply and processed:
        if wrote_content:
            print("  main is protected: branch, open a PR, and let Rodrigo merge it.")
            print("  Close these issues only AFTER that PR is merged:")
        else:
            print("  Close these issues once the assets are committed:")
        for num, _ in processed:
            print(f"    gh issue close {num} --repo {REPO}")

    tail = f", {skipped} skipped (other wing)" if skipped else ""
    print(f"\n  {done} wired, {failed} refused/failed, {len(issues)} seen{tail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
