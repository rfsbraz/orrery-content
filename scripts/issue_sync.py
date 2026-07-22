#!/usr/bin/env python3
"""File and close GitHub issues for the visual-asset backlog.

    python scripts/issue_sync.py                    # dry run, every wing
    python scripts/issue_sync.py valter-hugo-mae    # dry run, one wing
    python scripts/issue_sync.py --apply            # write

The queue is derived, never hand-kept. `asset_audit.py` computes what the
content actually needs; this makes GitHub match it. Content is the source of
truth in both directions: a missing asset gets an issue filed, and an asset
that has since been drawn gets its issue closed. An issue that disagrees with
the repo is simply wrong and this run corrects it.

That matters because the tracker WILL drift otherwise. Issue #29 still talks
about "WoT/Cosmere", wings that were renamed on 2026-07-21 - a queue nobody
reconciles slowly starts describing a repo that no longer exists.

Idempotency comes from the `key:` line in each issue body, which is stable for
the life of the asset. Every existing issue is fetched in ONE call and matched
locally rather than searched per item; at 181 assets the per-item search was
181 round trips to discover, almost always, that nothing had changed.

State machine (one label at a time):

    asset:blocked      the wing has no theme.art - nothing can be drawn yet
    asset:needs-prompt filed, but nobody has written the prompt (curator's job)
    asset:needs-art    prompt is ready, paste it into the generator
    asset:ready        image attached, waiting to be wired in
    (closed)           committed, validated and rendering

Rodrigo touches exactly one of these: he flips needs-art -> ready by uploading.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_audit as A  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "rfsbraz/orrery-content"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LABELS = {
    "asset:blocked": ("6a737d", "Wing has no theme.art yet - no asset can be drawn"),
    "asset:needs-prompt": ("fbca04", "Asset queued, prompt not written yet"),
    "asset:needs-art": ("0e8a16", "Prompt ready - generate and attach the image"),
    "asset:ready": ("1d76db", "Image attached, waiting to be wired into content"),
}

# Where each asset type's sketch field actually lives.
TYPE_FILE = {
    "era-plate": "content/franchises/{wing}/eras.yaml",
    "franchise-event": "content/franchises/{wing}/events.yaml",
    "world-event": "content/events/global.yaml",
    # life-event resolves to the author's own file; filled in per job.
}


def wings() -> list[str]:
    d = os.path.join(ROOT, "content", "franchises")
    return sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))


def life_event_home(wing: str) -> dict[str, str]:
    """life-event id -> the author file that owns it.

    A life event lives on the AUTHOR, not the wing, and a wing can have several
    authors. Guessing the wing's first author would silently write a co-author's
    event into the wrong file.
    """
    works = A.load("content", "franchises", wing, "works.yaml") or []
    out = {}
    for aid in dict.fromkeys(a for w in works for a in (w.get("authorIds") or [])):
        a = A.load("content", "authors", f"{aid}.yaml")
        for e in (a or {}).get("lifeEvents") or []:
            out[e.get("id")] = f"content/authors/{aid}.yaml"
    return out


def gh(*args: str, check: bool = True) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


def existing() -> dict[str, dict]:
    """Every asset issue that already exists, keyed. One API call, not N."""
    raw = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "1000",
             "--json", "number,body,state,labels")
    out = {}
    for i in json.loads(raw or "[]"):
        for ln in (i.get("body") or "").splitlines():
            if ln.strip().startswith("key:"):
                out[ln.split("key:", 1)[1].strip()] = i
                break
    return out


def body_for(wing: str, kind: str, aid: str, why: str, path: str, accent: str) -> str:
    dest_dir = "global" if kind == "world-event" else wing
    shared = kind == "world-event"
    lines = [
        f"**{why}**",
        "",
        "No prompt yet. A curator writes it against `docs/VISUAL.md` and the "
        "wing's `theme.art`, then flips this to `asset:needs-art`.",
        "",
    ]
    if shared:
        lines += [
            "> Shared asset. This is drawn ONCE for the catalogue in neutral "
            "house style and tinted per wing by the app, so do not draw it in "
            "any wing's palette.",
            "",
        ]
    lines += [
        "```yaml",
        "asset:",
        f"  key:   {wing}/{kind}/{aid}",
        f"  wing:  {wing}",
        f"  type:  {kind}",
        f"  file:  {path}",
        f"  entry: {aid}",
        "  field: images.sketch",
        f"  dest:  assets/{dest_dir}/{aid}.webp",
        # Quoted: a hex colour starts with '#', which unquoted opens a YAML
        # comment and silently parses the accent as null.
        f'  accent: "{accent}"' if accent else "  accent: null",
        "```",
        "",
        "<sub>Filed by `scripts/issue_sync.py`. The block above is parsed on "
        "intake, so please leave it intact. Attach the image and set "
        "`asset:ready`.</sub>",
    ]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("wing", nargs="?")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--limit", type=int, help="file at most N new issues this run")
    a = p.parse_args()

    targets = [a.wing] if a.wing else wings()
    if a.wing and a.wing not in wings():
        print(f"no wing '{a.wing}'", file=sys.stderr)
        return 2

    have = existing()
    to_file, to_close, blocked = [], [], []

    for wing in targets:
        r = A.audit(wing)
        homes = life_event_home(wing)
        accent = r.get("accent") or ""
        if not r["art"]:
            blocked.append(wing)
            continue
        for kind, aid, why in A.jobs(r):
            key = f"{wing}/{kind}/{aid}"
            if key in have:
                continue
            path = (homes.get(aid) if kind == "life-event"
                    else TYPE_FILE[kind].format(wing=wing))
            if not path:
                print(f"  ?? no home for {key}, skipping")
                continue
            to_file.append((wing, kind, aid, why, path, accent, key))

        # An asset drawn since the issue was filed: close it, do not leave a
        # tracker item describing work that is already in main.
        done = {f"{wing}/{k}/{i}" for k, i, _ in A.jobs(r)}
        for key, issue in have.items():
            if key.startswith(f"{wing}/") and key not in done and issue["state"] == "OPEN":
                to_close.append((key, issue["number"]))

    if a.limit:
        to_file = to_file[: a.limit]

    for w in blocked:
        print(f"  blocked  {w} - needs theme.art before anything can be drawn")
    for _, kind, aid, *_ in to_file:
        print(f"  file     {kind:<16} {aid}")
    for key, num in to_close:
        print(f"  close    #{num} {key} (asset exists now)")
    print(f"\n  {len(to_file)} to file, {len(to_close)} to close, "
          f"{len(have)} already tracked, {len(blocked)} wing(s) blocked")

    if not a.apply:
        print("\n  dry run - nothing written. Re-run with --apply")
        return 0

    for name, (colour, desc) in LABELS.items():
        gh("label", "create", name, "--repo", REPO, "--color", colour,
           "--description", desc, "--force", check=False)

    for wing, kind, aid, why, path, accent, key in to_file:
        title = f"[art] {wing}: {kind} - {aid}"
        gh("issue", "create", "--repo", REPO, "--title", title,
           "--body", body_for(wing, kind, aid, why, path, accent),
           "--label", "asset:needs-prompt")
        print(f"  filed    {key}")
    for key, num in to_close:
        gh("issue", "close", str(num), "--repo", REPO,
           "--comment", "The asset exists in content now; closing automatically.")
        print(f"  closed   #{num}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
