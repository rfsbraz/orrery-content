#!/usr/bin/env python3
"""Turn a generated PNG into a filed sketch: check alpha, trim, convert, place.

    python scripts/prepare_asset.py <image> <wing-slug> <entity-id>
    python scripts/prepare_asset.py in.png valter-hugo-mae vhm-born-1971 --dry-run

Three jobs, each of which has already gone wrong once by hand:

1. REFUSE A FLATTENED IMAGE. Every sketch must carry real alpha - the layout
   depends on the page showing through. A file exported or screenshotted
   without it arrives as an opaque rectangle, and on a near-black wing that is
   a bright slab. The giveaway is a transparency checkerboard baked into the
   pixels, so this looks for that too and names it, rather than filing a broken
   asset that validates green.
2. TRIM THE EMPTY MARGINS. A sketch of a landscape under an open sky leaves the
   sky transparent, so a third of the frame can be nothing. The app renders
   with object-contain, which scales to the whole frame including the void, and
   the art comes out small for no reason. Cropping to the alpha bounding box
   costs nothing and is not a judgement call.
3. CONVERT AND CAP. webp, under the size the validator enforces, in the right
   place with the right name.
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_BYTES = 320_000


def looks_checkerboarded(im: Image.Image) -> bool:
    """A flattened transparent export carries the viewer's checkerboard.

    Sample a corner: a baked checkerboard alternates between two near-white
    greys on a regular pitch, which no drawn sky does.
    """
    rgb = im.convert("RGB")
    w, h = rgb.size
    step = max(4, min(w, h) // 128)
    px = [rgb.getpixel((x, y))
          for y in range(step, min(h, step * 16), step)
          for x in range(step, min(w, step * 16), step)]
    light = [p for p in px if min(p) > 230]
    if len(light) < len(px) * 0.9:
        return False
    # Bucket coarsely: re-encoding jitters each square by a few levels, so the
    # raw tone count runs into the dozens and an exact-match test misses the
    # very case it exists for - which is worse than no test, because it sends
    # someone off to re-roll a generation that was fine.
    tones = {round(sum(p) / 3 / 4) * 4 for p in light}
    spread = max(tones) - min(tones)
    return 2 <= len(tones) <= 4 and 3 <= spread <= 24


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("slug")
    p.add_argument("entity_id")
    p.add_argument("--quality", type=int, default=82)
    p.add_argument("--no-trim", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force-opaque", action="store_true",
                   help="file an image with no alpha anyway (era plates only)")
    a = p.parse_args()

    if not os.path.exists(a.image):
        print(f"no such file: {a.image}", file=sys.stderr)
        return 2
    im = Image.open(a.image)
    print(f"in : {im.size[0]}x{im.size[1]} {im.mode} "
          f"{os.path.getsize(a.image) // 1000}KB")

    has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
    if not has_alpha and not a.force_opaque:
        checker = looks_checkerboarded(im)
        print("\nthis image has NO alpha channel.", file=sys.stderr)
        if checker:
            print(
                "it looks like a transparency checkerboard has been flattened "
                "into the pixels - the generation almost certainly DID produce "
                "alpha and it was lost on the way here (a screenshot, or an "
                "export that dropped it). Fetch the original PNG.",
                file=sys.stderr,
            )
        else:
            print(
                "it was probably generated without a transparent background. "
                "Re-roll asking for one; on a dark wing an opaque rectangle is "
                "a bright slab.",
                file=sys.stderr,
            )
        print("(era plates are opaque by design: pass --force-opaque)", file=sys.stderr)
        return 1

    im = im.convert("RGBA") if has_alpha else im.convert("RGB")
    if has_alpha and not a.no_trim:
        box = im.getchannel("A").getbbox()
        if box and box != (0, 0, *im.size):
            before = im.size
            im = im.crop(box)
            print(f"trim: {before[0]}x{before[1]} -> {im.size[0]}x{im.size[1]} "
                  f"(dropped empty margins)")

    rel = os.path.join("assets", a.slug, f"{a.entity_id}.webp")
    out = os.path.join(ROOT, rel)
    if a.dry_run:
        print(f"would write {rel}")
        return 0

    os.makedirs(os.path.dirname(out), exist_ok=True)
    quality = a.quality
    while True:
        im.save(out, "WEBP", quality=quality, method=6, lossless=False)
        size = os.path.getsize(out)
        if size <= MAX_BYTES or quality <= 50:
            break
        quality -= 8
    print(f"out: {rel}  {size // 1000}KB  q{quality}")
    if size > MAX_BYTES:
        print(f"still over the {MAX_BYTES // 1000}KB cap - shrink the image",
              file=sys.stderr)
        return 1
    print(f"\nfile it on the entity:\n"
          f"    images:\n"
          f"      sketch: {rel.replace(os.sep, '/')}\n"
          f"      sketchCredit: Generated for Orrery (gpt-image-1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
