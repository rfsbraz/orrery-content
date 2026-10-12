#!/usr/bin/env python3
"""Regression tests for scripts/enrich.py.

The scheduled "Enrich content" run failed every Monday from 2026-07-27 to
2026-10-12 (e.g. run 38242247734): works carrying the placeholder
`externalIds: {openLibrary: null}` count as "lacking" an ID, so they were
enriched, and the text-insertion writer added a SECOND `openLibrary:` line
under `externalIds:` instead of filling the existing key. validate.py's
StrictLoader then rejected brandon-sanderson/works.yaml and
jim-butcher/works.yaml (duplicate key 'openLibrary'). These tests were
checked against the unfixed code first and fail there.
"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import enrich  # noqa: E402
from validate import StrictLoader  # noqa: E402

# The real shapes from main: a placeholder followed by a blank line
# (brandon-sanderson) and by more fields (jim-butcher).
SANDERSON = """\
# --- Elantris / Sel ---
- id: brandon-sanderson/elantris
  title: "Elantris"
  authorIds: [brandon-sanderson]
  published: 2005
  externalIds:
    openLibrary: null

- id: brandon-sanderson/the-hope-of-elantris
  title: "The Hope of Elantris"
  authorIds: [brandon-sanderson]
  published: 2006
  synopsis: "A short coda."
"""

BUTCHER = """\
- id: jim-butcher/storm-front
  title: "Storm Front"
  authorIds: [jim-butcher]
  published: 2000
  note: >
    Folded note text that spans
    two lines.
  externalIds:
    openLibrary: null
  images:
    cover: "https://covers.openlibrary.org/b/id/6414916-L.jpg"
  sources:
    - https://www.jim-butcher.com/books/dresden-files/storm-front/
"""


def strict_load(text):
    return yaml.load(text, Loader=StrictLoader)


class EnrichWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, text):
        path = os.path.join(self.tmp, "works.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def apply(self, text, enrichments):
        path = self.write(text)
        enrich.insert_external_ids(path, enrichments)
        with open(path, encoding="utf-8") as f:
            return f.read()

    def by_id(self, text):
        return {w["id"]: w for w in strict_load(text)}

    def test_null_placeholder_is_filled_not_duplicated(self):
        out = self.apply(SANDERSON, {"brandon-sanderson/elantris": "OL123W"})
        works = self.by_id(out)  # StrictLoader raises on a duplicate key
        self.assertEqual(works["brandon-sanderson/elantris"]["externalIds"], {"openLibrary": "OL123W"})
        self.assertEqual(out.count("openLibrary:"), 1)
        self.assertEqual(out, SANDERSON.replace("openLibrary: null", "openLibrary: OL123W"))

    def test_null_placeholder_before_more_fields(self):
        out = self.apply(BUTCHER, {"jim-butcher/storm-front": "OL5685119W"})
        work = self.by_id(out)["jim-butcher/storm-front"]
        self.assertEqual(work["externalIds"], {"openLibrary": "OL5685119W"})
        self.assertEqual(out, BUTCHER.replace("openLibrary: null", "openLibrary: OL5685119W"))

    def test_work_without_external_ids_gets_a_block(self):
        out = self.apply(SANDERSON, {"brandon-sanderson/the-hope-of-elantris": "OL9W"})
        works = self.by_id(out)
        self.assertEqual(works["brandon-sanderson/the-hope-of-elantris"]["externalIds"], {"openLibrary": "OL9W"})
        self.assertIsNone(works["brandon-sanderson/elantris"]["externalIds"]["openLibrary"])
        self.assertTrue(out.endswith('  synopsis: "A short coda."\n  externalIds:\n    openLibrary: OL9W\n'))

    def test_other_external_ids_are_kept(self):
        text = "- id: a/b\n  title: B\n  externalIds:\n    goodreads: '42'\n  canonTier: core\n"
        out = self.apply(text, {"a/b": "OL1W"})
        self.assertEqual(self.by_id(out)["a/b"]["externalIds"], {"goodreads": "42", "openLibrary": "OL1W"})
        self.assertEqual(self.by_id(out)["a/b"]["canonTier"], "core")

    def test_existing_value_is_never_overwritten(self):
        text = SANDERSON.replace("openLibrary: null", "openLibrary: OL777W")
        out = self.apply(text, {"brandon-sanderson/elantris": "OL123W"})
        self.assertEqual(out, text)

    def test_applying_twice_is_idempotent(self):
        enrichments = {"brandon-sanderson/elantris": "OL1W", "brandon-sanderson/the-hope-of-elantris": "OL2W"}
        once = self.apply(SANDERSON, enrichments)
        twice = self.apply(once, enrichments)
        self.assertEqual(once, twice)
        strict_load(twice)

    def test_real_files_from_main(self):
        """Every placeholder in the two failing wings fills cleanly."""
        root = os.path.dirname(HERE)
        for slug in ("brandon-sanderson", "jim-butcher"):
            with open(os.path.join(root, "content", "franchises", slug, "works.yaml"), encoding="utf-8") as f:
                text = f.read()
            works = strict_load(text)
            targets = {w["id"]: f"OL{i}W" for i, w in enumerate(works)
                       if not (w.get("externalIds") or {}).get("openLibrary")}
            out = self.apply(text, targets)
            for w in strict_load(out):
                if w["id"] in targets:
                    self.assertEqual(w["externalIds"]["openLibrary"], targets[w["id"]], w["id"])


class EnrichRunTwiceTest(unittest.TestCase):
    """Running the whole enrich step twice yields the same files."""

    def test_main_twice(self):
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, "content", "authors"))
            os.makedirs(os.path.join(tmp, "content", "franchises", "jim-butcher"))
            with open(os.path.join(tmp, "content", "authors", "jim-butcher.yaml"), "w") as f:
                f.write("id: jim-butcher\nname: Jim Butcher\n")
            works = os.path.join(tmp, "content", "franchises", "jim-butcher", "works.yaml")
            with open(works, "w") as f:
                f.write(BUTCHER)

            def run():
                with mock.patch.object(enrich, "ROOT", tmp), \
                        mock.patch.object(enrich, "best_match", return_value=("OL5685119W", "test")), \
                        mock.patch.object(enrich.time, "sleep"), \
                        mock.patch.object(sys, "argv", ["enrich.py"]), \
                        mock.patch("builtins.print"):
                    enrich.main()
                with open(works, encoding="utf-8") as f:
                    return f.read()

            first = run()
            second = run()
            self.assertEqual(first, second)
            self.assertEqual(strict_load(first)[0]["externalIds"], {"openLibrary": "OL5685119W"})
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
