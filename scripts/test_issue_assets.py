#!/usr/bin/env python3
"""Tests for the asset-issue reading (`issue_assets.read`).

    python scripts/test_issue_assets.py

Written against the three failures that motivated the module, each of which
shipped before anyone noticed:

1. a two-image entry flipping to ready on one image;
2. a redraw picking up the image from the PREVIOUS prompt;
3. a stranger's attachment advancing the pipeline on a public repo.

Every case is an assertion that the gate says NO when it should. A gate only
tested on its happy path is a gate nobody has seen refuse anything, which is
the same as no gate at all.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issue_assets as IA  # noqa: E402

PROMPT = "STYLE:\n  ...\nCONSTRAINTS:\n  ..."
IMG1 = "![a](https://github.com/user-attachments/assets/aaaa-1111)"
IMG2 = "![b](https://github.com/user-attachments/assets/bbbb-2222)"
IMG3 = "![c](https://github.com/user-attachments/assets/cccc-3333)"


def body(n: int = 1, block: bool = True, prompt: bool = False) -> str:
    out = "Filed by issue_sync.\n\n"
    if prompt:
        out += PROMPT + "\n\n"
    if block:
        out += (
            "```yaml\n"
            "asset:\n"
            "  key:   demo/life-event/demo-x\n"
            "  wing:  demo\n"
            "  type:  life-event\n"
            "  file:  content/authors/demo.yaml\n"
            "  entry: demo-x\n"
            "  field: images.sketch\n"
            "  dest:  assets/demo/demo-x.webp\n"
            f"  images_required: {n}\n"
            "```\n"
        )
    return out


def c(text: str, login: str = "rfsbraz", assoc: str = "OWNER") -> dict:
    return {"body": text, "user": {"login": login}, "author_association": assoc}


CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


@case("one image satisfies a one-image entry")
def _():
    v = IA.read({"number": 1, "body": body(1), "comments": [c(PROMPT), c(IMG1)]})
    assert v["ready"], v
    assert v["selected"] == [IMG1.split("(")[1][:-1]], v


@case("one image does NOT satisfy a two-image entry")
def _():
    v = IA.read({"number": 2, "body": body(2), "comments": [c(PROMPT), c(IMG1)]})
    assert not v["ready"], v
    assert v["required"] == 2 and len(v["images"]) == 1, v


@case("two images satisfy a two-image entry")
def _():
    v = IA.read({"number": 3, "body": body(2), "comments": [c(PROMPT), c(IMG1), c(IMG2)]})
    assert v["ready"], v
    assert len(v["selected"]) == 2, v


@case("two images in ONE comment satisfy a two-image entry")
def _():
    v = IA.read({"number": 4, "body": body(2), "comments": [c(PROMPT), c(IMG1 + "\n" + IMG2)]})
    assert v["ready"], v


@case("a redraw ignores the image from the previous prompt")
def _():
    v = IA.read({"number": 5, "body": body(1), "comments": [
        c(PROMPT), c(IMG1),        # round one, finished
        c(PROMPT),                 # reprompt: round two starts here
    ]})
    assert not v["ready"], v
    assert v["images"] == [], v
    assert v["round_starts_at_comment"] == 3, v


@case("a redraw accepts the image posted after the new prompt")
def _():
    v = IA.read({"number": 6, "body": body(1), "comments": [
        c(PROMPT), c(IMG1), c(PROMPT), c(IMG2),
    ]})
    assert v["ready"], v
    assert v["selected"] == ["https://github.com/user-attachments/assets/bbbb-2222"], v


@case("a stranger's image does not advance the pipeline")
def _():
    v = IA.read({"number": 7, "body": body(1), "comments": [
        c(PROMPT), c(IMG1, login="passer-by", assoc="NONE"),
    ]})
    assert not v["ready"], v
    assert "untrusted" in v["why"], v


@case("no asset block is a refusal, however many images")
def _():
    v = IA.read({"number": 8, "body": body(1, block=False), "comments": [c(PROMPT), c(IMG1)]})
    assert not v["ready"], v
    assert "no `asset:` block" in v["why"], v


@case("a prompt in the BODY admits images from the comments")
def _():
    v = IA.read({"number": 9, "body": body(1, prompt=True), "comments": [c(IMG1)]})
    assert v["ready"], v
    assert v["prompt_in_body"] and v["round_starts_at_comment"] == 0, v


@case("the last images win when more than required are posted")
def _():
    v = IA.read({"number": 10, "body": body(2), "comments": [
        c(PROMPT), c(IMG1), c(IMG2), c(IMG3),
    ]})
    assert v["ready"], v
    assert v["selected"] == [
        "https://github.com/user-attachments/assets/bbbb-2222",
        "https://github.com/user-attachments/assets/cccc-3333",
    ], v


@case("slot destinations derive from dest when no slots list is given")
def _():
    spec = {"dest": "assets/demo/demo-x.webp", "images_required": 3}
    assert IA.slot_dests(spec) == [
        "assets/demo/demo-x.webp",
        "assets/demo/demo-x-2.webp",
        "assets/demo/demo-x-3.webp",
    ], IA.slot_dests(spec)


@case("an explicit slots list wins over the derived one")
def _():
    spec = {"dest": "assets/demo/a.webp", "images_required": 2,
            "slots": [{"dest": "assets/demo/a.webp"}, {"dest": "assets/demo/a-2.webp"}]}
    assert IA.slot_dests(spec) == ["assets/demo/a.webp", "assets/demo/a-2.webp"]


def main() -> int:
    failed = 0
    for name, fn in CASES:
        try:
            fn()
            print(f"  ok   {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL {name}\n       {e}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
