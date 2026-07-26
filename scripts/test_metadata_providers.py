#!/usr/bin/env python3
"""Regression tests for the metadata providers.

Both cases here are real failures found during the John Shirley wing build,
where `lookup.py <slug> --author "<name>"` - the first call every editions and
visual-metadata run is told to make - died before printing a single row. Each
test was checked against the unfixed code first and does fail there.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "metadata"))

import providers  # noqa: E402
from providers import Nasjonalbiblioteket, _nb_lang  # noqa: E402


class NbNoQueryIsAscii(unittest.TestCase):
    """The request line is encoded as ASCII, so a literal ø takes the sweep down.

    Not a Norwegian-author problem: every provider is queried before results are
    filtered by market, so an author with no Norwegian editions at all still
    crashed on the default `--markets no,en,pt`.
    """

    def test_url_the_provider_actually_builds_is_ascii(self):
        # Capture the URL the provider builds, rather than rebuilding it here -
        # a test that constructs its own string cannot fail when the provider
        # regresses, which is the whole point of this file.
        seen = {}

        def fake_get_json(url, **kwargs):
            seen["url"] = url
            return {}

        original = providers.get_json
        providers.get_json = fake_get_json
        try:
            Nasjonalbiblioteket().by_author("John Shirley")
        finally:
            providers.get_json = original

        url = seen.get("url", "")
        self.assertTrue(url, "provider did not issue a request")
        url.encode("ascii")  # raises UnicodeEncodeError on the unfixed form
        self.assertIn("mediatype:b%C3%B8ker", url)


class NbNoLanguageIsAString(unittest.TestCase):
    """nb.no returns [{"code": "eng"}], and callers do rec.language.lower()."""

    def test_dict_shape(self):
        self.assertEqual(_nb_lang([{"code": "eng"}]), "eng")

    def test_plain_string_shape_still_works(self):
        self.assertEqual(_nb_lang(["eng"]), "eng")

    def test_absent(self):
        self.assertIsNone(_nb_lang(None))
        self.assertIsNone(_nb_lang([]))

    def test_result_is_lowerable(self):
        # The exact call in lookup.py that raised AttributeError on a dict.
        self.assertEqual((_nb_lang([{"code": "ENG"}]) or "").lower(), "eng")


if __name__ == "__main__":
    unittest.main()
