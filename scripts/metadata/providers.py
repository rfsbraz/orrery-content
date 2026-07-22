#!/usr/bin/env python3
"""Metadata providers. Add a source by writing one class and registering it.

Modelled on Calibre-Web Automated's `cps/metadata_provider/` (12 providers,
each a class exposing one search method), which is the arrangement that lets a
book stack add a source without touching the callers. The difference here is
that ours must **batch**: CWA looks up one book at a time because a human is
waiting on one book, while we sweep a 34-work wing and pay per tool call.

To add a provider:

  1. Subclass `Provider`. Set `name`, and `interval` if the source is touchy.
  2. Implement whichever of the three capabilities the source actually has -
     `by_isbn`, `by_author`, `editions_of`. Leave the rest; the base class
     returns empty, and callers already handle a provider that cannot answer.
  3. Add it to `ALL` at the bottom.
  4. Say in the docstring what the source is authoritative FOR. Coverage is not
     uniform: OpenLibrary is broad and anglophone-biased, a national library is
     narrow and definitive for its own country. A caller choosing between them
     needs that sentence.

A provider must never invent a field. An absent publisher is a fact about the
record, and filling it makes the catalogue assert something no source says.

Scrapers are welcome here too - the contract is the same, and a scraper that
returns `MetaRecord`s is indistinguishable to a caller. Keep the parsing inside
the provider, set a slower `interval`, and expect to maintain it: CWA carries
`amazon.py` and `scholar.py` on exactly those terms.
"""
from __future__ import annotations

import os
import urllib.parse

from core import MetaRecord, chunked, get_json


class Provider:
    """The contract. Every capability is optional; none may raise on absence."""

    name = "provider"
    #: seconds between requests to this host, enforced process-wide
    interval = 0.5
    #: what this source is authoritative for, in one line
    authoritative_for = "nothing in particular"

    def by_isbn(self, isbns: list[str]) -> dict[str, MetaRecord]:
        """ISBN-13 -> record. Batches internally where the source allows it."""
        return {}

    def by_author(self, author: str, limit: int = 100) -> list[MetaRecord]:
        """Everything the source holds for an author. One call where possible."""
        return []

    def editions_of(self, work_key: str, limit: int = 100) -> list[MetaRecord]:
        """Every edition of one work, so a caller can pick a market."""
        return []


class OpenLibrary(Provider):
    """Broad, free, no key, and the only source here that batches ISBNs.

    Authoritative for nothing, but present for almost everything, and its
    `bibkeys` endpoint answers 20+ ISBNs in one request - the single biggest
    saving available to this stack.

    Two traps, both learned by shipping them:

    - A work-level record's `language` is the UNION over its editions, so
      `['ger','pol','nob','swe']` on one row does not mean a Norwegian edition
      exists with a Norwegian cover. Go through `editions_of` for anything
      market-specific.
    - `covers.openlibrary.org/b/isbn/<isbn>-M.jpg` is a GUESS and 404s for most
      non-anglophone ISBNs, while `/b/id/<cover_i>-L.jpg` is a real image.
      Prefer a cover id; never synthesise the isbn form and call it verified.
    """

    name = "openlibrary"
    interval = 0.4
    authoritative_for = "breadth and ISBN batching; weakest on non-anglophone editions"

    BASE = "https://openlibrary.org"

    def by_isbn(self, isbns: list[str]) -> dict[str, MetaRecord]:
        out: dict[str, MetaRecord] = {}
        for batch in chunked([i for i in isbns if i], 20):
            keys = ",".join(f"ISBN:{i}" for i in batch)
            url = f"{self.BASE}/api/books?bibkeys={keys}&format=json&jscmd=data"
            data = get_json(url, interval=self.interval) or {}
            for key, rec in data.items():
                isbn = key.split(":", 1)[1] if ":" in key else key
                cover = (rec.get("cover") or {})
                out[isbn] = MetaRecord(
                    source=self.name,
                    title=rec.get("title") or "",
                    source_url=rec.get("url"),
                    authors=[a.get("name", "") for a in rec.get("authors", [])],
                    publisher=", ".join(p.get("name", "") for p in rec.get("publishers", [])) or None,
                    published=rec.get("publish_date"),
                    isbn13=isbn,
                    cover_url=cover.get("large") or cover.get("medium") or None,
                    identifiers={"openlibrary": rec.get("key")},
                    raw=rec,
                )
        return out

    def by_author(self, author: str, limit: int = 100) -> list[MetaRecord]:
        fields = "key,title,first_publish_year,publisher,language,isbn,cover_i,edition_count"
        url = (f"{self.BASE}/search.json?author={urllib.parse.quote(author)}"
               f"&limit={limit}&fields={fields}")
        data = get_json(url, interval=self.interval) or {}
        out = []
        for d in data.get("docs", []):
            cover_i = d.get("cover_i")
            out.append(MetaRecord(
                source=self.name,
                title=d.get("title") or "",
                source_url=f"{self.BASE}{d.get('key')}" if d.get("key") else None,
                publisher=", ".join(d.get("publisher", [])[:3]) or None,
                published=str(d.get("first_publish_year") or "") or None,
                # NOTE: a union over editions, not this record's language.
                language=",".join(d.get("language", [])) or None,
                cover_url=f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg" if cover_i else None,
                identifiers={"openlibrary_work": d.get("key")},
                raw=d,
            ))
        return out

    def editions_of(self, work_key: str, limit: int = 100) -> list[MetaRecord]:
        key = work_key.strip("/").removeprefix("works/")
        url = f"{self.BASE}/works/{key}/editions.json?limit={limit}"
        data = get_json(url, interval=self.interval) or {}
        out = []
        for e in data.get("entries", []):
            langs = [l.get("key", "").rsplit("/", 1)[-1] for l in e.get("languages", [])]
            isbn13 = (e.get("isbn_13") or [None])[0]
            covers = e.get("covers") or []
            out.append(MetaRecord(
                source=self.name,
                title=e.get("title") or "",
                source_url=f"{self.BASE}{e.get('key')}" if e.get("key") else None,
                publisher=", ".join(e.get("publishers", [])) or None,
                published=e.get("publish_date"),
                language=langs[0] if langs else None,
                isbn13=isbn13,
                isbn10=(e.get("isbn_10") or [None])[0],
                # A real cover id, not the isbn guess. Absent means no cover,
                # which is the answer visual-metadata spends calls establishing.
                cover_url=f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg" if covers else None,
                identifiers={"openlibrary_edition": e.get("key")},
                raw=e,
            ))
        return out


class GoogleBooks(Provider):
    """Good non-anglophone coverage and the best cover resolution available.

    Authoritative for nothing, but it fills OpenLibrary's worst gap: editions
    published outside the anglophone trade.

    **Needs an API key in practice.** The unauthenticated endpoint returned
    HTTP 429 from two separate networks when this stack was first tested, so
    treat keyless operation as best-effort. Set `GOOGLE_BOOKS_API_KEY` (free,
    Google Cloud "Books API", 1,000 requests/day by default).

    The cover trick is lifted from CWA's `cps/metadata_provider/google.py`:
    strip `&edge=curl` and append `&fife=w800-h900` to get an 800x900 image
    instead of the ~128px thumbnail the API returns by default. That is the fix
    for a cover shipped on the Nesbo wing at 96x151.
    """

    name = "googlebooks"
    interval = 1.0  # keyless is throttled hard; be a good citizen even with a key
    authoritative_for = "non-anglophone editions and high-resolution covers"

    BASE = "https://www.googleapis.com/books/v1/volumes"

    def _key_suffix(self) -> str:
        key = os.environ.get("GOOGLE_BOOKS_API_KEY", "").strip()
        return f"&key={urllib.parse.quote(key)}" if key else ""

    @staticmethod
    def _cover(volume: dict) -> str | None:
        links = volume.get("imageLinks") or {}
        url = links.get("extraLarge") or links.get("large") or links.get("thumbnail")
        if not url:
            return None
        url = url.replace("&edge=curl", "").replace("http://", "https://")
        if "fife=" not in url:
            url += "&fife=w800-h900"
        return url

    def _record(self, item: dict) -> MetaRecord | None:
        v = item.get("volumeInfo") or {}
        if not v.get("title"):
            return None
        ids = {i.get("type"): i.get("identifier") for i in v.get("industryIdentifiers", [])}
        return MetaRecord(
            source=self.name,
            title=v.get("title"),
            source_url=f"https://books.google.com/books?id={item.get('id')}",
            authors=v.get("authors", []),
            publisher=v.get("publisher"),
            published=v.get("publishedDate"),
            language=v.get("language"),
            isbn13=ids.get("ISBN_13"),
            isbn10=ids.get("ISBN_10"),
            cover_url=self._cover(v),
            identifiers={"google": item.get("id")},
            raw=item,
        )

    def by_isbn(self, isbns: list[str]) -> dict[str, MetaRecord]:
        # No batch endpoint: Google is one query per ISBN. That is why
        # OpenLibrary runs first and this fills the holes, rather than leading.
        out: dict[str, MetaRecord] = {}
        for isbn in [i for i in isbns if i]:
            data = get_json(f"{self.BASE}?q=isbn:{isbn}{self._key_suffix()}",
                            interval=self.interval) or {}
            for item in (data.get("items") or [])[:1]:
                rec = self._record(item)
                if rec:
                    rec.isbn13 = rec.isbn13 or isbn
                    out[isbn] = rec
        return out

    def by_author(self, author: str, limit: int = 40) -> list[MetaRecord]:
        q = urllib.parse.quote(f'inauthor:"{author}"')
        out = []
        for start in range(0, min(limit, 200), 40):
            data = get_json(f"{self.BASE}?q={q}&maxResults=40&startIndex={start}{self._key_suffix()}",
                            interval=self.interval) or {}
            items = data.get("items") or []
            out.extend(r for r in (self._record(i) for i in items) if r)
            if len(items) < 40:
                break
        return out


class Nasjonalbiblioteket(Provider):
    """The National Library of Norway. Legal deposit, so its silence means something.

    Authoritative for Norwegian first editions and publication dates. This is
    the source that settled `Blod pa sno` as 2015 against English Wikipedia's
    2014: deposit is mandatory in Norway, so "no 2014 edition on record" is
    strong negative evidence rather than a gap.

    Included as a worked example of a NATIONAL LIBRARY provider - the pattern
    generalises. Portugal's BNP and Germany's DNB (which CWA carries as
    `dnb.py`) occupy the same role for their markets, and a wing whose author
    publishes there should get one.
    """

    name = "nb.no"
    interval = 0.6
    authoritative_for = "Norwegian first editions; mandatory legal deposit"

    BASE = "https://api.nb.no/catalog/v1/items"

    def by_author(self, author: str, limit: int = 100) -> list[MetaRecord]:
        q = urllib.parse.quote(f'creator:"{author}"')
        url = f"{self.BASE}?q={q}&size={min(limit, 100)}&filter=mediatype:bøker"
        data = get_json(url, interval=self.interval) or {}
        out = []
        embedded = (data.get("_embedded") or {}).get("items", [])
        for it in embedded:
            md = it.get("metadata") or {}
            out.append(MetaRecord(
                source=self.name,
                title=md.get("title") or "",
                source_url=((it.get("_links") or {}).get("self") or {}).get("href"),
                authors=[c for c in (md.get("creators") or [])],
                published=str((md.get("originInfo") or {}).get("issued") or "") or None,
                language=(md.get("languages") or [None])[0],
                isbn13=next((i for i in (md.get("isbns") or []) if len(str(i).replace("-", "")) == 13), None),
                identifiers={"nb": it.get("id")},
                raw=it,
            ))
        return out


#: Registration order is preference order for callers that merge sources:
#: batching and breadth first, then the gap-filler, then the narrow authority.
ALL: list[Provider] = [OpenLibrary(), GoogleBooks(), Nasjonalbiblioteket()]

BY_NAME = {p.name: p for p in ALL}
