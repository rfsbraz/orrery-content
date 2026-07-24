#!/usr/bin/env python3
"""The illustration-type catalogue as plain data, with no heavy dependencies.

docs/VISUAL.md §3b is the source of truth; this is the machine-readable copy
several scripts need. It lives on its own precisely because it is needed by
scripts on both sides of a dependency line: `prepare_asset.py` does the image
work and imports Pillow and numpy, but `issue_sync.py` only writes issue text
and runs in a CI job that installs nothing but pyyaml. When `issue_sync`
imported these sets straight from `prepare_asset`, it dragged Pillow in behind
them and the Asset queue workflow died on `ModuleNotFoundError: No module named
'PIL'`. A constant should never require an image library to read.

Keep this in sync with docs/VISUAL.md §3b and with `validate.py`'s own copy of
`ILLUSTRATION_TYPES` (that one is duplicated deliberately, so the validator has
no import at all).
"""
from __future__ import annotations

# The 25 illustration-type slugs (docs/VISUAL.md §3b).
ILLUSTRATION_TYPES = {
    "establishing-landscape", "place-portrait", "domestic-interior",
    "workplace-workshop", "aftermath-scene", "public-event-tableau",
    "journey-transit", "historical-context-tableau", "editorial-portrait",
    "relationship-tableau", "portrait-of-absence", "isolated-object",
    "symbolic-still-life", "book-object", "document-facsimile",
    "manuscript-proof", "archive-stack", "press-media-collage", "map-route",
    "process-diagram", "network-constellation", "serial-contact-sheet",
    "emblem-seal", "palimpsest-erasure", "atmospheric-motif-field",
}

# Strictly OPAQUE per §3b's table - no transparent alternative is offered at
# all for these, unlike "opaque or transparent" / "opaque pale or transparent"
# types, which stay on the default chroma+dissolve path because the doc
# genuinely asks gpt-image for alpha on them.
#
# AMBIGUOUS IN THE SPEC: the brief that produced this list named only three
# examples - `establishing-landscape`, an "immersion" subject, and
# `full-bleed-vista` - and the last of those is actually an ORGANISATION
# (docs/LAYOUT.md), not one of §3b's illustration types; LAYOUT.md does fix
# full-bleed-vista's background as opaque too, but its Holds list mixes
# strictly-opaque types with "opaque or transparent" ones (place-portrait,
# map-route, journey-transit). This set generalises the examples to every
# §3b type whose background is unambiguously "opaque" in the table, which is
# the closest concrete reading; worth a second look against VISUAL.md if a
# narrower list (just the named examples) was actually intended.
OPAQUE_TYPES = {
    "establishing-landscape", "place-portrait", "domestic-interior",
    "workplace-workshop", "aftermath-scene", "public-event-tableau",
    "historical-context-tableau", "relationship-tableau", "portrait-of-absence",
}

# §3b's edge rule: these draw their own paper edge and must SKIP the frame
# dissolve outright - equivalent to always passing --no-dissolve.
ARTIFACT_TYPES = {"document-facsimile", "manuscript-proof", "archive-stack"}
