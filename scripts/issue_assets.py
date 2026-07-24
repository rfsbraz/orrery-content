#!/usr/bin/env python3
"""One reading of an asset issue, shared by everything that reads one.

`issue_sync.py` writes an asset issue, `art_gate.py` decides when it is
finished, and `art_intake.py` takes the images off it. Those three used to
disagree in ways that only showed up as damage:

- the ready-flip fired on the FIRST image, so a `diptych` needing two went to
  `asset:ready` with one, and intake filed half an entry;
- intake took "the last image on the issue" with no notion of rounds, so on a
  REDRAW it could pick up the image from the previous prompt - the one being
  replaced - and file it again as the correction;
- intake always passed `--chroma`, which is contradictory for an opaque
  illustration type and simply wrong for the picture.

So the reading lives in one place and the three callers share it.

## The two rules that matter

**Count against `images_required`.** The issue body carries the count
(docs/LAYOUT.md); an entry is finished when that many images are attached, not
when one is.

**Only images from the current round count.** A round begins at the last
comment carrying a prompt. Anything attached before that belongs to the
previous attempt, and on a redraw the previous attempt is precisely what we
are throwing away. This is why the prompt is the boundary rather than, say, the
label change: the prompt comment is the thing the images are a response to.

An issue whose prompt lives in its BODY (the demo wing is filed that way) has
no prompt-bearing comment, so the round starts at the first comment and the
body itself is admissible - it is, in wall-clock terms, still "after the last
prompt".
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import yaml

REPO = os.environ.get("ORRERY_CONTENT_REPO", "rfsbraz/orrery-content")

# The machine-readable contract `issue_sync.py` writes into every issue body.
BLOCK = re.compile(r"```yaml\s*\n(asset:.*?)```", re.S)

# GitHub has used two hosts for uploads over the years, and an image can arrive
# as markdown or as a bare link, so match the hosts rather than the syntax.
IMG = re.compile(
    r"!\[[^\]]*\]\((https?://[^)\s]+)\)"
    r"|(https://github\.com/user-attachments/assets/[\w-]+)"
    r"|(https://user-images\.githubusercontent\.com/[^\s)]+)"
)

# A prompt is recognised by the labelled sections docs/VISUAL.md §5 mandates,
# not by a marker we would have to remember to write. Same rule as
# `issue_sync.has_prompt`, which is why that function now calls this one.
PROMPT_MARKERS = ("STYLE:", "CONSTRAINTS:")

# Anyone can comment on a public repo. Only people who can be trusted with the
# wing's state may advance it; contributed art is welcome and goes through
# `art:human-offer` instead (VISUAL.md §1b).
TRUSTED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
TRUSTED_LOGINS = {"rfsbraz"}


def gh(*args: str, check: bool = True) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


def is_prompt(text: str) -> bool:
    return all(m in (text or "") for m in PROMPT_MARKERS)


def trusted(author_login: str, association: str) -> bool:
    return (association or "").upper() in TRUSTED_ASSOCIATIONS or author_login in TRUSTED_LOGINS


def spec_of(body: str) -> dict | None:
    """The `asset:` block, or None. Never inferred: an issue without one is
    refused rather than filed somewhere plausible, because a sketch written
    onto the wrong entry is invisible until a human happens to look."""
    m = BLOCK.search(body or "")
    if not m:
        return None
    try:
        return (yaml.safe_load(m.group(1)) or {}).get("asset")
    except yaml.YAMLError:
        return None


def images_in(text: str) -> list[str]:
    out = []
    for groups in IMG.findall(text or ""):
        url = next((g for g in groups if g), None)
        if url and url not in out:
            out.append(url)
    return out


def slot_dests(spec: dict) -> list[str]:
    """Where each of this entry's images is filed.

    Prefers the explicit `slots:` list the issue body carries; falls back to
    deriving `<id>.webp`, `<id>-2.webp`, ... from `dest` for an issue filed
    before that list existed, so an old open issue is still processable.
    """
    slots = spec.get("slots")
    if isinstance(slots, list) and slots:
        out = []
        for s in slots:
            out.append(s.get("dest") if isinstance(s, dict) else str(s))
        return [d for d in out if d]

    dest = spec.get("dest")
    if not dest:
        return []
    n = int(spec.get("images_required") or 1)
    stem, ext = os.path.splitext(dest)
    return [dest] + [f"{stem}-{i}{ext}" for i in range(2, n + 1)]


def fetch(number: int, repo: str = REPO) -> dict:
    """Issue body plus its comments, chronologically.

    Comments come from the REST endpoint rather than `gh issue view --json`
    because only REST exposes `author_association`, and the trust check is not
    optional on a public repo.
    """
    body = gh("api", f"repos/{repo}/issues/{number}", "-q", ".body")
    raw = gh("api", "--paginate", f"repos/{repo}/issues/{number}/comments")
    comments = []
    for chunk in raw.strip().splitlines() or []:
        try:
            parsed = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        comments.extend(parsed if isinstance(parsed, list) else [parsed])
    return {"number": number, "body": body, "comments": comments}


def read(issue: dict) -> dict:
    """The whole verdict for one issue.

    Returns `required`, the `images` admissible this round (in posting order),
    `ready`, and a human-readable `why` - which is the part that matters when
    this says no, because "not ready" with no reason is indistinguishable from
    a broken gate.
    """
    body = issue.get("body") or ""
    comments = issue.get("comments") or []
    spec = spec_of(body)
    required = int((spec or {}).get("images_required") or 1)

    cut = 0
    for i, c in enumerate(comments):
        if is_prompt(c.get("body") or ""):
            cut = i + 1
    prompt_in_body = cut == 0 and is_prompt(body)

    images: list[str] = []
    skipped_untrusted = 0
    # The body is admissible only when no COMMENT carries a prompt - i.e. when
    # the body is itself the prompt, so an image edited into it came after.
    if cut == 0:
        images += images_in(body)
    for c in comments[cut:]:
        login = ((c.get("user") or {}).get("login")) or ""
        if not trusted(login, c.get("author_association") or ""):
            if images_in(c.get("body") or ""):
                skipped_untrusted += 1
            continue
        for url in images_in(c.get("body") or ""):
            if url not in images:
                images.append(url)

    ready = bool(spec) and len(images) >= required
    if not spec:
        why = "no `asset:` block in the body - nothing to file against"
    elif ready:
        why = f"{len(images)}/{required} image(s) attached this round"
    else:
        why = (f"{len(images)}/{required} image(s) attached this round"
               + (f" (round starts after comment #{cut})" if cut else "")
               + (f"; {skipped_untrusted} comment(s) with images ignored as untrusted"
                  if skipped_untrusted else ""))

    return {
        "number": issue.get("number"),
        "spec": spec,
        "required": required,
        "images": images,
        # The LAST `required` images win: a re-upload inside the same round is
        # a correction, and for a multi-slot entry the final N are the set the
        # curator settled on. Slot order is posting order.
        "selected": images[-required:] if len(images) >= required else images,
        "round_starts_at_comment": cut,
        "prompt_in_body": prompt_in_body,
        "has_prompt": cut > 0 or prompt_in_body,
        "ready": ready,
        "why": why,
    }


def read_number(number: int, repo: str = REPO) -> dict:
    return read(fetch(number, repo))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        v = read_number(int(arg))
        print(f"#{v['number']}: {'READY' if v['ready'] else 'waiting'} - {v['why']}")
