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
    def check_event(loc, e, allow_scope=True):
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
            if isbn and (len(isbn) != 13 or not isbn.isdigit()):
                err(loc, f"{eid}: isbn13 '{isbn}' is not 13 digits")
            if ed.get("format") and ed["format"] not in EDITION_FORMATS:
                err(loc, f"{eid}: bad format '{ed.get('format')}'")

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
    print(f"OK - {len(work_ids)} works, {len(author_ids)} authors, all references resolve.")


if __name__ == "__main__":
    main()
