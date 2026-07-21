#!/usr/bin/env python3
"""Keep the sanctuary rule identical in every curation skill.

The rule that content YAML carries data and never process is the one every
stage has broken at least once, and an indirection ("see CURATION.md") is what
let it happen: agents read the contract and still wrote to a colleague. So the
rule lives verbatim inside every SKILL.md, and this script is what stops the
copies from drifting.

    python scripts/sync_sanctuary_block.py           # check, exit 1 on drift
    python scripts/sync_sanctuary_block.py --write   # insert or update it
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK_PATH = os.path.join(ROOT, "scripts", "sanctuary_block.md")
HEADING = "## The sanctuary rule"


def block() -> str:
    with open(BLOCK_PATH, encoding="utf-8") as f:
        return f.read().strip() + "\n"


def anchor(lines: list[str]) -> int:
    """Line after the paragraph that points the skill at CURATION.md.

    Never 0: an earlier version fell back to the top of the file and inserted
    the block above franchise-research's YAML frontmatter, which would have
    stopped the skill loading at all. A wrong-but-valid position is recoverable;
    a broken file is not.
    """
    for i, line in enumerate(lines):
        if "CURATION" in line:
            for j in range(i, len(lines)):
                if not lines[j].strip():
                    return j + 1
    # no mention of the contract at all: after the frontmatter, never above it
    if lines and lines[0].startswith("---"):
        for j in range(1, len(lines)):
            if lines[j].startswith("---"):
                return j + 2
    return len(lines)


def current(lines: list[str]) -> tuple[int, int] | None:
    for i, line in enumerate(lines):
        if line.startswith(HEADING):
            # the block carries no headings of its own, so it ends at the next
            # one of ANY level - stopping only at "## " swallowed the "###"
            # subsections that follow it in six skills
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#"):
                    return i, j
            return i, len(lines)
    return None


def main() -> int:
    write = "--write" in sys.argv
    want = block()
    drifted = []
    for path in sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md"))):
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        found = current(lines)
        have = "".join(lines[found[0]:found[1]]).strip() + "\n" if found else None
        if have == want:
            continue
        drifted.append(os.path.relpath(path, ROOT))
        if not write:
            continue
        if found:
            lines[found[0]:found[1]] = [want, "\n"]
        else:
            lines[anchor(lines):anchor(lines)] = [want, "\n"]
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    if not drifted:
        print("OK - the sanctuary rule is identical in every skill.")
        return 0
    verb = "updated" if write else "drifted or missing"
    print(f"{len(drifted)} skill(s) {verb}:")
    for p in drifted:
        print(f"  {p}")
    return 0 if write else 1


if __name__ == "__main__":
    sys.exit(main())
