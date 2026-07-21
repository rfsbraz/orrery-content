#!/usr/bin/env python3
"""Which stages does this wing actually need?

The trigger table in `.claude/commands/author.md` is the contract; most of its
rows are arithmetic over files that are already on disk, and arithmetic is
cheaper than an agent. On the Valter Hugo Mãe build, `world-events` spent
~188k tokens to correctly conclude it had nothing to add, and then ~210k more
being sent back. This answers the cheap half of that question first.

    python scripts/stage_plan.py <slug>
    python scripts/stage_plan.py <slug> --since origin/main   # prose changed?

It reports RUN / SKIP / JUDGE per stage. **JUDGE means the trigger is genuinely
editorial and this script cannot see it** - not that the stage is optional. A
SKIP is a claim about inputs, never about quality: `completeness-auditor` is
always JUDGE, because "the bibliography looks complete" is exactly the belief
that ships a wing missing eighteen books.
"""
import argparse
import os
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(*parts):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def era_span(period):
    per = str(period or "")
    if "-" not in per:
        return None
    lo, hi = per.split("-", 1)
    hi = hi.strip().lower()
    try:
        return int(lo), (9999 if hi in ("present", "now") else int(hi))
    except ValueError:
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("--since", help="git ref to diff prose against")
    p.add_argument("--locale", default="pt-PT")
    args = p.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    wing = os.path.join("content", "franchises", args.slug)
    exists = os.path.isdir(os.path.join(ROOT, wing))
    works = load(wing, "works.yaml") or []
    eras = load(wing, "eras.yaml") or []
    orders = load(wing, "orders.yaml") or []
    franchise = load(wing, "franchise.yaml") or {}
    editions = load(wing, "editions.yaml") or []
    events = load(wing, "events.yaml") or []
    # global.yaml wraps its list in an `events:` key; the franchise files do not
    _g = load("content", "events", "global.yaml") or []
    globals_ = _g.get("events", []) if isinstance(_g, dict) else _g

    plan = []

    def say(stage, verdict, why):
        plan.append((stage, verdict, why))

    if not exists:
        say("franchise-research", "RUN", "no wing at content/franchises/%s" % args.slug)
        for s in ("completeness-auditor", "press-archaeology", "eras", "reading-orders",
                  "event-resonance", "spoiler-audit", "visual-metadata", "editions",
                  "translation", "wing-audit"):
            say(s, "RUN", "new wing, every layer is empty")
        render(plan)
        return 0
    say("franchise-research", "SKIP", "wing exists and is not being restructured")

    say("completeness-auditor", "JUDGE",
        f"{len(works)} works on file; whether that is all of them is not visible from here")

    years = sorted(w.get("published") for w in works if isinstance(w.get("published"), int))

    # Ask aura_density.py rather than recomputing: it counts franchise events,
    # author lifeEvents AND the globals reaching the wing, and a second, simpler
    # implementation here reported a 10-year dark run where the real one is 4.
    # A duplicated metric that disagrees with the gate is worse than no metric.
    aura_line = ""
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "aura_density.py")],
                             cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
        aura_line = next((l for l in out.splitlines() if l.strip().startswith(args.slug)), "")
    except (OSError, subprocess.TimeoutExpired):
        pass
    if aura_line:
        flagged = "<--" in aura_line
        say("press-archaeology", "RUN" if flagged else "JUDGE",
            "aura_density: " + " ".join(aura_line.replace("<--", "").split())
            + (" (5+ yr dark run)" if flagged else ""))
    else:
        say("press-archaeology", "JUDGE", "aura_density.py gave no line for this wing; read it directly")

    decades = {(y // 10) * 10 for y in years}
    gdec = set()
    for g in globals_:
        d = str(g.get("date", ""))[:4]
        if d.isdigit():
            gdec.add((int(d) // 10) * 10)
    empty = sorted(decades - gdec)
    if empty:
        say("world-events", "RUN", f"publishes in decade(s) with no global event: {empty}")
    else:
        say("world-events", "SKIP",
            "every decade this author publishes in already has a global event; "
            "adding one is an editorial call, not a gap")

    orphans = [w for w in works if not any(
        (sp := era_span(e.get("period"))) and sp[0] <= (w.get("published") or 0) <= sp[1] for e in eras)]
    unsourced = [e for e in eras if e.get("provenance") in (None, "none")]
    if not eras or unsourced:
        say("eras", "RUN", f"{len(eras)} eras, {len(unsourced)} unsourced")
    elif orphans:
        say("eras", "JUDGE",
            f"{len(orphans)} works outside every era - honest if the record names no period, "
            "so this is a judgement, not a gap to tile")
    else:
        say("eras", "SKIP", "every work sits in a sourced era")

    start = (franchise.get("startHere") or {}).get("paths") or []
    if not orders or not start:
        say("reading-orders", "RUN", f"{len(orders)} orders, {len(start)} startHere paths")
    else:
        say("reading-orders", "JUDGE", f"{len(orders)} orders, {len(start)} paths; re-run only if works changed")

    ge = franchise.get("globalEvents")
    if ge is None:
        say("event-resonance", "RUN", "no globalEvents ruling on franchise.yaml")
    else:
        reach = len([g for g in globals_ if g.get("id") not in set(ge.get("exclude") or [])])
        say("event-resonance", "JUDGE",
            f"{len(ge.get('exclude') or [])} excluded, ~{reach} still reaching; re-rule if global.yaml changed")

    if args.since:
        try:
            changed = subprocess.run(
                ["git", "diff", "--name-only", args.since, "--", wing, "content/authors"],
                cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.split()
        except (OSError, subprocess.TimeoutExpired):
            changed = []
        say("spoiler-audit", "RUN" if changed else "SKIP",
            f"{len(changed)} file(s) changed since {args.since}" if changed else
            f"no file changed since {args.since}")
    else:
        say("spoiler-audit", "JUDGE", "pass --since <ref> to answer this mechanically")

    no_cover = [w for w in works if not (w.get("images") or {}).get("cover")]
    ed_ids = {e.get("workId") for e in editions}
    no_ed = [w for w in works if w["id"] not in ed_ids]
    say("visual-metadata", "RUN" if no_cover else "SKIP",
        f"{len(no_cover)}/{len(works)} works have no cover")
    say("editions", "RUN" if no_ed else "SKIP", f"{len(no_ed)}/{len(works)} works have no edition")

    i18n = os.path.join(ROOT, "content", "i18n", args.locale, "franchises", args.slug)
    missing = [n for n in ("works", "eras", "events", "orders", "franchise")
               if os.path.exists(os.path.join(ROOT, wing, f"{n}.yaml"))
               and not os.path.exists(os.path.join(i18n, f"{n}.yaml"))]
    say("translation", "RUN" if missing else "JUDGE",
        f"{args.locale} missing: {', '.join(missing)}" if missing else
        f"{args.locale} files all present; staleness is invisible to coverage, so check the handoffs")

    say("wing-audit", "RUN", "runs on any full build, and on any run touching three or more layers")
    render(plan)
    return 0


def render(plan):
    order = {"RUN": 0, "JUDGE": 1, "SKIP": 2}
    width = max(len(s) for s, _, _ in plan)
    for stage, verdict, why in sorted(plan, key=lambda r: order[r[1]]):
        print(f"  {verdict:<5} {stage:<{width}}  {why}")
    runs = sum(1 for _, v, _ in plan if v == "RUN")
    print(f"\n{runs} stage(s) triggered, {sum(1 for _, v, _ in plan if v == 'JUDGE')} need a human read, "
          f"{sum(1 for _, v, _ in plan if v == 'SKIP')} have no input to work on.")


if __name__ == "__main__":
    sys.exit(main())
