#!/usr/bin/env python3
"""Fetch many URLs in ONE tool call, cached, with bounded output.

Why this exists: a curation run costs roughly (context size x number of tool
calls), because every call re-sends the agent's whole context. One wing's
editions stage made 144 sequential fetches; the pages themselves were not the
expense, the 144 re-sends were. Fetching twenty URLs here costs one call.

Three savings, all of them measurable:
  1. BATCHING     - N URLs, one tool call.
  2. CACHING      - responses persist under .cache/fetch/, so a later stage
                    re-fetching a publisher page it already paid for is free.
                    Different stages hit the same Porto Editora pages
                    constantly.
  3. BOUNDED OUT  - never dump a whole page. Print a status line, and only the
                    text you asked for (--grep) or a capped extract.

Browser User-Agent by default: portoeditora.pt, infopedia.pt, observador.pt and
BNP's catalogue all 403 or redirect a bare fetch and serve normally to one.
That is recorded in CURATION.md's trap registry and cost a stage a real source
before anyone noticed.

Usage
  python scripts/fetch.py URL [URL...]
  cat urls.txt | python scripts/fetch.py -
  python scripts/fetch.py --check URL...              # status only, for link sweeps
  python scripts/fetch.py --grep 'ISBN|1a ed' URL...  # only the matching lines
  python scripts/fetch.py --json URL...               # compact JSON, no HTML stripping
  python scripts/fetch.py --max-chars 400 URL...      # tighten the extract

Exit code is 0 only when EVERY URL resolved, so a stage can branch on "did that
all work" without reading the output. Cached responses expire after --ttl
seconds (a week by default; a publisher page does not change mid-run).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache", "fetch")

# Almost everything fetched here is Portuguese, and the Windows console is not
# UTF-8: without this, printing an extract containing an accent crashes the tool
# with a UnicodeEncodeError and the agent loses the whole batch it just paid for.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
TTL = 7 * 24 * 3600  # a publisher page does not change during a run
TAGS = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S | re.I)
SPACE = re.compile(r"[ \t\r\f\v]+")
BLANK = re.compile(r"\n\s*\n+")


def cache_path(url: str) -> str:
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json")


def get(url: str, timeout: int, refresh: bool, ttl: int) -> dict:
    path = cache_path(url)
    fresh = os.path.exists(path) and (ttl < 0 or time.time() - os.path.getmtime(path) <= ttl)
    if not refresh and fresh:
        try:
            with open(path, encoding="utf-8") as f:
                hit = json.load(f)
            hit["cached"] = True
            return hit
        except (OSError, ValueError):
            pass  # a corrupt cache entry is a reason to refetch, not to fail

    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    })
    out = {"url": url, "cached": False}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            out["status"] = r.status
            out["type"] = r.headers.get("Content-Type", "").split(";")[0]
            out["body"] = raw.decode(r.headers.get_content_charset() or "utf-8", "replace")
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        out["type"] = e.headers.get("Content-Type", "").split(";")[0] if e.headers else ""
        out["body"] = ""
    except Exception as e:  # DNS, TLS, timeout - a failure is a result, not a crash
        out["status"] = 0
        out["type"] = ""
        out["body"] = ""
        out["error"] = f"{type(e).__name__}: {e}"

    out["bytes"] = len(out["body"])
    os.makedirs(CACHE, exist_ok=True)
    try:
        with open(cache_path(url), "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in out.items() if k != "cached"}, f)
    except OSError:
        pass
    return out


def to_text(body: str) -> str:
    text = TAGS.sub(" ", body)
    for ent, ch in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'),
                    ("&#39;", "'"), ("&lt;", "<"), ("&gt;", ">")):
        text = text.replace(ent, ch)
    return BLANK.sub("\n", SPACE.sub(" ", text)).strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("urls", nargs="*")
    p.add_argument("--check", action="store_true", help="status line only")
    p.add_argument("--grep", help="print only lines matching this regex")
    p.add_argument("--context", type=int, default=0, help="chars of context around a --grep hit")
    p.add_argument("--max-chars", type=int, default=1200, help="cap per-URL extract")
    p.add_argument("--max-hits", type=int, default=12, help="cap --grep hits per URL")
    p.add_argument("--timeout", type=int, default=25)
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--refresh", action="store_true", help="ignore the cache")
    p.add_argument("--ttl", type=int, default=TTL, help="cache lifetime in seconds, -1 to never expire")
    p.add_argument("--json", action="store_true", help="treat bodies as JSON: no HTML stripping")
    p.add_argument("--save", metavar="DIR",
                   help="write raw bytes to DIR instead of decoding (images and other binaries)")
    a = p.parse_args()

    urls = list(a.urls)
    if urls == ["-"] or not urls:
        urls = [ln.strip() for ln in sys.stdin if ln.strip()]
    urls = list(dict.fromkeys(urls))  # dedupe, keep order
    if not urls:
        print("no URLs given", file=sys.stderr)
        return 2

    # Binary needs its own path: the normal one decodes as UTF-8 and would
    # mangle an image. Without this a stage that has to LOOK at a cover writes
    # its own downloader, which is exactly the duplicated work this tool exists
    # to remove.
    if a.save:
        os.makedirs(a.save, exist_ok=True)
        ok = 0
        for u in urls:
            name = re.sub(r"[^A-Za-z0-9._-]", "_", u.split("/")[-1] or "download")[:80]
            dest = os.path.join(a.save, name)
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=a.timeout) as r:
                    raw = r.read()
                with open(dest, "wb") as f:
                    f.write(raw)
                print(f"[{r.status}] {len(raw):>8}b  {dest}")
                ok += 1
            except Exception as e:
                print(f"[err] {type(e).__name__}: {e}  {u}")
        print(f"{ok}/{len(urls)} saved to {a.save}")
        return 0 if ok == len(urls) else 1

    started = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(lambda u: get(u, a.timeout, a.refresh, a.ttl), urls))

    ok = 0
    for r in results:
        flag = "cache" if r["cached"] else "live "
        note = f"  {r['error']}" if r.get("error") else ""
        print(f"[{r['status']}] {flag} {r['bytes']:>7}b  {r['url']}{note}")
        if r["status"] == 200:
            ok += 1
        if a.check or r["status"] != 200 or not r["body"]:
            continue

        text = r["body"] if (a.json or "json" in r["type"]) else to_text(r["body"])
        if a.grep:
            rx = re.compile(a.grep, re.I)
            hits = 0
            for m in rx.finditer(text):
                s = max(0, m.start() - a.context)
                e = min(len(text), m.end() + a.context)
                print(f"    | {text[s:e].strip()}")
                hits += 1
                if hits >= a.max_hits:
                    print(f"    | ... more hits suppressed (--max-hits {a.max_hits})")
                    break
            if not hits:
                print("    | (no match)")
        else:
            extract = text[: a.max_chars]
            print(f"    | {extract}")
            if len(text) > a.max_chars:
                print(f"    | ... truncated, {len(text) - a.max_chars} chars left (--max-chars)")

    print(f"\n{ok}/{len(results)} ok in {time.time() - started:.1f}s"
          f" ({sum(1 for r in results if r['cached'])} from cache)")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
