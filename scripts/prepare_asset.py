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


CHROMA = (255, 0, 255)   # magenta: no ink, umber, parchment or terracotta is near it


def _flood_from_border(mask):
    """Which cells of a boolean mask are reachable from the frame border?

    Four-way flood, seeded from every border cell already in the mask. Used to
    separate key spill (contiguous with the background, which §5b guarantees
    touches all four edges) from an intentional magenta-hued wash inside the
    picture, which is not.

    Plain iterative dilation rather than anything cleverer: this is an
    authoring tool run on one image at a time, a corona is at most a couple of
    hundred pixels deep, and a dependency on scipy to save a second of wall
    clock is a bad trade.
    """
    import numpy as np

    reach = np.zeros_like(mask)
    reach[0, :] = mask[0, :]
    reach[-1, :] = mask[-1, :]
    reach[:, 0] = mask[:, 0]
    reach[:, -1] = mask[:, -1]

    while True:
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= mask
        if grown.sum() == reach.sum():
            return grown
        reach = grown


def key_chroma(im: Image.Image, key=CHROMA, tol: int = 90, soft: int = 60):
    """Turn a solid chroma background into real alpha.

    Generating on transparency does not survive the download, so we generate on
    a flat colour instead and key it out here. This works where rebuilding a
    flattened checkerboard did not, for one reason: magenta is nowhere in this
    palette, so a GLOBAL key is safe. The checkerboard shared its grey with the
    drawn sky, which is why that flood ate holes in the artwork.

    Fully keyed below `tol`, fully opaque above `tol + soft`, ramped between so
    antialiased edges keep partial alpha instead of a hard staircase.

    THE DESPILL PASS

    The first version of this despilled with `excess = min(r, b) - g`, which is
    only correct when the spill is balanced - true magenta, red and blue equal.
    Real spill is a warm mauve where red leads: the measured corona on five
    shipped assets sat at RGB (148, 122, 124), for which that formula computes
    an excess of 2 and returns (146, 122, 122). Still magenta, still visible,
    and it shipped five times because nothing measured the output.

    The correct operation for a magenta key is to lift green to the mean of the
    other two channels: (148, 136, 124) is a warm neutral tan, which is what
    that pixel was before the key bled into it. Green is the minimum channel in
    magenta by definition, so the gate is `r > g and b > g` - and no colour in
    this catalogue's palette has green as its minimum, which is exactly why
    magenta was chosen as the key.

    Except one: an intentional mauve or ashen cast, which docs/VISUAL.md §4a
    explicitly allows for grief. A global despill would flatten that to grey and
    silently overrule an editorial decision. So the strength is weighted by
    PROXIMITY TO THE KEYED REGION - spill is a boundary phenomenon and decays
    inward, while an intentional wash sits in the middle of the picture. The
    blurred key mask is that proximity field, for free.
    """
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - authoring tool, not CI
        raise SystemExit(
            "--chroma needs numpy (pip install numpy). It is not a CI "
            "dependency: this is an authoring tool."
        )
    from PIL import ImageFilter

    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    kr, kg, kb = key

    # Pass 1: the flat background, by distance to the key colour. This finds
    # only the untouched chroma, which is the point - it is the one region we
    # can identify with no risk of eating artwork.
    d = np.abs(r - kr) + np.abs(g - kg) + np.abs(b - kb)
    flat = d <= tol
    keyed = int(flat.sum())

    # Pass 2: magenta CHROMA, not distance to the key. A corona is a gradient
    # from the key into the artwork, and its outer half is unambiguously
    # background while sitting far outside `tol` - (201, 61, 189) is 181 away
    # from pure magenta and survived every earlier version of this function.
    # Green is the minimum channel in magenta, so `min(r,b) - g` measures how
    # magenta a pixel is regardless of how bright or washed out it has become.
    m = np.minimum(r, b) - g
    # Deliberately near zero, and NOT the same threshold the alpha ramp uses
    # below. This one only decides which pixels belong to the spill REGION, and
    # the innermost tip of a corona is barely magenta at all - the measured one
    # tapers to min(r,b) - g == 2 while still carrying a visible cast. Set this
    # to the ramp's 20 and that tip escapes, which is worth 8 points of residual
    # cast. Nothing in the palette has green as its minimum channel, so a low
    # threshold cannot leak into artwork, and reachability is doing the real
    # work of keeping it out.
    magentaish = m > 4.0

    # Which of those are spill? An intentional mauve or ashen wash (VISUAL.md
    # §4a allows one for grief) is magenta-hued too, and no per-pixel colour
    # test can tell them apart. CONNECTIVITY can: §5b requires the chroma to be
    # visible along all four edges, so the background touches the border, and a
    # corona is by definition contiguous with it. A wash inside the picture is
    # not - it is surrounded by artwork.
    #
    # A proximity blur was tried here first and is the wrong primitive: it
    # decays over a fixed radius while a corona has no fixed width, so the
    # inner half of a wide one kept its cast. Reachability has no radius.
    reach = _flood_from_border(magentaish)
    soft_reach = np.asarray(
        Image.fromarray((reach * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.5))
    ).astype(np.float32) / 255.0

    cut = np.clip((m - 20.0) / 70.0, 0.0, 1.0) * soft_reach
    alpha = np.clip((d - tol) / soft, 0.0, 1.0) * (1.0 - cut) * 255.0

    # Whatever survives inside the spill region is despilled by lifting green to
    # the mean of the other two channels, the correct operation for a magenta
    # key. Artwork outside that region is never touched.
    spill = np.maximum((r + b) / 2.0 - g, 0.0)
    spill[(r <= g) | (b <= g)] = 0.0
    g = g + spill * soft_reach

    out = np.stack([r, g, b, alpha], axis=-1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), keyed


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("slug")
    p.add_argument("entity_id")
    p.add_argument("--quality", type=int, default=82)
    p.add_argument("--no-trim", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--chroma", nargs="?", const="magenta", default=None,
                   help="key out a solid background colour (default magenta)")
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

    if a.chroma:
        key = CHROMA if a.chroma == "magenta" else tuple(
            int(a.chroma.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        im, keyed = key_chroma(im, key)
        print(f"chroma: keyed out {100 * keyed // (im.size[0] * im.size[1])}% "
              f"of the frame as rgb{key}")

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
