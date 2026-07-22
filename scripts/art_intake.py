#!/usr/bin/env python3
"""Collect finished art off GitHub issues and wire it into content.

    python scripts/art_intake.py            # dry run: what is waiting
    python scripts/art_intake.py --apply    # download, convert, patch, close

The other half of `issue_sync.py`. An issue labelled `asset:ready` has an image
attached; this takes it the rest of the way: download, chroma-key, convert to a
capped webp, write the `images.sketch` field on the right entry, and close the
issue. One `gh` call lists everything pending, so the whole queue costs one
round trip regardless of how deep it is.

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

BLOCK = re.compile(r"```yaml\s*\n(asset:.*?)```", re.S)
# GitHub renders an upload as markdown; newer uploads use user-attachments.
IMG = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)\)|(https://github\.com/user-attachments/assets/[\w-]+)")


def gh(*args: str, check: bool = True) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


def pending() -> list[dict]:
    raw = gh("issue", "list", "--repo", REPO, "--label", "asset:ready",
             "--state", "open", "--limit", "200",
             "--json", "number,title,body,comments")
    return json.loads(raw or "[]")


def spec_of(issue: dict) -> dict | None:
    m = BLOCK.search(issue.get("body") or "")
    if not m:
        return None
    try:
        return (yaml.safe_load(m.group(1)) or {}).get("asset")
    except yaml.YAMLError:
        return None


def image_of(issue: dict) -> str | None:
    """The LAST image posted wins - a re-upload is a correction."""
    found = []
    for text in [issue.get("body") or ""] + [c.get("body") or "" for c in issue.get("comments") or []]:
        for a, b in IMG.findall(text):
            found.append(a or b)
    return found[-1] if found else None


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
    a = p.parse_args()

    issues = pending()
    if not issues:
        print("  nothing waiting (no open issue labelled asset:ready)")
        return 0

    done, failed = 0, 0
    for i in issues:
        num, spec, url = i["number"], spec_of(i), image_of(i)
        if not spec:
            print(f"  #{num} REFUSED - no `asset:` block in the body")
            failed += 1
            continue
        if not url:
            print(f"  #{num} REFUSED - labelled ready but no image attached")
            failed += 1
            continue
        key, dest = spec.get("key"), spec.get("dest")
        print(f"  #{num} {key}")
        print(f"        <- {url[:76]}")
        print(f"        -> {dest}")
        if not a.apply:
            continue

        tmp = os.path.join(ROOT, ".cache", f"intake-{num}.png")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
            f.write(r.read())

        out = os.path.join(ROOT, dest)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        r = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "prepare_asset.py"), tmp,
             spec["wing"], spec["entry"], "--chroma"],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(f"        FAILED prepare_asset: {(r.stderr or r.stdout).strip()[:200]}")
            failed += 1
            continue
        if not os.path.exists(out):
            print(f"        FAILED - prepare_asset wrote no file at {dest}")
            failed += 1
            continue
        if not set_field(spec["file"], spec["entry"], spec["field"], dest):
            print(f"        FAILED - no entry '{spec['entry']}' in {spec['file']}")
            failed += 1
            continue
        # `sketch` without `sketchCredit` fails validation, so writing one
        # without the other leaves the wing red and the issue un-closable.
        # The validator wants the credit to say the image was generated.
        set_field(spec["file"], spec["entry"], "images.sketchCredit",
                  "Generated for Orrery (gpt-image-1)")
        if not a.keep_temp:
            os.remove(tmp)
        print("        wired in")
        done += 1

    if a.apply and done:
        v = subprocess.run([sys.executable, os.path.join(SCRIPTS, "validate.py")],
                           capture_output=True, text=True, encoding="utf-8")
        print(f"\n  validate exit={v.returncode}")
        if v.returncode != 0:
            print("  NOT closing any issue - validate is red, fix before committing")
            print((v.stdout or "")[-1500:])
            return 1
        print("  commit the change, then close the issues with:")
        for i in issues:
            print(f"    gh issue close {i['number']} --repo {REPO}")

    print(f"\n  {done} wired, {failed} refused/failed, {len(issues)} seen")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
