#!/usr/bin/env python3
"""Enrich Orrery works with external IDs from OpenLibrary.

ADDITIVE AND SAFE BY DESIGN - this is a bot that opens PRs, never touches canon
directly, and only ever *adds* metadata:

- Fills `externalIds.openLibrary` on works that lack it. Never overwrites an
  existing value, never touches any other field (titles, dates, synopses,
  orders, events are curator facts and are left alone).
- High-confidence matches only: a result must match on normalized title AND
  author AND publication year (+/- 2). Anything less is FLAGGED for a human,
  not written - a wrong match means a wrong cover/ID later.
- Writes are surgical line insertions, so the diff contains ONLY the added
  `externalIds` lines - nothing else in the file is reformatted or moved.

Reading uses yaml.safe_load (no code execution). Writes `.enrichment-report.md`
(git-ignored) for the PR body.

Usage: python scripts/enrich.py [--limit N] [--franchise slug]
"""
import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Orrery-enrichment/1.0 (+https://github.com/rfsbraz/orrery-content)"
YEAR_TOLERANCE = 2


def norm(s):
    """Lowercase, drop non-alphanumerics, collapse spaces - for title compare."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", (s or "").lower())).strip()


def author_names(work, authors):
    """All names this work could be found under: real author(s), pen name, collaborators."""
    names = []
    for aid in (work.get("authorIds") or []) + (work.get("withAuthorIds") or []):
        if aid in authors:
            names.append(authors[aid])
    if work.get("publishedAs"):
        names.append(str(work["publishedAs"]))
    return names


def ol_search(title, author):
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode({
        "title": title,
        "author": author,
        "fields": "key,title,author_name,first_publish_year",
        "limit": 5,
    })
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def best_match(work, authors):
    """Return (olid, reason) for a high-confidence match, or (None, reason)."""
    title = str(work.get("title", ""))
    ntitle = norm(title)
    year = work.get("published")
    names = author_names(work, authors)
    nnames = [norm(n) for n in names]

    for author in names:
        try:
            data = ol_search(title, author)
        except Exception as e:
            return None, f"search error: {e}"
        for doc in data.get("docs", []):
            dtitle = norm(doc.get("title", ""))
            title_ok = dtitle == ntitle or (ntitle in dtitle) or (dtitle in ntitle and len(dtitle) >= 4)
            doc_authors = [norm(a) for a in doc.get("author_name", [])]
            author_ok = any(nn in da or da in nn for nn in nnames for da in doc_authors)
            fy = doc.get("first_publish_year")
            year_ok = (not year or not fy) or abs(int(fy) - int(year)) <= YEAR_TOLERANCE
            if title_ok and author_ok and year_ok:
                olid = doc["key"].split("/")[-1]  # /works/OL...W -> OL...W
                return olid, f"matched '{doc.get('title')}' ({fy})"
        time.sleep(0.5)
    return None, "no high-confidence match"


def load_authors():
    m = {}
    for path in glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml")):
        with open(path, encoding="utf-8") as f:
            a = yaml.safe_load(f)
        if a and a.get("id"):
            m[a["id"]] = a.get("name", a["id"])
    return m


def insert_external_ids(path, enrichments):
    """Surgically add `externalIds.openLibrary` to each work block.

    enrichments: {work_id: olid}. Only inserts; never rewrites other lines.
    Works are top-level list items (`- id: <wid>`) with 2-space fields.
    """
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # Find the line index of each work's `- id:` and the end of its block.
    starts = []  # (index, work_id)
    for i, ln in enumerate(lines):
        m = re.match(r"^- id:\s*(\S+)\s*$", ln)
        if m:
            starts.append((i, m.group(1)))

    # Build insertions as (position, text) then apply back-to-front.
    inserts = []
    for n, (idx, wid) in enumerate(starts):
        if wid not in enrichments:
            continue
        block_end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        block = lines[idx:block_end]
        olid = enrichments[wid]
        # If the block already has an externalIds: key, add openLibrary under it.
        ext_line = next((idx + j for j, bl in enumerate(block)
                         if re.match(r"^  externalIds:\s*$", bl)), None)
        if ext_line is not None:
            inserts.append((ext_line + 1, f"    openLibrary: {olid}\n"))
        else:
            # Insert after the last non-blank line of the block.
            last = block_end - 1
            while last > idx and lines[last].strip() == "":
                last -= 1
            inserts.append((last + 1, f"  externalIds:\n    openLibrary: {olid}\n"))

    for pos, text in sorted(inserts, reverse=True):
        lines[pos:pos] = [text]

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="max works to enrich (0 = all)")
    ap.add_argument("--franchise", default=None, help="only this franchise slug")
    args = ap.parse_args()

    authors = load_authors()
    enriched, flagged = [], []
    processed = 0

    pattern = os.path.join(ROOT, "content", "franchises",
                           args.franchise or "*", "works.yaml")
    for wpath in sorted(glob.glob(pattern)):
        with open(wpath, encoding="utf-8") as f:
            works = yaml.safe_load(f) or []
        enrichments = {}
        for w in works:
            if (w.get("externalIds") or {}).get("openLibrary"):
                continue  # additive: never overwrite
            if args.limit and processed >= args.limit:
                break
            processed += 1
            olid, reason = best_match(w, authors)
            time.sleep(0.5)  # be polite to OpenLibrary
            if olid:
                enrichments[w["id"]] = olid
                enriched.append((w["id"], olid, reason))
            else:
                flagged.append((w["id"], reason))
        if enrichments:
            insert_external_ids(wpath, enrichments)

    lines = ["# Enrichment report", ""]
    lines.append(f"- **Enriched:** {len(enriched)} work(s) with `externalIds.openLibrary`")
    lines.append(f"- **Flagged (no confident match - left untouched for a curator):** {len(flagged)}")
    lines.append("")
    if enriched:
        lines.append("## Enriched")
        lines += [f"- `{wid}` -> `{olid}`  ({reason})" for wid, olid, reason in enriched]
        lines.append("")
    if flagged:
        lines.append("## Flagged for manual review")
        lines += [f"- `{wid}` - {reason}" for wid, reason in flagged]
        lines.append("")
    lines.append("_Additive only: existing IDs and all curator facts were left untouched. "
                 "Nothing is canon until this is reviewed and merged._")
    report = "\n".join(lines)
    with open(os.path.join(ROOT, ".enrichment-report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\nprocessed={processed} enriched={len(enriched)} flagged={len(flagged)}")


if __name__ == "__main__":
    main()
