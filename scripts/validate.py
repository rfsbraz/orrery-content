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

    # --- franchise.yaml authorIds ---
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        fr = load(os.path.join(fdir, "franchise.yaml")) or {}
        for aid in fr.get("authorIds", []):
            if aid not in author_ids:
                err(f"{fslug}/franchise.yaml", f"unknown authorId '{aid}'")

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
            # franchise/character refs are not yet a registry - skipped

    if ERRORS:
        print(f"FAILED - {len(ERRORS)} error(s):\n")
        for e in ERRORS:
            print("  -", e)
        sys.exit(1)
    print(f"OK - {len(work_ids)} works, {len(author_ids)} authors, all references resolve.")


if __name__ == "__main__":
    main()
