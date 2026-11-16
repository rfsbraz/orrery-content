#!/usr/bin/env python3
"""The McDougal/Sanderson succession must agree with published dates.

Harriet McDougal chose Sanderson in December 2007. The Hero of Ages, the
ending of the first Mistborn trilogy, was published in 2008, so a claim
that she had already read that ending cannot stand. These tests fail on
the unfixed franchise event wording.
"""
import os
import re
import sys
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from validate import StrictLoader  # noqa: E402

JORDAN_EVENTS = os.path.join(ROOT, "content/franchises/robert-jordan/events.yaml")
SANDERSON_AUTHOR = os.path.join(ROOT, "content/authors/brandon-sanderson.yaml")
SANDERSON_WORKS = os.path.join(ROOT, "content/franchises/brandon-sanderson/works.yaml")
PT_JORDAN_EVENTS = os.path.join(
    ROOT, "content/i18n/pt-PT/franchises/robert-jordan/events.yaml"
)


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=StrictLoader)


def _find(items, eid):
    for item in items or []:
        if item.get("id") == eid:
            return item
    raise AssertionError(f"missing id {eid}")


def _text(item):
    return " ".join(
        part for part in (item.get("description"), item.get("note"), item.get("synopsis")) if part
    )


TRILOGY_ENDING = re.compile(
    r"ending of his Mistborn trilogy|final da sua trilogia Mistborn",
    re.IGNORECASE,
)


class McDougalSuccession(unittest.TestCase):
    def test_hero_of_ages_was_published_in_2008(self):
        work = _find(_load(SANDERSON_WORKS), "brandon-sanderson/the-hero-of-ages")
        self.assertEqual(work.get("published"), 2008)

    def test_franchise_event_names_the_final_empire_not_the_trilogy_ending(self):
        ev = _find(_load(JORDAN_EVENTS), "wot-sanderson-chosen-2007")
        text = _text(ev)
        self.assertRegex(text, r"\[\[work:brandon-sanderson/the-final-empire")
        self.assertIsNone(
            TRILOGY_ENDING.search(text),
            "the 2007 choice cannot rest on a trilogy ending published in 2008",
        )

    def test_author_event_names_the_final_empire(self):
        author = _load(SANDERSON_AUTHOR)
        ev = _find(author.get("lifeEvents") or author.get("events") or [], "sanderson-wot-succession-2007")
        # life events may be nested under a key — try a few shapes
        text = _text(ev)
        self.assertRegex(text, r"\[\[work:brandon-sanderson/the-final-empire")
        self.assertIsNone(TRILOGY_ENDING.search(text))

    def test_portuguese_event_matches_the_final_empire_version(self):
        ev = _find(_load(PT_JORDAN_EVENTS), "wot-sanderson-chosen-2007")
        text = _text(ev)
        self.assertRegex(text, r"\[\[work:brandon-sanderson/the-final-empire")
        self.assertIsNone(TRILOGY_ENDING.search(text))


if __name__ == "__main__":
    # Author file shape may use life-events; discover it if the default path fails
    unittest.main()
