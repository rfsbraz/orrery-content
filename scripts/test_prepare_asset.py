#!/usr/bin/env python3
"""Does the chroma key actually remove a corona, and does it spare a wash?

    python scripts/test_prepare_asset.py

Written because `prepare_asset.py --chroma` shipped a despill that did not
work, and nothing noticed for five assets. The old formula was
`excess = min(r, b) - g`, which is only correct when the spill is balanced.
Real spill is a warm mauve where red leads: the measured corona sat at
RGB (148, 122, 124), for which that formula computes an excess of 2.

This test was written to FAIL first, and did, three times:

  1. against the original despill formula       - corona cast 54.7
  2. against a proximity-blur gate              - corona cast 45.8 (the blur
     decays over a fixed radius; a corona has no fixed width)
  3. against a reachability gate thresholded at
     the same value as the alpha ramp           - corona cast  8.5 (the
     innermost tip of a corona is barely magenta and escaped the region)

Only then did it pass at 1.6. A guard nobody has watched fail is not a guard,
and this file exists so the next person changing that function has one.
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_prepare_asset():
    path = os.path.join(ROOT, "scripts", "prepare_asset.py")
    spec = importlib.util.spec_from_file_location("prepare_asset", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_fixture(np, Image):
    """A magenta frame, a tan disc, a mauve wash inside it, a corona around it.

    The corona interpolates from pure key to the measured (148, 122, 124), which
    is what the model actually produces when it eases artwork into the chroma
    instead of breaking it up. The wash is the case §4a explicitly allows and
    the despill must not touch.
    """
    n = 512
    a = np.full((n, n, 3), 0, dtype=np.float32)
    a[:, :] = (255, 0, 255)

    yy, xx = np.mgrid[0:n, 0:n]
    dist = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2)

    art = dist < 150
    a[art] = (190, 175, 150)          # warm neutral artwork
    wash = dist < 70
    a[wash] = (150, 120, 145)         # intentional mauve, must survive

    halo = (dist >= 150) & (dist < 210)
    t = ((210 - dist[halo]) / 60.0)[:, None]
    a[halo] = np.array([255, 0, 255]) * (1 - t) + np.array([148, 122, 124]) * t

    return Image.fromarray(a.astype(np.uint8)), dist, art, wash, halo


def main() -> int:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        print(f"SKIP: needs numpy and pillow ({exc})")
        return 0

    pa = load_prepare_asset()
    src, dist, art, wash, halo = build_fixture(np, Image)
    out, _ = pa.key_chroma(src)

    o = np.asarray(out).astype(np.float32)
    rgb, alpha = o[..., :3], o[..., 3]

    def cast(mask):
        m = mask & (alpha > 120)
        if not m.any():
            return 0.0
        v = rgb[m]
        return float(((v[:, 0] + v[:, 2]) / 2 - v[:, 1]).mean())

    background = alpha[dist > 240]
    keyed = float((background < 10).mean())
    corona = cast(halo)
    intentional = cast(wash)

    print(f"background keyed:      {keyed:.1%} fully transparent   (want >= 99%)")
    print(f"corona magenta cast:   {corona:6.2f}                (want <= 8)")
    print(f"intentional wash cast: {intentional:6.2f}                (want >= 20)")

    failures = []
    if keyed < 0.99:
        failures.append("the flat background was not keyed out")
    if corona > 8:
        failures.append(f"the corona survived the despill (cast {corona:.2f})")
    if intentional < 20:
        failures.append(
            f"the intentional mauve wash was flattened (cast {intentional:.2f}) - "
            f"the despill is overrunning artwork it should not touch"
        )

    for f in failures:
        print(f"FAIL: {f}")
    print("FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
