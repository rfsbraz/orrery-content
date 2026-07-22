#!/usr/bin/env python3
"""Shared plumbing for metadata providers: the record shape and the HTTP layer.

A curation run costs roughly (context size x number of tool calls), because
every call re-sends the agent's whole context. That is why this package exists:
the Jo Nesbo wing's `editions` stage made **186 tool calls** and its
`visual-metadata` stage **176**, together ~880k tokens and 57 minutes, almost
all of it one-record-at-a-time lookups an agent narrated. The same work is ~40
HTTP calls inside a single script run.

The division of labour this package assumes:

    scripts  fetch, filter, verify, measure    - arithmetic, no judgement
    agent    which market, is this an omnibus  - judgement, no fetching

Every real catch on the wings built so far came from the second column (a
title-page scan filed as a cover, a German jacket on a Norwegian work, a
library barcode). None came from the first. So the first column belongs here.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "metadata")

# The Windows console is not UTF-8, and almost every record here carries an
# accent or a slashed o. Without this, printing one crashes the tool and the
# batch it just paid for is lost. Same reason as scripts/fetch.py.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

# A browser User-Agent, for the same reason fetch.py sends one: several
# publisher and library catalogues 403 a bare urllib request and serve a
# browser normally. Recorded in CURATION.md's trap registry.
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
TTL = 7 * 24 * 3600  # a catalogue record does not change during a run

# A User-Agent alone is no longer enough for a Cloudflare-fronted site. WOOK
# 403s on UA-only and serves 200 to this full set - which is why earlier runs
# concluded "the live site 403s" and fell back to web.archive.org, losing the
# current catalogue. Send these whenever fetching HTML.
BROWSER_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",   # no gzip: urllib will not transparently inflate
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


@dataclasses.dataclass
class MetaRecord:
    """One edition of one work, as a provider sees it.

    Deliberately flat and provider-agnostic: a caller should never need to know
    which source a record came from to read it, only to judge it - which is
    what `source` and `source_url` are for. Fields are Optional because real
    catalogues are patchy, and a provider must never invent a value to fill a
    column. An absent publisher is a fact about the record.
    """

    source: str
    title: str
    source_url: str | None = None
    authors: list[str] = dataclasses.field(default_factory=list)
    publisher: str | None = None
    published: str | None = None          # as printed; may be "2007" or "Oct 23, 2007"
    language: str | None = None           # ISO-ish, as the source gives it
    isbn13: str | None = None
    isbn10: str | None = None
    cover_url: str | None = None
    identifiers: dict = dataclasses.field(default_factory=dict)
    raw: dict = dataclasses.field(default_factory=dict)

    def year(self) -> int | None:
        """First 4-digit year in `published`, or None. Never guesses."""
        import re
        m = re.search(r"\b(1\d{3}|2\d{3})\b", str(self.published or ""))
        return int(m.group(1)) if m else None

    def as_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d.pop("raw", None)  # raw is for debugging, never for output
        return d


class RateLimiter:
    """One shared minimum interval per host.

    Providers are hit concurrently, so this is process-wide and locked. Without
    it the first bulk run against a public API earns a 429 and the whole batch
    is wasted - which is exactly what Google Books returned when this stack was
    first tested unauthenticated, from two different IPs.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._next: dict[str, float] = {}

    def wait(self, host: str, interval: float) -> None:
        with self._lock:
            now = time.monotonic()
            due = self._next.get(host, 0.0)
            sleep_for = max(0.0, due - now)
            self._next[host] = max(now, due) + interval
        if sleep_for:
            time.sleep(sleep_for)


LIMITER = RateLimiter()


def _cache_path(url: str) -> str:
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".json")


def get_json(
    url: str,
    *,
    interval: float = 0.5,
    ttl: int = TTL,
    refresh: bool = False,
    timeout: int = 45,
    tries: int = 3,
) -> dict | list | None:
    """GET a JSON URL, cached on disk, rate-limited per host.

    Returns the decoded body, or None if the request could not be completed.
    **None is a result, not an exception**: a caller sweeping thirty works must
    be able to record "this one had no record" without the run dying, and a
    provider that raises on a 404 turns a normal absence into an outage.

    Retries only on 429 and 5xx, with a widening backoff.

    **Failures are never cached.** An earlier version cached them like any
    other answer, and a burst of 429s from an unauthenticated Google Books
    poisoned the cache for a week: adding a working API key then changed
    nothing, because every lookup was served the stored failure. Re-fetching a
    genuine 404 next run is far cheaper than not noticing that.
    """
    os.makedirs(CACHE, exist_ok=True)
    path = _cache_path(url)
    if not refresh and os.path.exists(path):
        try:
            blob = json.load(open(path, encoding="utf-8"))
            if time.time() - blob.get("at", 0) < ttl:
                return blob.get("body")
        except (json.JSONDecodeError, OSError):
            pass  # a corrupt cache entry is not worth failing over; refetch

    host = urllib.parse.urlparse(url).netloc
    body: dict | list | None = None
    for attempt in range(tries):
        LIMITER.wait(host, interval)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read().decode("utf-8", "replace"))
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                # Widening backoff. 429 in particular means "you are early",
                # so sleeping the same amount again just earns another one.
                time.sleep(2 ** attempt * 2)
                continue
            body = None
            break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            body = None
            break

    if body is not None:
        try:
            json.dump({"at": time.time(), "body": body}, open(path, "w", encoding="utf-8"))
        except OSError:
            pass  # an unwritable cache slows the next run; it does not break this one
    return body


def get_html(
    url: str,
    *,
    interval: float = 1.0,
    ttl: int = TTL,
    refresh: bool = False,
    timeout: int = 45,
    tries: int = 3,
) -> str | None:
    """GET an HTML page with full browser headers, cached and rate-limited.

    Same contract as `get_json`: None means the page could not be fetched, and
    failures are never cached. Scraping providers are slower by default
    (`interval=1.0`) because a retail catalogue is somebody else's server.
    """
    os.makedirs(CACHE, exist_ok=True)
    path = _cache_path("html:" + url)
    if not refresh and os.path.exists(path):
        try:
            blob = json.load(open(path, encoding="utf-8"))
            if time.time() - blob.get("at", 0) < ttl:
                return blob.get("body")
        except (json.JSONDecodeError, OSError):
            pass

    host = urllib.parse.urlparse(url).netloc
    body = None
    for attempt in range(tries):
        LIMITER.wait(host, interval)
        try:
            req = urllib.request.Request(url, headers=BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(2 ** attempt * 2)
                continue
            break
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            break

    if body is not None:
        try:
            json.dump({"at": time.time(), "body": body}, open(path, "w", encoding="utf-8"))
        except OSError:
            pass
    return body


def chunked(seq: list, n: int) -> list[list]:
    """Split into batches of at most n. The whole point of this package."""
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def isbn13_ok(value: str | None) -> bool:
    """Check digit. Arithmetic, so it belongs in a script and not in a prompt."""
    digits = [c for c in str(value or "") if c.isdigit()]
    if len(digits) != 13:
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (total + int(digits[12])) % 10 == 0


# Publisher-prefix ranges, for catching an edition filed under the wrong market.
# An English ISBN on a pt-PT row is the specific trap the editions skill names,
# and it is cheap to catch here rather than by reading.
REGION_PREFIX = {
    "pt": ("978972", "978989"),
    "no": ("978821", "978822", "978823", "978824", "978825", "978826",
           "978827", "978828", "978829", "97882"),
    "en": ("9780", "9781"),
}


def region_of(isbn13: str | None) -> str | None:
    """Best-guess market from an ISBN's registration group. None when unsure."""
    s = "".join(c for c in str(isbn13 or "") if c.isdigit())
    if len(s) != 13:
        return None
    for market, prefixes in REGION_PREFIX.items():
        if any(s.startswith(p) for p in prefixes):
            return market
    return None
