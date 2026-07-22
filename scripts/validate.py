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
# Non-fatal: things a curator should look at but which are legitimately a
# judgement call (a posthumous or companion work may sit outside every era).
WARNINGS = []
# Set by --slug. Narrows the warning REPORT to one wing; never narrows checking.
SCOPE = None
INLINE_REF = re.compile(r"\[\[(?P<type>work|author|franchise|character):(?P<id>[^\]|]+)(?:\|[^\]]*)?\]\]")
ORDER_TYPES = {"chronological-inuniverse", "author-recommended", "curated", "community", "official-publication"}
IMPACTS = {"low", "med", "high"}
# Theme values the APP actually implements. A wing may name anything it likes
# here and the app will silently substitute its default - so a wing can ship a
# look nobody chose and every check stays green. Keep in sync with the orrery
# app's `lib/theme.ts` (DISPLAY_FACES and SignatureKind).
DISPLAY_FACES = {"fraunces", "spectral", "sourceSerif"}
SIGNATURES = {"beam", "thread", "rule", "none"}
SCOPES = {"author-life", "world", "culture", "industry"}
FEATURE_KEYS = {"river", "wizard", "connections", "companion", "hall", "editions"}
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


# `sketch` is the generated-art slot on eras, events and life events. It is
# credited like any other image, and its credit must say it was generated: a
# reader who cannot tell a sourced photograph from an illustration we made has
# been misled by omission, on a site whose whole claim is that the facts are
# checked.
IMAGE_FIELDS = {"portrait", "header", "cover", "sketch"}
GENERATED = re.compile(r"\bgenerated\b|\billustration for\b", re.I)


ASSET_MAX_BYTES = 320_000
ASSET_EXT = {".webp"}


def check_asset(loc, entity_id, value):
    """A sketch is a repo-relative path under assets/, and it must be there.

    Checking the file exists is a real guard, unlike checking a URL's syntax: a
    dead link validates green forever, a missing file fails the moment someone
    mistypes it or forgets to commit the binary alongside the YAML.

    webp only, and capped: a wing carries dozens of these and a repo full of
    multi-megabyte PNGs becomes a clone everybody dreads. gpt-image-1 returns
    PNG, so converting is part of filing the asset, not an optimisation to do
    later.
    """
    if value.startswith("http"):
        err(loc, f"{entity_id}: sketch is ours - commit it under assets/ rather "
                 f"than linking to '{value[:60]}'")
        return
    if value.startswith("/") or ".." in value:
        err(loc, f"{entity_id}: sketch path must be repo-relative, got '{value}'")
        return
    if not value.startswith("assets/"):
        err(loc, f"{entity_id}: sketch must live under assets/, got '{value}'")
        return
    ext = os.path.splitext(value)[1].lower()
    if ext not in ASSET_EXT:
        err(loc, f"{entity_id}: sketch must be {' or '.join(sorted(ASSET_EXT))}, got '{ext or 'no extension'}'")
        return
    path = os.path.join(ROOT, value)
    if not os.path.exists(path):
        err(loc, f"{entity_id}: sketch '{value}' is not in the repo - commit the file with the entry")
        return
    size = os.path.getsize(path)
    if size > ASSET_MAX_BYTES:
        err(loc, f"{entity_id}: sketch '{value}' is {size // 1000}KB, over the "
                 f"{ASSET_MAX_BYTES // 1000}KB cap - re-encode it")


def check_images(loc, entity_id, images):
    """Third-party images are URLs; our own sketches are files in this repo.

    The "never commit binaries" rule was written for LICENSED images - a
    Wikimedia portrait or an OpenLibrary cover belongs to someone else, so we
    link to the source and keep the credit honest. A generated sketch is ours,
    small, and meaningless apart from the entry that references it, so it lives
    in `assets/` and ships with the content. A committed file also cannot rot,
    which a link can, silently.
    """
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
            if base == "sketch":
                check_asset(loc, entity_id, str(value))
            elif not str(value).startswith("http"):
                err(loc, f"{entity_id}: image '{key}' must be a URL (never commit binaries)")
            # Rights discipline: an image without a credit cannot be published.
            credit = images.get(base + "Credit")
            if not credit:
                err(loc, f"{entity_id}: image '{key}' has no '{base}Credit'")
            elif base == "sketch" and not GENERATED.search(str(credit)):
                err(
                    loc,
                    f"{entity_id}: sketchCredit must say the image was generated "
                    f"(got '{credit}') - a reader has to be able to tell our "
                    f"illustration from a sourced photograph",
                )


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) != 6:
        return None
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    if la is None or lb is None:
        return None
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def valid_isbn13(isbn):
    """ISBN-13 check digit (EAN-13): weights 1,3,1,3... over the first 12."""
    digits = [int(c) for c in isbn]
    total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (10 - (total % 10)) % 10 == digits[12]


def err(where, msg):
    ERRORS.append(f"{where}: {msg}")


def warn(where, msg):
    WARNINGS.append(f"{where}: {msg}")


def era_span(period):
    """[start, end] for an era period ("1974-1978", "2020-present", "1980s").

    Mirrors the app's eraSpan so this guard sees what the River sees.
    """
    raw = str(period or "")
    years = re.findall(r"\d{4}", raw)
    if not years:
        return None
    start = int(years[0])
    if re.search(r"present|now", raw, re.I):
        return (start, 9999)
    if len(years) > 1:
        return (start, int(years[-1]))
    if re.search(r"\d{4}s", raw):
        return (start, start + 9)
    return (start, start)


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys.

    Subclasses SafeLoader deliberately: `yaml.load(f, StrictLoader)` is exactly
    as safe as `yaml.safe_load(f)` (which is itself `load(stream, SafeLoader)`)
    because no constructor for arbitrary Python types is registered. Do not
    swap the base class for `yaml.Loader`.

    PyYAML silently keeps the LAST value for a repeated key, so a file with two
    `note:` blocks loads clean here and every check goes green - while the app's
    JS parser (`yaml`) is strict, throws, and takes the whole page down. That
    exact split shipped once: two stages each appended a `note:` to the same
    work, Python was happy, and the app could not parse the wing at all.

    The validator must fail wherever the real consumer fails.
    """


def _no_duplicate_keys(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None,
                None,
                f"duplicate key '{key}' (the app's parser rejects this file)",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys
)


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, StrictLoader)
    except Exception as e:
        err(path, f"YAML parse error: {e}")
        return None


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def main():
    # --- pipeline handoffs (.orrery/, branch-local, absent on main) ----------
    # Stage handoffs are how one curation agent tells the next what it did;
    # nothing else validates them, because they live outside content/. A
    # handoff that does not parse is worse than a missing one: the next stage
    # is told to read it, silently gets nothing, and its gap looks like
    # completion. This directory is deleted before the final merge, so on main
    # this check simply finds nothing.
    # They are also capped. A handoff is read by EVERY later stage, so its cost
    # is its length times the stages left to run - the last stage of the Valter
    # Hugo Mãe build read nine of them. Long-form reasoning belongs in the run
    # report, which is read once, by a human.
    HANDOFF_WORDS = 700
    for path in glob.glob(os.path.join(ROOT, ".orrery", "**", "*.yaml"), recursive=True):
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
            yaml.safe_load(raw)
        except Exception as e:
            err(rel(path), f"handoff does not parse: {e}")
            continue
        words = len(raw.split())
        if words > HANDOFF_WORDS:
            warn(
                rel(path),
                f"handoff is {words} words (soft cap {HANDOFF_WORDS}); every later "
                f"stage pays to read it - move the reasoning to the run report and "
                f"keep the summary, what changed, and what the next stage must know",
            )

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
            # `published` must be a bare year integer. A full date (1974-03-26)
            # parses as a string in the app, and every consumer of this field is
            # year arithmetic - River layers, era spans, decade rules, era-reader
            # achievements. A string loses all of those comparisons silently:
            # the work gets a layer of its own, sits outside every era, and is
            # missing from the achievement that should have counted it. Nothing
            # throws. Day precision has no consumer, so it is simply forbidden.
            pub = w.get("published")
            if isinstance(pub, bool) or not isinstance(pub, int):
                err(
                    loc,
                    f"{wid}: published must be a bare year integer, got "
                    f"{pub!r} - use the year alone (1974, not 1974-03-26)",
                )
            elif not 1000 <= pub <= 2999:
                err(loc, f"{wid}: published '{pub}' is not a 4-digit year")
            # authorRole defaults to "author"; it only needs stating when the
            # author did not write the whole book. A contributor or editor entry
            # must never look like authorship, so the tier has to match.
            role = w.get("authorRole", "author")
            if role not in {"author", "co-author", "contributor", "editor"}:
                err(loc, f"{wid}: bad authorRole '{role}'")
            if role in {"contributor", "editor"} and w.get("canonTier") != "apocrypha":
                err(loc, f"{wid}: authorRole '{role}' must be canonTier apocrypha")
            if w.get("contributionTitle") and role == "author":
                err(loc, f"{wid}: contributionTitle set but authorRole is 'author'")
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
        # Franchise events, author lifeEvents and global events all funnel
        # through here, so one call covers every event kind's `sketch`.
        check_images(loc, e.get("id", "?"), e.get("images"))

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

    # --- theme values the app can honour ------------------------------------
    # `displayFace` and `signature` both fall back silently in the app when it
    # does not implement the named value, so an invented one costs a wing its
    # chosen look without failing anything. Warning rather than error: the fix
    # may legitimately be to implement the value in the app rather than to
    # change the content.
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        tpath = os.path.join(fdir, "theme.yaml")
        if not os.path.exists(tpath):
            continue
        theme = load(tpath) or {}
        face = theme.get("displayFace")
        if face and face not in DISPLAY_FACES:
            warn(
                f"{fslug}/theme.yaml",
                f"displayFace '{face}' is not implemented by the app - it will "
                f"silently render as 'fraunces' (implemented: {sorted(DISPLAY_FACES)})",
            )
        sig = theme.get("signature")
        if sig and sig not in SIGNATURES:
            warn(
                f"{fslug}/theme.yaml",
                f"signature '{sig}' is not implemented by the app - it will "
                f"silently render as 'thread' (implemented: {sorted(SIGNATURES)})",
            )
        # A wing with no `art:` block cannot have a single asset generated for
        # it: `asset_audit.py` refuses to list jobs, because ten drawings made
        # months apart with no shared visual law are ten unrelated pictures.
        # Seven of ten wings sat in exactly this state, which was 156 assets
        # blocked behind a decision nobody had recorded. Error, not warning:
        # the whole point is that it stops the wing rather than annotating it.
        art = theme.get("art") or {}
        if not art:
            err(f"{fslug}/theme.yaml",
                "no `art:` block - the wing has no visual law, so nothing can "
                "be drawn for it (run the visual-language stage)")
        else:
            missing = [k for k in ("motifs", "atmosphere", "lineCharacter",
                                   "backgroundTexture", "accentUse", "avoid")
                       if not art.get(k)]
            if missing:
                err(f"{fslug}/theme.yaml",
                    f"`art:` is missing {', '.join(missing)} - a partial visual "
                    f"law reads as settled and is not")

        # CONCEPT §6 calls the readability floor non-negotiable, and nothing
        # enforced it: a wing shipped `muted` at 4.15:1 on its own surface and
        # every check stayed green, because no script had ever opened a palette.
        # WCAG AA for body text is 4.5:1.
        palette = theme.get("palette") or {}
        for fg, bg, why in (("ink", "bg", "body text"),
                            ("ink", "surface", "text on cards"),
                            ("muted", "surface", "metadata on cards"),
                            ("muted", "bg", "metadata on the page")):
            if palette.get(fg) and palette.get(bg):
                ratio = contrast(palette[fg], palette[bg])
                if ratio is not None and ratio < 4.5:
                    err(
                        f"{fslug}/theme.yaml",
                        f"{fg} {palette[fg]} on {bg} {palette[bg]} is "
                        f"{ratio:.2f}:1, under the 4.5:1 AA floor for {why}",
                    )

    # --- era coverage -------------------------------------------------------
    # Every work should sit under some era: the River renders works against era
    # plates, so an uncovered year leaves the work floating with no context.
    # Re-sourcing an era's boundaries is how this breaks - tightening a span to
    # a defensible range silently orphans whatever fell in the slack. A warning
    # rather than an error, because a posthumous release or a companion volume
    # can legitimately sit outside the creative eras.
    for fdir in franchise_dirs:
        if not os.path.isdir(fdir):
            continue
        fslug = os.path.basename(fdir)
        epath = os.path.join(fdir, "eras.yaml")
        if not os.path.exists(epath):
            continue
        for e in load(epath) or []:
            check_images(f"{fslug}/eras.yaml", e.get("id", "?"), e.get("images"))
        spans = [s for s in (era_span(e.get("period")) for e in (load(epath) or [])) if s]
        if not spans:
            continue
        for w in load(os.path.join(fdir, "works.yaml")) or []:
            year = w.get("published")
            if not isinstance(year, int):
                continue
            if not any(a <= year <= b for a, b in spans):
                warn(
                    f"{fslug}/works.yaml",
                    f"{w.get('id')}: published {year} falls outside every era "
                    f"(covered: {', '.join(f'{a}-{b}' for a, b in sorted(spans))})",
                )

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
    # Never translatable anywhere: identifiers, source URLs, edition facts.
    FORBIDDEN = {"id", "sources", "isbn13", "language", "workId"}
    # `title` is prose almost everywhere it appears - era titles, event titles,
    # nested lifeEvent titles, startHere path titles. The ONE exception is a
    # work/edition title, which is edition data: it must be a real published
    # title from editions.yaml, never an invention, or we send a reader after a
    # book that does not exist.
    TITLE_FORBIDDEN_IN = {"works.yaml", "editions.yaml"}
    # `name` is a proper noun (authors, franchises, characters) EXCEPT on an
    # order, where it is a curated label a reader reads.
    NAME_ALLOWED_IN = {"orders.yaml"}
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
                # Nested id-bearing lists (lifeEvents, startHere.paths) are
                # merged by id, so validate their entries too.
                for ne in e.get("lifeEvents") or []:
                    if isinstance(ne, dict) and not ne.get("id"):
                        err(loc, f"{eid}: lifeEvents entry missing id")
                sh = e.get("startHere")
                if isinstance(sh, dict):
                    for np_ in sh.get("paths") or []:
                        if isinstance(np_, dict) and not np_.get("id"):
                            err(loc, f"{eid}: startHere path missing id")

                base_name = os.path.basename(path)
                for field in e:
                    if field == "id":
                        continue
                    if field in FORBIDDEN:
                        err(loc, f"{eid}: '{field}' must never be translated")
                    elif field == "title" and base_name in TITLE_FORBIDDEN_IN:
                        err(
                            loc,
                            f"{eid}: a work's 'title' is edition data - add a published "
                            "edition instead of translating the title",
                        )
                    elif field == "name" and base_name not in NAME_ALLOWED_IN:
                        err(loc, f"{eid}: 'name' is a proper noun and is not translated here")

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

    # --- spoilerAfter must sit somewhere the app can actually honour it ---
    #
    # The app reads spoilerAfter on events (franchise, global, author lifeEvents)
    # and on character appearances. Nowhere else. A boundary written onto a work,
    # an order, an era or a startHere path is accepted by YAML, reads like
    # protection, and does nothing at all.
    #
    # That is the dangerous case: an agent gates a synopsis, sees a green build,
    # records the spoiler as contained, and ships it in the clear. CI ends up
    # confirming the wrong belief. So a boundary the engine cannot honour is an
    # error, not a harmless extra field. Loud beats silent when the failure mode
    # is a spoiler a reader cannot un-read.
    def scan_unhonoured(loc, node, path="", inside_event=False):
        if isinstance(node, dict):
            here = path.split(".")[-1]
            # Events are dicts carrying `impact`; appearances carry `workId`.
            honours = inside_event or "impact" in node or "workId" in node
            if "spoilerAfter" in node and not honours:
                where = node.get("id") or node.get("slug") or path or "root"
                err(
                    loc,
                    f"{where}: spoilerAfter is not honoured by the app here "
                    f"(only events, author lifeEvents and character appearances "
                    f"support it) - rewrite the prose instead",
                )
            for k, v in node.items():
                child_event = k in {"events", "lifeEvents", "appearsIn"}
                scan_unhonoured(loc, v, f"{path}.{k}" if path else k, child_event)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                scan_unhonoured(loc, v, f"{path}[{i}]", inside_event)

    for path in glob.glob(os.path.join(ROOT, "content", "**", "*.yaml"), recursive=True):
        data = load(path)
        base = os.path.basename(path)
        # Top-level lists in events.yaml / global.yaml are events themselves.
        top_is_event = base in {"events.yaml", "global.yaml", "characters.yaml"}
        scan_unhonoured(rel(path), data, "", top_is_event)

    # --- comment policy (docs/CURATION.md §2) --------------------------------
    # Content YAML is a data source of truth: comments carry sources and DATA
    # decision logs, never pipeline narration or coordination. Process history
    # belongs in PR bodies, handoffs and git. This is a heuristic scan of
    # comment lines for pipeline vocabulary; a hit is a question, not a
    # verdict, hence a warning.
    PROCESS_COMMENT = re.compile(
        # who is doing the work, or who is being addressed
        r"\bcurator\b|\bauditor\b|research agent|curation stage|\bthis (?:stage|agent)\b"
        r"|\bfranchise-research\b|\bcompleteness\b|\bpress-archaeology\b|\bworld-events\b"
        r"|\bevent-resonance\b|\breading-orders\b|\bspoiler-audit\b|\bvisual-metadata\b"
        r"|\bwing-audit\b|\bwhats-new\b|\bopen ?questions?\b|\bforStages\b"
        # when the work happened, or that more of it is owed
        r"|\bpipeline\b|\bhandoff\b|\b(?:first|second|another|dedicated) pass\b"
        r"|\bthis (?:pass|run)\b|\bnever ran\b|\bnot yet (?:a )?(?:finished|complete)\b"
        r"|\bhas since been\b|\bwas (?:first|originally) (?:built|written|drafted)\b"
        r"|\bstill (?:open|needs|remains)\b|\bfor (?:a )?(?:future|later) pass\b"
        r"|search budget|\bstage \d\b|\.claude|skills/|\bTODO\b|\bre-?run\b"
        # self-congratulation about method rather than a statement about the data
        r"|\brather than (?:papered over|guessed|invented|coined)\b"
        r"|\bflagged rather than\b|\bleft (?:to|for) the\b",
        re.IGNORECASE,
    )
    # Comments are not the only place this leaks: `note:` is curator-only prose
    # and collects the same "a curator should decide" addressing. Reader-facing
    # prose is NOT scanned - a Cosmere synopsis legitimately describes librarians
    # "whose curators collect souls as readily as books", and a scan that cannot
    # tell that from coordination would train everyone to ignore it.
    in_note = False
    for path in glob.glob(os.path.join(ROOT, "content", "**", "*.yaml"), recursive=True):
        try:
            with open(path, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    stripped = line.strip()
                    if re.match(r"^-?\s*\w+:", stripped):
                        in_note = bool(re.match(r"^-?\s*note:", stripped))
                    if not stripped.startswith("#") and not in_note:
                        continue
                    m = PROCESS_COMMENT.search(stripped)
                    if m:
                        warn(
                            rel(path),
                            f"line {n}: comment reads as pipeline narration "
                            f"('{m.group(0)}') - content comments carry data "
                            f"decisions and sources only (docs/CURATION.md)",
                        )
        except OSError:
            pass

    if WARNINGS:
        # Checking is always catalogue-wide: a broken reference crosses wings,
        # so scoping the CHECK would hide real breakage. Only the REPORT
        # narrows. A stage building one wing was reading ~78 warnings belonging
        # to eight other wings, which buries its own and invites it to "fix" a
        # wing nobody asked it to touch.
        shown, hidden = WARNINGS, 0
        if SCOPE:
            shown = [w for w in WARNINGS if SCOPE in w]
            hidden = len(WARNINGS) - len(shown)
        if shown:
            print(f"{len(shown)} warning(s) - not blocking, but a curator should look:\n")
            for w in shown:
                print("  ~", w)
            print()
        if hidden:
            print(f"({hidden} warning(s) on other wings hidden by --slug {SCOPE}; "
                  f"run without it to see the whole catalogue)\n")

    if ERRORS:
        print(f"FAILED - {len(ERRORS)} error(s):\n")
        for e in ERRORS:
            print("  -", e)
        sys.exit(1)
    print(f"OK - {len(work_ids)} works, {len(author_ids)} authors, {len(character_ids)} characters, {len(achievement_ids)} achievements, all references resolve.")


if __name__ == "__main__":
    # --slug <wing> reports only that wing's warnings. Errors and the catalogue
    # summary are always global, because correctness is not per-wing.
    if "--slug" in sys.argv:
        i = sys.argv.index("--slug")
        SCOPE = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        del sys.argv[i:i + 2]
    main()
