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
- the ready-check trusted the issue body's `images_required`, a snapshot from
  whenever `issue_sync.py` filed it. `issue_sync.py` opens and closes issues
  but never rewrites one already filed, so an entry regraded to a diptych
  afterwards left its issue claiming `images_required: 1` forever. Two of
  those went to `ready` on one image, and intake keyed the LAST attachment
  (the diptych's second/mirror panel) into the first/only slot - the true
  first panel silently dropped, no error anywhere (2026-07-27, #584).

So the reading lives in one place and the three callers share it.

## The two rules that matter

**Count against `images_required` - read from content, not the issue body.**
An entry is finished when that many images are attached, not when one is.
`content_images_required` looks the entry up in its actual YAML file, because
the issue body is a snapshot that can go stale (see above); the issue's own
count is only the fallback when content can't be read (a demo issue with no
real entry, a renamed id).

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
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def _find_entry(doc, entry_id: str):
    """The dict with `id: entry_id`, wherever it sits in a content YAML.

    Structure-agnostic on purpose: a top-level list (events.yaml, eras.yaml)
    and a dict with a nested list (authors.yaml's `lifeEvents`) both show up
    across the catalogue, and a third shape would not be a surprise. Same
    "search, don't assume the shape" spirit as `art_intake.set_field`'s line
    surgery.
    """
    if isinstance(doc, dict):
        if doc.get("id") == entry_id:
            return doc
        for v in doc.values():
            found = _find_entry(v, entry_id)
            if found is not None:
                return found
    elif isinstance(doc, list):
        for item in doc:
            found = _find_entry(item, entry_id)
            if found is not None:
                return found
    return None


def content_images_required(spec: dict) -> int | None:
    """The entry's actual `images_required`, read from content - or None if
    it cannot be determined (a demo issue with no real entry, a missing file,
    a renamed id).

    The issue body's `images_required` is a snapshot taken when `issue_sync.py`
    filed the issue; content is the source of truth going forward (its own
    module docstring says as much) but nothing ever WROTE that back into an
    already-filed issue's body. An entry regraded to a diptych after its issue
    existed left the body claiming `images_required: 1` forever, and the
    stale count is what a caller trusting the body alone would use: the
    ready-check flips on one image instead of two, and intake keys the LAST
    attached image (a diptych's second/mirror panel) into the first/only slot,
    dropping the true first panel with no error anywhere. This is the fix -
    content, not the issue, decides the count.
    """
    file = spec.get("file")
    entry_id = spec.get("entry")
    if not file or not entry_id:
        return None
    path = os.path.join(ROOT, file)
    try:
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return None
    entry = _find_entry(doc, entry_id)
    if entry is None:
        return None
    try:
        return int(entry.get("images_required") or 1)
    except (TypeError, ValueError):
        return None


def slot_dests(spec: dict) -> list[str]:
    """Where each of this entry's images is filed.

    `images_required` (by now corrected against content - see `read()`)
    decides how many. Uses the explicit `slots:` list the issue body carries
    for the dest paths when it actually covers that many; otherwise derives
    `<id>.webp`, `<id>-2.webp`, ... from `dest`, which also covers an issue
    filed before `slots:` existed, or one where content grew past what the
    body's list still lists.
    """
    n = int(spec.get("images_required") or 1)
    slots = spec.get("slots")
    if isinstance(slots, list) and len(slots) >= n:
        out = [s.get("dest") if isinstance(s, dict) else str(s) for s in slots[:n]]
        out = [d for d in out if d]
        if len(out) == n:
            return out

    dest = spec.get("dest")
    if not dest:
        return []
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
    declared = int((spec or {}).get("images_required") or 1)
    # Content decides the count, not the issue body's snapshot of it - see
    # `content_images_required`. `spec` is copied before the correction is
    # written back onto it, so `slot_dests(v["spec"])` downstream also sees
    # the right count instead of re-deriving the stale one.
    actual = content_images_required(spec) if spec else None
    required = actual if actual is not None else declared
    stale = actual is not None and actual != declared
    if spec is not None and stale:
        spec = dict(spec)
        spec["images_required"] = required

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
    stale_note = (f" (issue declared images_required: {declared}, content now "
                  f"wants {required} - stale, re-run issue_sync.py on this wing)"
                  if stale else "")
    if not spec:
        why = "no `asset:` block in the body - nothing to file against"
    elif ready:
        why = f"{len(images)}/{required} image(s) attached this round{stale_note}"
    else:
        why = (f"{len(images)}/{required} image(s) attached this round{stale_note}"
               + (f" (round starts after comment #{cut})" if cut else "")
               + (f"; {skipped_untrusted} comment(s) with images ignored as untrusted"
                  if skipped_untrusted else ""))

    return {
        "number": issue.get("number"),
        "spec": spec,
        "required": required,
        "stale": stale,
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
