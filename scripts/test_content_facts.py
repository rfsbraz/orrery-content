#!/usr/bin/env python3
"""Factual invariants for canon prose that validate.py cannot see.

These are narrow regressions for claims that went stale or stacked until
they read as filler. They were checked against unfixed main first.
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

CHRISTIE_WORKS = os.path.join(ROOT, "content/franchises/agatha-christie/works.yaml")
CHRISTIE_ERAS = os.path.join(ROOT, "content/franchises/agatha-christie/eras.yaml")

# Christie's own 1972 list, as published by her official estate.
# https://www.agathachristie.com/en/about-christie/christies-favourite-christie
OFFICIAL_1972_LIST = {
    "agatha-christie/and-then-there-were-none",
    "agatha-christie/the-murder-of-roger-ackroyd",
    "agatha-christie/a-murder-is-announced",
    "agatha-christie/murder-on-the-orient-express",
    "agatha-christie/the-thirteen-problems",
    "agatha-christie/towards-zero",
    "agatha-christie/endless-night",
    "agatha-christie/crooked-house",
    "agatha-christie/ordeal-by-innocence",
    "agatha-christie/the-moving-finger",
}
OFFICIAL_1972_URL = (
    "https://www.agathachristie.com/en/about-christie/christies-favourite-christie"
)

# Unscoped "she named this among her favourites" language. Qualified claims
# (favourite creation, favourite of the Westmacott books, a readers' poll)
# are left out so they can be judged on their own sources.
UNSCOPED_FAVOURITE = re.compile(
    r"(?:personal favourite"
    r"|one of her own favourites"
    r"|among her own favourites"
    r"|counted among her favourites"
    r"|named as one of her own favourites"
    r"|A Christie personal favourite"
    r")",
    re.IGNORECASE,
)


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=StrictLoader)


def _blob(item):
    parts = [item.get("synopsis") or "", item.get("description") or "", item.get("note") or ""]
    return " ".join(parts)


def _sources(item):
    raw = item.get("sources") or []
    if isinstance(raw, str):
        return [raw]
    return list(raw)


class ChristieFavouriteClaims(unittest.TestCase):
    def test_unscoped_favourite_claims_are_on_the_1972_list_and_cite_it(self):
        works = _load(CHRISTIE_WORKS) or []
        flagged = []
        missing_source = []
        for work in works:
            wid = work.get("id")
            if not UNSCOPED_FAVOURITE.search(_blob(work)):
                continue
            if wid not in OFFICIAL_1972_LIST:
                flagged.append(wid)
            if OFFICIAL_1972_URL not in _sources(work):
                missing_source.append(wid)
        self.assertEqual(
            flagged,
            [],
            "unscoped 'Christie's favourite' claims may only appear on titles "
            "from her official 1972 list: " + ", ".join(flagged),
        )
        self.assertEqual(
            missing_source,
            [],
            "those claims must cite the official 1972 list page: "
            + ", ".join(missing_source),
        )

    def test_era_favourite_claims_cite_the_1972_list(self):
        eras = _load(CHRISTIE_ERAS) or []
        missing = []
        for era in eras:
            if not UNSCOPED_FAVOURITE.search(_blob(era)):
                continue
            if OFFICIAL_1972_URL not in _sources(era):
                missing.append(era.get("id"))
        self.assertEqual(
            missing,
            [],
            "era prose that calls books her own favourites must cite the "
            "official 1972 list page: " + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
