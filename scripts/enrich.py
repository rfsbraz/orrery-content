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
- Writes are driven by the parsed YAML structure but splice only the affected
  lines, so the diff contains ONLY the `externalIds` change - nothing else is
  reformatted or moved. An existing `openLibrary` key (e.g. a `null`
  placeholder) is filled in place, never duplicated; re-running is a no-op.

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


class EnrichWriteError(Exception):
    """The file's layout isn't one the surgical writer can safely edit."""


def _scalar(node):
    return node.value if isinstance(node, yaml.ScalarNode) else None


def _is_null(node):
    return isinstance(node, yaml.ScalarNode) and node.tag == "tag:yaml.org,2002:null"


def _find(mapping, key):
    for k, v in mapping.value:
        if _scalar(k) == key:
            return k, v
    return None, None


def _plan_edit(lines, work, olid):
    """Return (start, end, replacement_lines) for one work, or None if no-op.

    Merges into the parsed structure instead of appending text, so an existing
    `openLibrary` key (e.g. the `null` placeholder) is filled in place and a
    second key is never written.
    """
    ext_key, ext = _find(work, "externalIds")
    if ext is None:
        # Append an externalIds block after the work's last value.
        indent = " " * work.value[0][0].start_mark.column
        last_value = work.value[-1][1]
        last = last_value.end_mark.line - (1 if last_value.end_mark.column == 0 else 0)
        first = work.start_mark.line
        while last > first and lines[last].strip() == "":
            last -= 1
        pos = last + 1
        return pos, pos, [f"{indent}externalIds:\n", f"{indent}  openLibrary: {olid}\n"]

    if _is_null(ext) or (isinstance(ext, yaml.MappingNode) and not ext.value):
        # `externalIds:` / `externalIds: null` / `externalIds: {}` -> block mapping.
        line = ext_key.start_mark.line
        if ext.end_mark.line != line and not _is_null(ext):
            raise EnrichWriteError("multi-line empty externalIds")
        indent = " " * ext_key.start_mark.column
        return line, line + 1, [f"{indent}externalIds:\n", f"{indent}  openLibrary: {olid}\n"]

    if not isinstance(ext, yaml.MappingNode) or ext.flow_style:
        raise EnrichWriteError("externalIds is not a block mapping")

    ol_key, ol = _find(ext, "openLibrary")
    if ol_key is None:
        indent = " " * ext.value[0][0].start_mark.column
        pos = ext.value[0][0].start_mark.line
        return pos, pos, [f"{indent}openLibrary: {olid}\n"]

    if not _is_null(ol) and (_scalar(ol) or "").strip():
        return None  # additive: never overwrite an existing ID

    # Fill the placeholder in place, keeping indentation and any trailing comment.
    line_no = ol_key.start_mark.line
    text = lines[line_no]
    colon = text.index(":", ol_key.end_mark.column)
    if ol.start_mark.line == line_no and ol.end_mark.column > ol.start_mark.column:
        rest = text[ol.end_mark.column:]
    else:  # bare `openLibrary:` with an implicit null
        rest = text[colon + 1:].lstrip(" ")
        rest = (" " + rest) if rest.strip() else "\n"
    return line_no, line_no + 1, [f"{text[:colon]}: {olid}{rest}"]


def insert_external_ids(path, enrichments):
    """Set `externalIds.openLibrary` on each work in `enrichments` ({work_id: olid}).

    Locates each work through the parsed YAML node tree (yaml.compose, so the
    edit is driven by structure, not by regexes over text) and splices only the
    affected lines: comments, ordering and formatting elsewhere are untouched.
    An existing `openLibrary` key is filled in place; a non-empty value is never
    overwritten. Idempotent. The result is re-parsed with the validator's
    duplicate-key-rejecting loader before writing; on any surprise the file is
    left unchanged and the affected works are returned for flagging.
    """
    with open(path, encoding="utf-8") as f:
        original = f.read()
    lines = original.splitlines(keepends=True)
    root = yaml.compose(original)
    if not isinstance(root, yaml.SequenceNode):
        raise EnrichWriteError(f"{path}: expected a list of works")

    edits, failed = [], {}
    for work in root.value:
        if not isinstance(work, yaml.MappingNode):
            continue
        _, id_node = _find(work, "id")
        wid = _scalar(id_node) if id_node is not None else None
        if wid not in enrichments:
            continue
        try:
            edit = _plan_edit(lines, work, enrichments[wid])
        except EnrichWriteError as e:
            failed[wid] = str(e)
            continue
        if edit:
            edits.append(edit)

    for start, end, repl in sorted(edits, reverse=True):
        lines[start:end] = repl
    result = "".join(lines)

    # Never write a file the app (or validate.py) would reject.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from validate import StrictLoader  # noqa: E402
    works = yaml.load(result, Loader=StrictLoader) or []
    by_id = {w.get("id"): w for w in works if isinstance(w, dict)}
    for wid, olid in enrichments.items():
        if wid in failed:
            continue
        got = ((by_id.get(wid) or {}).get("externalIds") or {}).get("openLibrary")
        if got is None:
            raise EnrichWriteError(f"{path}: {wid} did not receive openLibrary")

    if result != original:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(result)
    return failed


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
            try:
                failed = insert_external_ids(wpath, enrichments)
            except (EnrichWriteError, yaml.YAMLError) as e:
                failed = {wid: f"write skipped: {e}" for wid in enrichments}
            for wid, why in failed.items():
                enriched[:] = [e for e in enriched if e[0] != wid]
                flagged.append((wid, f"could not write safely ({why})"))

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
