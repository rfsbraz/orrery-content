#!/usr/bin/env python3
"""Gather edition and cover candidates for a wing, in one tool call.

    python scripts/metadata/lookup.py jo-nesbo --author "Jo Nesbo"
    python scripts/metadata/lookup.py jo-nesbo --author "Jo Nesbo" --markets no,en,pt
    python scripts/metadata/lookup.py --verify-isbns jo-nesbo
    python scripts/metadata/lookup.py --check-covers jo-nesbo

This replaces the fetching half of the `editions` and `visual-metadata` stages.
It does not replace their judgement: it produces a candidate table and leaves
which-market, is-this-an-omnibus and is-this-a-title-page to a reader. Every
real catch on the wings built so far was one of those, and none of them was a
lookup.

Cost, measured on the Jo Nesbo wing (34 works):
    before   editions 186 tool calls + visual-metadata 176 = ~880k tokens, 57 min
    after    ~40 HTTP requests inside ONE tool call

Output is TSV by default because a table is the cheapest thing for an agent to
read, and `--json` when something downstream needs to parse it.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from core import ROOT, MetaRecord, isbn13_ok, region_of  # noqa: E402
from providers import ALL, BY_NAME, OpenLibrary  # noqa: E402

MARKET_LANG = {"no": {"nor", "nob", "nno", "no"}, "en": {"eng", "en"},
               "pt": {"por", "pt", "pt-PT"}}


def wing_works(slug: str) -> list[dict]:
    p = os.path.join(ROOT, "content", "franchises", slug, "works.yaml")
    d = yaml.safe_load(io.open(p, encoding="utf-8"))
    return d["works"] if isinstance(d, dict) else (d or [])


def wing_editions(slug: str) -> list[dict]:
    p = os.path.join(ROOT, "content", "franchises", slug, "editions.yaml")
    if not os.path.exists(p):
        return []
    d = yaml.safe_load(io.open(p, encoding="utf-8"))
    return d["editions"] if isinstance(d, dict) else (d or [])


def verify_isbns(slug: str) -> int:
    """Check digit and market prefix for every ISBN already in the wing.

    Pure arithmetic, so it costs nothing and needs no model. A valid-but-wrong
    ISBN is a reader's money, and an English prefix on a pt-PT row is the trap
    the editions skill names explicitly.
    """
    eds = wing_editions(slug)
    if not eds:
        print(f"no editions.yaml for {slug}")
        return 0
    bad = 0
    for e in eds:
        isbn, lang = e.get("isbn13"), str(e.get("language") or "")
        wid = e.get("workId", "?")
        if not isbn:
            continue
        if not isbn13_ok(isbn):
            print(f"  CHECK-DIGIT  {wid:44} {isbn}")
            bad += 1
            continue
        want = lang.split("-")[0].lower()
        got = region_of(isbn)
        if got and want in ("pt", "no", "en") and got != want:
            print(f"  REGION       {wid:44} {isbn} is {got}, row says {lang}")
            bad += 1
    print(f"\n  {len(eds)} editions, {bad} suspect")
    return bad


def check_covers(slug: str) -> int:
    """Fetch every cover URL the wing references and report the dead ones.

    Includes the URLs the app DERIVES: a work with no `images.cover` falls
    through to an ISBN-shaped OpenLibrary guess, which 404s for most
    non-anglophone ISBNs. Those render as broken images and no validator sees
    them, so they are checked here.
    """
    import urllib.request, urllib.error
    from core import UA
    works = wing_works(slug)
    eds = wing_editions(slug)
    by_work: dict[str, list[dict]] = {}
    for e in eds:
        by_work.setdefault(e.get("workId", ""), []).append(e)

    checks: list[tuple[str, str, str]] = []
    for w in works:
        wid = w["id"]
        cover = (w.get("images") or {}).get("cover")
        if cover:
            checks.append((wid, "declared", cover))
        else:
            for e in by_work.get(wid, []):
                if e.get("isbn13"):
                    checks.append((wid, "derived", f"https://covers.openlibrary.org/b/isbn/{e['isbn13']}-M.jpg"))
                    break

    dead = 0
    for wid, kind, url in checks:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                blob = r.read()
            # OpenLibrary serves a ~800-byte blank placeholder at HTTP 200, so
            # a status code is not proof. Size is the cheap discriminator.
            ok = len(blob) > 3000
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            ok = False
        if not ok:
            print(f"  DEAD  {kind:8} {wid:44} {url}")
            dead += 1
    print(f"\n  {len(checks)} cover URLs checked, {dead} dead")
    return dead


def candidates(slug: str, author: str, markets: list[str], limit: int) -> list[dict]:
    """Every edition the providers know of, tagged by market. One pass."""
    ol = OpenLibrary()
    works = ol.by_author(author, limit=limit)
    rows: list[dict] = []
    for w in works:
        key = (w.identifiers or {}).get("openlibrary_work")
        if not key:
            continue
        for ed in ol.editions_of(key):
            lang = (ed.language or "").lower()
            market = next((m for m in markets if lang in MARKET_LANG.get(m, set())), None)
            if markets and not market:
                continue
            rows.append({
                "work": w.title,
                "market": market or lang or "?",
                "title": ed.title,
                "publisher": ed.publisher or "",
                "published": ed.published or "",
                "isbn13": ed.isbn13 or "",
                "isbn_ok": isbn13_ok(ed.isbn13) if ed.isbn13 else None,
                "region": region_of(ed.isbn13) or "",
                "cover": ed.cover_url or "",
                "source_url": ed.source_url or "",
            })
    return rows


def download_covers(rows: list[dict], out_dir: str) -> int:
    """Download every candidate cover so a reader can judge them in one pass.

    This is the part that cannot be automated away, and finding that out was
    the point of building this. Run against the Jo Nesbo wing, the candidate
    search surfaced two images the `visual-metadata` agent had already refused
    after 176 calls: a scan of `Gjenferd`'s TITLE PAGE, and a `Snomannen` cover
    carrying a San Francisco Public Library barcode. A script cannot see either
    - not by size, not by status code, not by any cheap signal.

    So the saving is in the FETCHING, not the looking. Pull every candidate
    down here in one call; a reader then opens a handful of local files instead
    of paying a round trip per image.
    """
    import urllib.request, urllib.error
    from core import UA
    os.makedirs(out_dir, exist_ok=True)
    got = 0
    for r in rows:
        url = r.get("cover")
        if not url:
            continue
        name = (r.get("isbn13") or r.get("title", "x"))[:60]
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        path = os.path.join(out_dir, f"{safe}.jpg")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                blob = resp.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            continue
        # A blank OpenLibrary placeholder is ~800 bytes and returns HTTP 200,
        # so size is the only cheap discriminator. It is not a quality check.
        if len(blob) < 3000:
            continue
        with open(path, "wb") as f:
            f.write(blob)
        r["local"] = path
        got += 1
    return got


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("--author", help="author name as the sources spell it")
    p.add_argument("--markets", default="no,en,pt",
                   help="comma-separated; blank for every language")
    p.add_argument("--limit", type=int, default=100, help="works to pull from the author search")
    p.add_argument("--verify-isbns", action="store_true", help="check digits and market prefixes only")
    p.add_argument("--check-covers", action="store_true", help="fetch declared and derived cover URLs")
    p.add_argument("--json", action="store_true")
    p.add_argument("--download-covers", metavar="DIR",
                   help="pull every candidate cover into DIR so they can be LOOKED at; "
                        "a script cannot tell a jacket from a title page")
    p.add_argument("--providers", action="store_true", help="list registered providers and exit")
    a = p.parse_args()

    if a.providers:
        for prov in ALL:
            print(f"  {prov.name:16} every {prov.interval}s   {prov.authoritative_for}")
        return 0
    if a.verify_isbns:
        return 1 if verify_isbns(a.slug) else 0
    if a.check_covers:
        return 1 if check_covers(a.slug) else 0

    if not a.author:
        print("--author is required (or use --verify-isbns / --check-covers)", file=sys.stderr)
        return 2
    markets = [m for m in a.markets.split(",") if m]
    rows = candidates(a.slug, a.author, markets, a.limit)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if a.download_covers:
        n = download_covers(rows, a.download_covers)
        print(f"downloaded {n} candidate covers to {a.download_covers} - "
              f"open them before trusting any of them", file=sys.stderr)
    cols = ["market", "published", "publisher", "isbn13", "region", "title", "cover"]
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r.get(c, ""))[:60] for c in cols))
    print(f"\n{len(rows)} candidate editions across {len(set(r['work'] for r in rows))} works",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
