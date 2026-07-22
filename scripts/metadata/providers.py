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

import json
import re

from core import MetaRecord, chunked, get_html, get_json


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


class PortoEditoraShop(Provider):
    """Shared base for the Porto Editora group's Portuguese bookshops.

    WOOK and Bertrand run the same platform: the same product-URL shape, the
    same `img.*` CDN with a `/1000x` size suffix, and - the part that makes
    this worth scraping at all - a **JSON-LD `@type: Book` block** on every
    product page carrying name, isbn, author, publisher, datePublished and
    inLanguage.

    Reading the structured data rather than the DOM is what keeps a scraper
    alive: it is data the site publishes deliberately, so it survives a
    redesign that would break every CSS selector.

    Both sit behind Cloudflare and **403 a User-Agent-only request**. They
    serve `core.BROWSER_HEADERS` normally. That distinction cost real work:
    earlier runs concluded "the live site 403s" and fell back to
    web.archive.org, which serves a stale catalogue.

    Neither is a bibliographic authority - they are shops, so BNP settles a
    disputed Portuguese date. They are the best available source for the
    **pt-PT published title, ISBN, publisher and exact release date**, which
    OpenLibrary barely holds for Portugal.

    Subclasses set `name`, `BASE`, `search_url()` and `covers_watermarked`.
    """

    interval = 1.5  # somebody else's shop; do not hammer it
    BASE = ""
    #: whether this shop stamps its own mark on cover images (see Wook)
    covers_watermarked = False
    PRODUCT = re.compile(r'href="(/livro/[^"?#]+/\d+)"')

    def search_url(self, term: str) -> str:
        raise NotImplementedError

    @staticmethod
    def _name_of(v):
        if isinstance(v, dict):
            return v.get("name")
        if isinstance(v, list):
            return ", ".join(filter(None, (PortoEditoraShop._name_of(x) for x in v)))
        return v

    def _product(self, path: str) -> MetaRecord | None:
        html = get_html(self.BASE + path, interval=self.interval)
        if not html:
            return None
        book = None
        for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
            try:
                d = json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict) and d.get("@type") == "Book":
                book = d
                break
        if not book:
            return None

        cover = book.get("image")
        if cover:
            cover = re.sub(r"/\d+x$", "", cover.rstrip("/")) + "/1000x"
        author = self._name_of(book.get("author"))
        # Bertrand prints the ISBN hyphenated, WOOK does not. Normalise, or
        # every downstream check digit and prefix test sees a different shape.
        isbn = "".join(c for c in str(book.get("isbn") or "") if c.isdigit()) or None
        lang = str(book.get("inLanguage") or "")
        return MetaRecord(
            source=self.name,
            title=book.get("name") or "",
            source_url=self.BASE + path,
            authors=[a.strip() for a in str(author).split(",")] if author else [],
            publisher=self._name_of(book.get("publisher")),
            published=book.get("datePublished"),
            # Both write the language as a Portuguese word, not a code.
            language="pt-PT" if lang.lower().startswith("portug") else (lang or None),
            isbn13=isbn,
            cover_url=cover,
            identifiers={self.name: path.rsplit("/", 1)[-1]},
            raw=book,
        )

    def by_author(self, author: str, limit: int = 40) -> list[MetaRecord]:
        html = get_html(self.search_url(author), interval=self.interval)
        if not html:
            return []
        seen: list[str] = []
        for m in self.PRODUCT.finditer(html):
            if m.group(1) not in seen:
                seen.append(m.group(1))
        out = []
        for path in seen[:limit]:
            rec = self._product(path)
            if rec:
                out.append(rec)
        return out


class Wook(PortoEditoraShop):
    """WOOK. Good for pt-PT records; **its covers are watermarked and unusable.**

    Every `img.wook.pt` image carries a diagonal "wook" mark in the
    bottom-right corner - invisible in a thumbnail, obvious at `/1000x`, and
    worse the higher the resolution goes. That is precisely the "watermarked
    scrape" the visual-metadata skill names: it passes every automated check
    and is not licensable. `cover_url` is still returned, because looking at a
    jacket is a good way to confirm WHICH edition a record is, but it belongs
    in a candidate table and never in `images.cover`. Use Bertrand instead.

    Searching WOOK **by ISBN does not work** - it falls back to unrelated
    recommendations rather than returning nothing, which is worse than an empty
    result because it looks like an answer. Search by author or title.
    """

    name = "wook"
    BASE = "https://www.wook.pt"
    covers_watermarked = True
    authoritative_for = "pt-PT records; covers are watermarked, do not use them"

    def search_url(self, term: str) -> str:
        return f"{self.BASE}/pesquisa?keyword={urllib.parse.quote(term)}"


class Bertrand(PortoEditoraShop):
    """Bertrand. The same records as WOOK, and **clean, unwatermarked covers.**

    This is the pt-PT cover source. Checked at `/1000x` (1000x1547) with the
    corner cropped and inspected: no retailer mark anywhere on the image, where
    the equivalent WOOK image is stamped.

    Note the search path differs from WOOK's - `/pesquisa/<term>` rather than a
    query parameter - which is why `search_url` is a method rather than a
    format string on the base.

    **Rights:** these are publisher jacket images on a retailer's CDN. Anything
    written into `images.cover` from here needs `coverCredit` and `coverSource`
    filled the same way any other sourced image does.
    """

    name = "bertrand"
    BASE = "https://www.bertrand.pt"
    covers_watermarked = False
    authoritative_for = "pt-PT records AND clean covers; the pt cover source"

    def search_url(self, term: str) -> str:
        return f"{self.BASE}/pesquisa/{urllib.parse.quote(term)}"


class ShopifyShop(Provider):
    """Any Shopify bookshop. No scraping at all - Shopify exposes JSON.

    Portuguese publishing has a long tail of small houses on Shopify, and they
    all speak the same three endpoints, so one class covers every one of them:

        /search/suggest.json?q=...&resources[type]=product   discovery
        /products/<handle>.json                              the full record
        /products.json?limit=250&page=N                      the whole catalogue

    This is the cheapest source in the stack: no HTML, no selectors, nothing to
    break on a redesign. `barcode` (and usually `sku`) on the first variant is
    the **ISBN-13**, which is what makes these shops worth having at all.

    **`vendor` is NOT reliably the publisher.** almadoslivros puts the AUTHOR
    there ("Robert Bryndza"), Presença puts the IMPRINT ("Presença"). Mapping
    it blindly would make the catalogue assert something the source does not
    say, so each shop declares `vendor_is` and anything else stays empty.

    **The catalogue listing omits `barcode`.** `/products.json` is fine for
    discovering handles and useless for ISBNs; fetch the per-product `.json`
    for those.

    Covers come from the Shopify CDN and are the publisher's own uploads - no
    retailer watermark, unlike WOOK. Checked at full size on almadoslivros
    (914x1386, clean; the "alma dos livros" mark on the jacket is the imprint's
    own, printed on the book).

    To add another Shopify bookshop: subclass, set `name`, `BASE` and
    `vendor_is`. Nothing else.
    """

    interval = 1.0
    BASE = ""
    #: what this shop puts in `vendor`: "author", "publisher", or None if unknown
    vendor_is: str | None = None

    def _record(self, product: dict, handle: str) -> MetaRecord | None:
        if not product.get("title"):
            return None
        variants = product.get("variants") or []
        isbn = None
        for v in variants:
            cand = str(v.get("barcode") or v.get("sku") or "")
            digits = "".join(c for c in cand if c.isdigit())
            if len(digits) == 13:
                isbn = digits
                break
        images = product.get("images") or []
        vendor = product.get("vendor")
        return MetaRecord(
            source=self.name,
            title=product.get("title"),
            source_url=f"{self.BASE}/products/{handle}",
            authors=[vendor] if (vendor and self.vendor_is == "author") else [],
            publisher=vendor if self.vendor_is == "publisher" else None,
            published=(product.get("published_at") or "")[:10] or None,
            language="pt-PT",   # these are Portuguese-market shops
            isbn13=isbn,
            cover_url=(images[0].get("src") if images else None),
            identifiers={self.name: handle},
            raw=product,
        )

    def _by_handle(self, handle: str) -> MetaRecord | None:
        d = get_json(f"{self.BASE}/products/{handle}.json", interval=self.interval)
        if not isinstance(d, dict):
            return None
        return self._record(d.get("product") or {}, handle)

    def by_author(self, author: str, limit: int = 20) -> list[MetaRecord]:
        url = (f"{self.BASE}/search/suggest.json?q={urllib.parse.quote(author)}"
               f"&resources[type]=product&resources[limit]={min(limit, 10)}")
        d = get_json(url, interval=self.interval) or {}
        prods = (((d.get("resources") or {}).get("results") or {}).get("products")) or []
        out = []
        for p in prods[:limit]:
            handle = p.get("handle")
            if not handle:
                continue
            rec = self._by_handle(handle)
            if rec:
                out.append(rec)
        return out


class AlmaDosLivros(ShopifyShop):
    """Alma dos Livros. Shopify; `vendor` holds the AUTHOR."""

    name = "almadoslivros"
    BASE = "https://almadoslivros.pt"
    vendor_is = "author"
    authoritative_for = "its own pt-PT list; clean covers"


class Presenca(ShopifyShop):
    """Editorial Presença. Shopify; `vendor` holds the IMPRINT."""

    name = "presenca"
    BASE = "https://www.presenca.pt"
    vendor_is = "publisher"
    authoritative_for = "its own pt-PT list; clean covers"



#: Registration order is preference order for callers that merge sources:
#: batching and breadth first, then the gap-filler, then the narrow authority.
ALL: list[Provider] = [OpenLibrary(), GoogleBooks(), Nasjonalbiblioteket(),
                       Bertrand(), Wook(), AlmaDosLivros(), Presenca()]

BY_NAME = {p.name: p for p in ALL}
