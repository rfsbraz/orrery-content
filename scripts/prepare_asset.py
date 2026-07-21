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
    # Sample SMALL patches at all four corners and accept if any one of them is
    # a two-tone neutral field. One big top-left window fails as soon as the
    # artwork reaches into that corner - which it did on the second image, so
    # the check silently reported "no transparency was ever asked for" about a
    # file that had it.
    n = max(24, min(w, h) // 24)
    corners = [(0, 0), (w - n, 0), (0, h - n), (w - n, h - n)]
    for cx, cy in corners:
        px = [rgb.getpixel((x, y))
              for y in range(cy + 2, cy + n, 3)
              for x in range(cx + 2, cx + n, 3)]
        light = [q for q in px if min(q) > 230 and max(q) - min(q) <= 6]
        if len(light) < len(px) * 0.95:
            continue
        tones = {round(sum(q) / 3 / 4) * 4 for q in light}
        spread = max(tones) - min(tones)
        # The signal is the SPREAD, not how many buckets it lands in. A plain
        # white or cream background is flat (spread 0-2); a checkerboard always
        # carries two tones a few levels apart. Counting buckets rejected a real
        # checkerboard whose re-encoding smeared it across five of them.
        if len(tones) >= 2 and 3 <= spread <= 28:
            return True
    return False


def recover_alpha(im: Image.Image):
    """Undo a flattened transparency checkerboard.

    The ChatGPT export paints alpha onto its viewer checkerboard: a perfectly
    regular grid of two near-white greys, measured at a 20px pitch with 1px
    transitions. No illustration produces that, which is how we know the
    generation DID have alpha and the download lost it.

    Detect the grid, then FLOOD FILL from the border through matching pixels.
    The flood matters: a drawn sky is the same near-white grey as the
    checkerboard, so a colour test alone would eat it. The sky is enclosed by
    the artwork; the checkerboard touches the frame.

    Returns (image, pixels_cleared) or (None, 0) if no grid is found.
    """
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    row = [px[x, 8] for x in range(min(w, 400))]
    flips = [x for x in range(1, len(row)) if abs(row[x] - row[x - 1]) >= 4]
    gaps = [b - a for a, b in zip(flips, flips[1:]) if b - a > 3]
    if len(gaps) < 3:
        return None, 0
    pitch = max(set(gaps), key=gaps.count)
    if not 4 <= pitch <= 64:
        return None, 0

    rgb = im.convert("RGB")
    rp = rgb.load()

    def at(x, y):
        return px[min(max(x, 0), w - 1), min(max(y, 0), h - 1)]

    def is_checker(x, y):
        """Phase-independent: a checker pixel matches its neighbour one full
        square away and differs from the one half a square away.

        Predicting the square from (x // pitch) drifts out of phase, because
        the export is upscaled and the true pitch is fractional - which left
        one corner of a plainly checkerboarded image untouched.

        Neighbours are CLAMPED rather than bounds-rejected. Rejecting them
        meant every border pixel failed, and since the flood starts at the
        border it could never begin at all.
        """
        r, gg, b = rp[x, y]
        if max(r, gg, b) - min(r, gg, b) > 6 or min(r, gg, b) < 225:
            return False
        here = px[x, y]
        # `pitch` is the SQUARE size, so the pattern's PERIOD is two squares:
        # the same tone repeats at 2*pitch and the opposite tone sits at
        # 1*pitch. Testing at pitch/2 compared a pixel with itself and the
        # whole detector returned nothing.
        span, step = 2 * pitch, pitch
        dx = span if x + span < w else -span
        dy = span if y + span < h else -span
        hx = step if x + step < w else -step
        hy = step if y + step < h else -step
        return (abs(here - at(x + dx, y)) <= 4 and abs(here - at(x + hx, y)) >= 3) or                (abs(here - at(x, y + dy)) <= 4 and abs(here - at(x, y + hy)) >= 3)

    out = im.convert("RGBA")
    a = Image.new("L", (w, h), 255)
    ap = a.load()
    seen = bytearray(w * h)
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] +             [(x, y) for y in range(h) for x in (0, w - 1)]
    cleared = 0
    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h):
            continue          # bounds BEFORE the index, or the flood walks off
        i = y * w + x
        if seen[i] or not is_checker(x, y):
            continue
        seen[i] = 1
        ap[x, y] = 0
        cleared += 1
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    if cleared < (w * h) * 0.01:
        return None, 0
    out.putalpha(a)
    return out, cleared


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("slug")
    p.add_argument("entity_id")
    p.add_argument("--quality", type=int, default=82)
    p.add_argument("--no-trim", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--recover-alpha", action="store_true",
                   help="last resort: rebuild alpha from a flattened checkerboard (lossy)")
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
    if not has_alpha and a.recover_alpha and looks_checkerboarded(im):
        rec, cleared = recover_alpha(im)
        if rec is not None:
            pct = 100 * cleared // (im.size[0] * im.size[1])
            print(f"alpha: recovered from a flattened checkerboard "
                  f"({pct}% of the frame cleared)")
            print("  WARNING: a lossy repair, not a substitute for a real alpha "
                  "PNG. The flood leaks through soft edges into any drawn sky of "
                  "the same grey, and the 1px seams between squares survive as a "
                  "faint grid. Look at the result before filing it.",
                  file=sys.stderr)
            im, has_alpha = rec, True
    if not has_alpha and not a.force_opaque:
        checker = looks_checkerboarded(im)
        print("\nthis image has NO alpha channel.", file=sys.stderr)
        if checker:
            print(
                "a transparency checkerboard has been flattened into the pixels. "
                "The grid is machine-regular, so the generation DID produce alpha "
                "and the DOWNLOAD lost it - the prompt is not the problem. Get the "
                "original PNG with its alpha channel (the API returns one directly "
                "with background=transparent). --recover-alpha can rebuild it "
                "approximately, but it eats any drawn sky of the same grey and "
                "leaves a faint grid, so treat it as a diagnostic.",
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
