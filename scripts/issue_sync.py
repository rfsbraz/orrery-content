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

    asset:blocked       the wing has no theme.art - nothing can be drawn yet
    asset:needs-prompt  filed, but nobody has written the prompt (curator's job)
    asset:needs-art     prompt is ready, paste it into the generator
    asset:ready         image attached, waiting to be wired in
    asset:needs-redraw  the asset exists and is being replaced anyway
    (closed)            committed, validated and rendering

Rodrigo touches exactly one of these: he flips needs-art -> ready by uploading.

REGENERATIONS. Everything above reads the filesystem, and the filesystem cannot
tell a finished asset from one that is about to be replaced - both are a file
at a path. So a wing being redrawn used to have an empty queue while being the
busiest thing in the repo, and worse, the sync would close the issues carrying
the new prompts. `--redraw` is the missing state:

    python scripts/issue_sync.py <wing> --redraw           # dry run
    python scripts/issue_sync.py <wing> --redraw --apply

It reopens every asset issue on the wing and labels it by evidence: an issue
whose comments already carry a prompt goes to `asset:needs-art`, one without
goes to `asset:needs-redraw`. Both are in KEEP_OPEN, so the normal sync stops
treating those files as proof of finished work.
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
    "asset:needs-redraw": ("d93f0b", "Asset exists but is being replaced - do not close on file existence"),
}

# Labels that mean "this issue is live work, whatever the filesystem says".
#
# The queue's whole model is "does a file exist at this path", and that model
# cannot see a REGENERATION: an asset being replaced looks exactly like an
# asset that is finished. It has already gone wrong once - #190 was a redraw
# request, its replacement image was attached, and the sync closed it two hours
# later, before anything wired it in.
#
# So file existence stops being sufficient to close. Any of these means a human
# or a pass has said there is work here, and the filesystem does not get a vote.
KEEP_OPEN = {
    "asset:ready",         # art attached, waiting to be wired in
    "art:human-offer",     # somebody is offering human art for the slot
    "asset:needs-redraw",  # explicitly marked for replacement
    "asset:needs-art",     # a prompt is queued against an asset that already
                           # exists, which IS a redraw in flight; closing it
                           # throws the written prompt away
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
    # A world event is CATALOGUE canon: one drawing, shared by every wing that
    # carries the event and recoloured per wing in CSS. So it is scoped to the
    # catalogue, never to whichever wing's audit happened to surface it - the
    # wing is an accident of discovery, not a property of the asset.
    shared = kind == "world-event"
    owner = "global" if shared else wing
    dest_dir = "global" if shared else wing
    lines = [
        f"**{why}**",
        "",
        "No prompt yet. A curator writes it against `docs/VISUAL.md`"
        + ("" if shared else " and the wing's `theme.art`")
        + ", then flips this to `asset:needs-art`.",
        "",
    ]
    if not shared:
        # The queue files one issue per asset, which is the right unit of
        # RECORD - a permanent address for a moment, so it survives
        # regeneration and a human art offer can attach to it. It is the wrong
        # unit of AUTHORING: cohesion is a property of the sequence, and §4a's
        # cap on any one composition type cannot be checked an asset at a time.
        # That gap is how the Mãe wing shipped seven of eleven event sketches
        # as the same close still-life while every prompt passed review alone.
        lines += [
            "> **Check the wing's rotation before writing this.** "
            f"`python scripts/art_rotation.py {wing}` rebuilds the whole wing's "
            "rotation from the issue history and reports the §4a cap. Vary at "
            "least two of composition type, distance, tonal cast and motif "
            "carrier against the neighbours, and state the four fields on the "
            "`Rotation:` line of your prompt comment or this asset drops out "
            "of the counts.",
            "",
            "> If several assets on this wing are queued at once, that is a "
            "**wing-level pass**, not N independent prompts: plan the rotation "
            "across all of them first (docs/VISUAL.md §7 step 2), then write.",
            "",
        ]
    if shared:
        lines += [
            "> **Shared asset, catalogue scope.** Drawn ONCE in neutral house "
            "style, line and texture only on transparency, and recoloured per "
            "wing in CSS - so it must not be drawn in any wing's palette, and "
            "must contain no filled shapes or a tint turns it into a blob. "
            "It belongs to no author: the wing that surfaced it is an accident "
            "of which audit ran.",
            "",
        ]
    lines += [
        "```yaml",
        "asset:",
        f"  key:   {owner}/{kind}/{aid}",
        f"  wing:  {owner}",
        f"  type:  {kind}",
        f"  file:  {path}",
        f"  entry: {aid}",
        "  field: images.sketch",
        f"  dest:  assets/{dest_dir}/{aid}.webp",
        # Quoted: a hex colour starts with '#', which unquoted opens a YAML
        # comment and silently parses the accent as null.
        ("  accent: null   # tinted per wing; a shared asset has no single accent"
         if shared else (f'  accent: "{accent}"' if accent else "  accent: null")),
        "```",
        "",
        "<sub>Filed by `scripts/issue_sync.py`. The block above is parsed on "
        "intake, so please leave it intact. Attach the image and set "
        "`asset:ready`.</sub>",
    ]
    return "\n".join(lines)


def has_prompt(number: int) -> bool:
    """Does this issue already carry a written prompt?

    Derived from the comments rather than asked for as a flag: a prompt is a
    fenced block containing the labelled sections docs/VISUAL.md §5 mandates.
    The point is that a redraw pass does not have to be told twice what it
    already did - the issue history is the record.
    """
    raw = gh("issue", "view", str(number), "--repo", REPO, "--json", "comments",
             check=False)
    try:
        comments = json.loads(raw or "{}").get("comments") or []
    except json.JSONDecodeError:
        return False
    for c in reversed(comments):
        body = c.get("body") or ""
        if "STYLE:" in body and "CONSTRAINTS:" in body:
            return True
    return False


def redraw(wing: str, apply: bool) -> int:
    """Reopen a wing's asset issues so a regeneration is visible as work.

    The queue reads the filesystem, so after a regeneration decision every one
    of a wing's assets still LOOKS finished - the files are all there, they are
    simply the wrong files. Without this, a wing being redrawn has an empty
    queue and the work exists only in somebody's head.

    The label is derived, not assumed: an issue whose comments already carry a
    prompt goes to `asset:needs-art` (generate it), one without goes to
    `asset:needs-redraw` (write the prompt first). That way running this after
    a prompt pass does the right thing, and running it before also does.
    """
    have = existing()
    keys = sorted(k for k in have if k.startswith(f"{wing}/"))
    if not keys:
        print(f"no asset issues for '{wing}' - nothing to redraw", file=sys.stderr)
        return 2

    plan = []
    for key in keys:
        issue = have[key]
        num = issue["number"]
        label = "asset:needs-art" if has_prompt(num) else "asset:needs-redraw"
        plan.append((key, num, issue["state"], label))

    ready = sum(1 for _, _, _, l in plan if l == "asset:needs-art")
    for key, num, state, label in plan:
        print(f"  redraw   #{num:<5} {key:<58} {state.lower():<7} -> {label}")
    print(f"\n  {len(plan)} asset(s): {ready} with a prompt already written, "
          f"{len(plan) - ready} still needing one")

    if not apply:
        print("\n  dry run - nothing written. Re-run with --apply")
        return 0

    for name, (colour, desc) in LABELS.items():
        gh("label", "create", name, "--repo", REPO, "--color", colour,
           "--description", desc, "--force", check=False)

    for key, num, state, label in plan:
        if state != "OPEN":
            gh("issue", "reopen", str(num), "--repo", REPO, check=False)
        # Remove the other lifecycle labels so the state machine keeps its
        # "one label at a time" property; --add-label alone would leave an
        # asset sitting at needs-prompt AND needs-art.
        stale = [l for l in LABELS if l != label]
        gh("issue", "edit", str(num), "--repo", REPO,
           "--add-label", label,
           *sum((["--remove-label", s] for s in stale), []),
           check=False)
        print(f"  reopened #{num} -> {label}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("wing", nargs="?")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--limit", type=int, help="file at most N new issues this run")
    p.add_argument("--redraw", action="store_true",
                   help="mark a wing for regeneration: reopen its asset issues "
                        "and label them so the sync stops treating an existing "
                        "file as finished work. Requires a wing.")
    a = p.parse_args()

    if a.redraw:
        if not a.wing:
            print("--redraw needs a wing: a catalogue-wide redraw is not a "
                  "thing anyone means to do by accident.", file=sys.stderr)
            return 2
        return redraw(a.wing, a.apply)

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
            # Same scoping as the body: a world event is keyed to the catalogue
            # so two wings carrying it cannot file two issues for one drawing.
            # portugal-bailout-2011 was filed twice (#210 palahniuk, #296
            # joao-tordo) and covid-19-pandemic-2020 twice as well before this.
            owner = "global" if kind == "world-event" else wing
            key = f"{owner}/{kind}/{aid}"
            if key in have:
                continue
            path = (homes.get(aid) if kind == "life-event"
                    else TYPE_FILE[kind].format(wing=wing))
            if not path:
                print(f"  ?? no home for {key}, skipping")
                continue
            to_file.append((owner, kind, aid, why, path, accent, key))

        # An asset drawn since the issue was filed: close it, do not leave a
        # tracker item describing work that is already in main.
        done = {f"{'global' if k == 'world-event' else wing}/{k}/{i}"
                for k, i, _ in A.jobs(r)}
        for key, issue in have.items():
            if not (key.startswith(f"{wing}/") and key not in done):
                continue
            if issue["state"] != "OPEN":
                continue
            # An asset that exists is NOT proof the issue is finished. See
            # KEEP_OPEN: the queue reads the filesystem, and the filesystem
            # cannot tell a finished asset from one being replaced.
            labels = {l.get("name") for l in (issue.get("labels") or [])}
            held = labels & KEEP_OPEN
            if held:
                print(f"  keep     #{issue['number']} {key} ({', '.join(sorted(held))})")
                continue
            to_close.append((key, issue["number"]))

    # World-event issues are keyed to the catalogue, so no wing's pass owns
    # them and the per-wing sweep above can never close one. Reconcile them
    # once, against the union of what every wing still needs: an asset is only
    # finished when NO wing is still waiting on it.
    if not a.wing:
        wanted_global = set()
        for wing in targets:
            r = A.audit(wing)
            if not r["art"]:
                continue
            for kind, aid, _ in A.jobs(r):
                if kind == "world-event":
                    wanted_global.add(f"global/{kind}/{aid}")
        for key, issue in have.items():
            if not key.startswith("global/") or key in wanted_global:
                continue
            if issue["state"] != "OPEN":
                continue
            labels = {l.get("name") for l in (issue.get("labels") or [])}
            held = labels & KEEP_OPEN
            if held:
                print(f"  keep     #{issue['number']} {key} ({', '.join(sorted(held))})")
                continue
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
        title = (f"[art] {kind} - {aid}" if wing == "global"
                 else f"[art] {wing}: {kind} - {aid}")
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
