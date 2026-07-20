#!/usr/bin/env python3
"""Validate Orrery canon content.

Checks structure, stable-ID discipline, and that every reference resolves -
authorIds/withAuthorIds, order work IDs, spoiler boundaries, and inline
[[type:id|text]] links in prose. Exit non-zero on any error so CI blocks the PR.

Usage: python scripts/validate.py
"""
import glob
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS = []
INLINE_REF = re.compile(r"\[\[(?P<type>work|author|franchise|character):(?P<id>[^\]|]+)(?:\|[^\]]*)?\]\]")
ORDER_TYPES = {"chronological-inuniverse", "author-recommended", "curated", "community", "official-publication"}
IMPACTS = {"low", "med", "high"}
SCOPES = {"author-life", "world", "culture", "industry"}
FEATURE_KEYS = {"river", "orderDiff", "wizard", "connections", "companion", "hall", "editions"}
FEATURE_VALUES = {"auto", "on", "off", True, False}
FIT_EXPERIENCE = {"new", "returning", "completionist"}
FIT_COMMITMENT = {"taste", "arc", "complete"}
EDITION_FORMATS = {"hardcover", "paperback", "ebook", "audiobook"}
# BCP-47-ish: "pt", "pt-PT", "en-GB". Region matters for books (pt-PT vs pt-BR).
LANG_RE = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
ACHIEVEMENT_TIERS = {"bronze", "silver", "gold"}
ACHIEVEMENT_CATEGORIES = {"completion", "streak", "context", "social", "discovery", "curation"}
# criteria kind -> required fields (the app implements one evaluator per kind)
CRITERIA_KINDS = {
    "read_count": {"count"},
    "franchise_complete": {"franchiseId"},
    "order_complete": {"orderId"},
    "punctual_read": {"withinYears"},
    "era_reader": {"franchiseId", "eraId", "count"},
}


IMAGE_FIELDS = {"portrait", "header", "cover"}


def check_images(loc, entity_id, images):
    """Images are URLs (never committed binaries) and must carry a credit."""
    if not images:
        return
    if not isinstance(images, dict):
        err(loc, f"{entity_id}: images must be a mapping")
        return
    for key, value in images.items():
        base = key.replace("Credit", "").replace("Source", "")
        if base not in IMAGE_FIELDS:
            err(loc, f"{entity_id}: unknown image field '{key}' (known: {sorted(IMAGE_FIELDS)})")
            continue
        if key == base:
            if not str(value).startswith("http"):
                err(loc, f"{entity_id}: image '{key}' must be a URL (never commit binaries)")
            # Rights discipline: an image without a credit cannot be published.
            if not images.get(base + "Credit"):
                err(loc, f"{entity_id}: image '{key}' has no '{base}Credit'")


def valid_isbn13(isbn):
    """ISBN-13 check digit (EAN-13): weights 1,3,1,3... over the first 12."""
    digits = [int(c) for c in isbn]
    total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (10 - (total % 10)) % 10 == digits[12]


def err(where, msg):
    ERRORS.append(f"{where}: {msg}")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        err(path, f"YAML parse error: {e}")
        return None


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def main():
    # --- authors (global registry) ---
    author_ids = set()
    for path in glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml")):
        a = load(path)
        if not a:
            continue
        if not a.get("id"):
            err(rel(path), "author missing id")
        else:
            author_ids.add(a["id"])
        check_images(rel(path), a.get("id", "?"), a.get("images"))

    # --- works (per franchise) ---
    work_ids = set()
    franchise_dirs = glob.glob(os.path.join(ROOT, "content", "franchises", "*"))
    franchise_slugs = {os.path.basename(d) for d in franchise_dirs if os.path.isdir(d)}
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        works = load(os.path.join(fdir, "works.yaml")) or []
        seen = set()
        for w in works:
            wid = w.get("id", "")
            loc = f"{fslug}/works.yaml"
            if not wid:
                err(loc, "work missing id")
                continue
            if not wid.startswith(fslug + "/"):
                err(loc, f"work id '{wid}' must start with '{fslug}/'")
            if wid in seen:
                err(loc, f"duplicate work id '{wid}'")
            seen.add(wid)
            work_ids.add(wid)
            for aid in w.get("authorIds", []):
                if aid not in author_ids:
                    err(loc, f"{wid}: unknown authorId '{aid}'")
            for aid in w.get("withAuthorIds", []):
                if aid not in author_ids:
                    err(loc, f"{wid}: unknown withAuthorId '{aid}'")
            if w.get("canonTier") not in {"core", "extended", "apocrypha"}:
                err(loc, f"{wid}: bad canonTier '{w.get('canonTier')}'")
            check_images(loc, wid, w.get("images"))

    # --- work connections (second pass: all work ids known) ---
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        for w in load(os.path.join(fdir, "works.yaml")) or []:
            wid = w.get("id", "?")
            for cid in w.get("connections", []) or []:
                if cid not in work_ids:
                    err(f"{fslug}/works.yaml", f"{wid}: connection references unknown work '{cid}'")
                if cid == wid:
                    err(f"{fslug}/works.yaml", f"{wid}: work connects to itself")

    # --- franchise.yaml: authorIds, features, startHere ---
    order_ids_by_franchise = {}
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        opath = os.path.join(fdir, "orders.yaml")
        order_ids_by_franchise[fslug] = {
            o.get("id") for o in (load(opath) or []) if o.get("id")
        } if os.path.exists(opath) else set()

    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        loc = f"{fslug}/franchise.yaml"
        fr = load(os.path.join(fdir, "franchise.yaml")) or {}
        for aid in fr.get("authorIds", []):
            if aid not in author_ids:
                err(loc, f"unknown authorId '{aid}'")
        check_images(loc, fslug, fr.get("images"))
        for k, v in (fr.get("features") or {}).items():
            if k not in FEATURE_KEYS:
                err(loc, f"unknown feature key '{k}' (known: {sorted(FEATURE_KEYS)})")
            elif v not in FEATURE_VALUES:
                err(loc, f"feature '{k}' has bad value '{v}' (auto|on|off)")
        sh = fr.get("startHere")
        if sh is not None:
            paths = sh.get("paths") or []
            if not paths:
                err(loc, "startHere present but has no paths")
            for p in paths:
                pid = p.get("id", "?")
                has_works = bool(p.get("workIds"))
                has_order = bool(p.get("orderId"))
                if has_works == has_order:
                    err(loc, f"startHere path '{pid}': needs exactly one of workIds or orderId")
                for wid in p.get("workIds") or []:
                    if wid not in work_ids:
                        err(loc, f"startHere path '{pid}': unknown work '{wid}'")
                oid = p.get("orderId")
                if oid and oid != "default" and oid not in order_ids_by_franchise.get(fslug, set()):
                    err(loc, f"startHere path '{pid}': unknown orderId '{oid}' (use 'default' for the derived order)")
                fit = p.get("fit") or {}
                for tag in fit.get("experience") or []:
                    if tag not in FIT_EXPERIENCE:
                        err(loc, f"startHere path '{pid}': bad experience tag '{tag}'")
                for tag in fit.get("commitment") or []:
                    if tag not in FIT_COMMITMENT:
                        err(loc, f"startHere path '{pid}': bad commitment tag '{tag}'")

    # --- orders ---
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        opath = os.path.join(fdir, "orders.yaml")
        if not os.path.exists(opath):
            continue
        for o in load(opath) or []:
            loc = f"{fslug}/orders.yaml"
            oid = o.get("id", "?")
            if o.get("type") not in ORDER_TYPES:
                err(loc, f"{oid}: bad order type '{o.get('type')}'")
            for wid in o.get("orderedWorkIds", []):
                if wid not in work_ids:
                    err(loc, f"{oid}: order references unknown work '{wid}'")

    # --- events: franchise, author lifeEvents, global ---
    event_ids = set()

    def check_event(loc, e, allow_scope=True):
        if e.get("id"):
            event_ids.add(e["id"])
        if e.get("impact") not in IMPACTS:
            err(loc, f"{e.get('id','?')}: bad impact '{e.get('impact')}'")
        if allow_scope and e.get("scope") and e["scope"] not in SCOPES:
            err(loc, f"{e.get('id','?')}: bad scope '{e.get('scope')}'")
        sa = e.get("spoilerAfter")
        if sa and sa not in work_ids:
            err(loc, f"{e.get('id','?')}: spoilerAfter '{sa}' is not a known work")

    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        epath = os.path.join(fdir, "events.yaml")
        if os.path.exists(epath):
            for e in load(epath) or []:
                check_event(f"{fslug}/events.yaml", e)
    for path in glob.glob(os.path.join(ROOT, "content", "authors", "*.yaml")):
        a = load(path) or {}
        for e in a.get("lifeEvents", []):
            check_event(rel(path), e, allow_scope=False)
    gpath = os.path.join(ROOT, "content", "events", "global.yaml")
    if os.path.exists(gpath):
        g = load(gpath) or {}
        for e in g.get("events", []):
            check_event("events/global.yaml", e)
            if e.get("reach") != "global":
                err("events/global.yaml", f"{e.get('id','?')}: global events must have reach: global")

    # --- characters ---
    character_ids = set()
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        cpath = os.path.join(fdir, "characters.yaml")
        if not os.path.exists(cpath):
            continue
        seen = set()
        for c in load(cpath) or []:
            loc = f"{fslug}/characters.yaml"
            cid = c.get("id", "")
            if not cid:
                err(loc, "character missing id")
                continue
            if not cid.startswith(fslug + "/"):
                err(loc, f"character id '{cid}' must start with '{fslug}/'")
            if cid in seen:
                err(loc, f"duplicate character id '{cid}'")
            seen.add(cid)
            character_ids.add(cid)
            if not c.get("name"):
                err(loc, f"{cid}: character missing name")
            for ap in c.get("appearsIn", []) or []:
                wid = ap.get("workId")
                if wid not in work_ids:
                    err(loc, f"{cid}: appearsIn references unknown work '{wid}'")
                sa = ap.get("spoilerAfter")
                if sa and sa not in work_ids:
                    err(loc, f"{cid}: appearance spoilerAfter '{sa}' is not a known work")

    # --- editions ---
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        epath = os.path.join(fdir, "editions.yaml")
        if not os.path.exists(epath):
            continue
        seen = set()
        for ed in load(epath) or []:
            loc = f"{fslug}/editions.yaml"
            eid = ed.get("id", "")
            if not eid:
                err(loc, "edition missing id")
                continue
            if eid in seen:
                err(loc, f"duplicate edition id '{eid}'")
            seen.add(eid)
            if ed.get("workId") not in work_ids:
                err(loc, f"{eid}: unknown workId '{ed.get('workId')}'")
            isbn = str(ed.get("isbn13") or "")
            if isbn:
                if len(isbn) != 13 or not isbn.isdigit():
                    err(loc, f"{eid}: isbn13 '{isbn}' is not 13 digits")
                elif not valid_isbn13(isbn):
                    # A bad check digit means the number is not a real ISBN -
                    # a transcription slip or an invented one. Either way it
                    # would send a reader to the wrong book (or nowhere).
                    err(loc, f"{eid}: isbn13 '{isbn}' fails its check digit - not a real ISBN")
            if ed.get("format") and ed["format"] not in EDITION_FORMATS:
                err(loc, f"{eid}: bad format '{ed.get('format')}'")
            lang = ed.get("language")
            if lang and not LANG_RE.match(str(lang)):
                err(loc, f"{eid}: bad language '{lang}' (use 'pt-PT', 'en', ...)")
            # A translated title without a language is unusable (we cannot know
            # which locale it belongs to); an edition in a non-original language
            # without a title is a missed opportunity but not an error.
            if ed.get("title") and not lang:
                err(loc, f"{eid}: has a published title but no language")

    # --- achievements (global + per franchise) ---
    era_ids_by_franchise = {}
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        epath = os.path.join(fdir, "eras.yaml")
        era_ids_by_franchise[fslug] = {
            e.get("id") for e in (load(epath) or []) if e.get("id")
        } if os.path.exists(epath) else set()

    all_order_ids = {oid for ids in order_ids_by_franchise.values() for oid in ids}
    all_era_ids = {eid for ids in era_ids_by_franchise.values() for eid in ids}
    achievement_ids = set()

    def check_achievements(loc, items, franchise_slug=None):
        for a in items or []:
            aid = a.get("id", "")
            if not aid:
                err(loc, "achievement missing id")
                continue
            if franchise_slug and not aid.startswith(franchise_slug + "/"):
                err(loc, f"achievement id '{aid}' must start with '{franchise_slug}/'")
            if aid in achievement_ids:
                err(loc, f"duplicate achievement id '{aid}'")
            achievement_ids.add(aid)
            for field in ("name", "description", "icon"):
                if not a.get(field):
                    err(loc, f"{aid}: achievement missing {field}")
            if a.get("tier") not in ACHIEVEMENT_TIERS:
                err(loc, f"{aid}: bad tier '{a.get('tier')}'")
            if a.get("category") not in ACHIEVEMENT_CATEGORIES:
                err(loc, f"{aid}: bad category '{a.get('category')}'")

            c = a.get("criteria") or {}
            kind = c.get("kind")
            if kind not in CRITERIA_KINDS:
                err(loc, f"{aid}: unknown criteria kind '{kind}' (app implements: {sorted(CRITERIA_KINDS)})")
                continue
            for field in CRITERIA_KINDS[kind]:
                if c.get(field) is None:
                    err(loc, f"{aid}: criteria '{kind}' requires '{field}'")
            # every reference in the criteria must resolve
            fid = c.get("franchiseId")
            if fid and fid not in franchise_slugs:
                err(loc, f"{aid}: criteria references unknown franchise '{fid}'")
            oid = c.get("orderId")
            if oid and oid not in all_order_ids:
                err(loc, f"{aid}: criteria references unknown order '{oid}'")
            eid = c.get("eraId")
            if eid and eid not in era_ids_by_franchise.get(fid or "", set()):
                err(loc, f"{aid}: criteria references unknown era '{eid}' for franchise '{fid}'")

    gapath = os.path.join(ROOT, "content", "achievements.yaml")
    if os.path.exists(gapath):
        check_achievements("achievements.yaml", load(gapath) or [])
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        apath = os.path.join(fdir, "achievements.yaml")
        if os.path.exists(apath):
            check_achievements(f"{fslug}/achievements.yaml", load(apath) or [], fslug)

    # --- translation overlays: every id must resolve, no forbidden fields ---
    # Never translatable anywhere: identifiers, author/order names, edition keys.
    FORBIDDEN = {"id", "sources", "isbn13", "language", "workId", "name"}
    # A WORK title is edition data - it must be a real published title from
    # editions.yaml, never an invention - so it stays forbidden. Era and event
    # titles are curated prose we wrote ourselves and ARE translatable.
    TITLE_ALLOWED_IN = {"eras.yaml", "events.yaml"}
    for lpath in glob.glob(os.path.join(ROOT, "content", "i18n", "*")):
        if not os.path.isdir(lpath):
            continue
        locale = os.path.basename(lpath)
        for path in glob.glob(os.path.join(lpath, "**", "*.yaml"), recursive=True):
            loc = rel(path)
            data = load(path)
            if data is None:
                continue
            entries = data if isinstance(data, list) else [data]
            for e in entries:
                if not isinstance(e, dict):
                    err(loc, "translation entry must be a mapping")
                    continue
                eid = e.get("id")
                if not eid:
                    err(loc, "translation entry missing id")
                    continue
                known = (
                    eid in work_ids
                    or eid in author_ids
                    or eid in franchise_slugs
                    or eid in all_order_ids
                    or eid in character_ids
                    or eid in event_ids
                    or eid in all_era_ids
                )
                if not known:
                    err(loc, f"translation for unknown id '{eid}' ({locale})")
                title_ok = os.path.basename(path) in TITLE_ALLOWED_IN
                for field in e:
                    if field == "id":
                        continue
                    if field in FORBIDDEN or (field == "title" and not title_ok):
                        err(loc, f"{eid}: '{field}' must never be translated")

    # --- inline [[type:id|text]] references resolve everywhere ---
    for path in glob.glob(os.path.join(ROOT, "content", "**", "*.yaml"), recursive=True):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for m in INLINE_REF.finditer(text):
            t, rid = m.group("type"), m.group("id").strip()
            if t == "work" and rid not in work_ids:
                err(rel(path), f"inline [[work:{rid}]] does not resolve")
            elif t == "author" and rid not in author_ids:
                err(rel(path), f"inline [[author:{rid}]] does not resolve")
            elif t == "character" and rid not in character_ids:
                err(rel(path), f"inline [[character:{rid}]] does not resolve")
            elif t == "franchise" and rid not in franchise_slugs:
                err(rel(path), f"inline [[franchise:{rid}]] does not resolve")

    if ERRORS:
        print(f"FAILED - {len(ERRORS)} error(s):\n")
        for e in ERRORS:
            print("  -", e)
        sys.exit(1)
    print(f"OK - {len(work_ids)} works, {len(author_ids)} authors, {len(character_ids)} characters, {len(achievement_ids)} achievements, all references resolve.")


if __name__ == "__main__":
    main()
