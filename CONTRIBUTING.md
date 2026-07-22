# Contributing to Orrery content

This repo is the **canon** for [Orrery](https://github.com/rfsbraz/orrery). Canon is content readers trust, so the process is built to be **auditable, reportable, and trackable**.

## The three ways in

- **Report** something wrong or missing → open an issue (Content error / Missing work / Reading order / New franchise). Blank issues are off; the forms ask for what a curator needs, including a **source**.
- **Propose** a change → open a pull request. The PR template is a checklist; unsourced changes are not merged.
- **Research** a franchise from scratch → use the `franchise-research` skill (`.claude/skills/franchise-research/`), which drafts a full bundle for review, or `/author <name>` to run the whole pipeline.
- **Offer art** → open an issue with the `art:human-offer` label. Human art replaces the generated placeholder and carries your credit. See the README.

## The rules that make it auditable

1. **Sources, always.** Every non-obvious claim - a date, an attribution, an order - carries a citation. Unsure? Mark `confidence: low` with a note instead of guessing. Especially for thinly-documented authors.
2. **Stable IDs are permanent.** `id: <franchise-slug>/<work-slug>` is referenced by user data in the app; renaming one orphans that data. Never rename an existing Work ID.
3. **The default order is derived, complete, and chronological.** Every franchise's default reading order is *all published works in publication order*, generated from `works.yaml`. You don't edit it - you keep `works.yaml` complete. Other orders (in-universe, author-recommended, curated) are hand-authored in `orders.yaml`.
4. **Pen names.** Record a pen name on the author (`pseudonyms`) and on each work (`publishedAs`). Pen-name works still belong to the author and appear in the default order. See the schema for when a pen name gets its own franchise.
5. **Global vs franchise events.** Shared world/culture events go in `content/events/global.yaml`; author-life and franchise-specific events stay in the franchise.
6. **Spoilers.** Tag anything that could spoil a book with `spoilerAfter:`.

## On AI assistance

This project is openly AI-assisted, and you are welcome to work the same way. The tools that built it ship in the repo (`.claude/skills/`, `scripts/`), and [`docs/TOOLING.md`](docs/TOOLING.md) explains how to use them and, more usefully, where they fail.

Saying how you produced a change is encouraged, not held against you. What is not acceptable is submitting output nobody read: unsourced claims, invented dates, or a diff you have not checked yourself. The rules above are the whole bar, and they apply identically to hand-written and agent-drafted work.

## Review and merge

A curator reviews for accuracy, sourcing, schema, and stable-ID discipline. **Nothing is canon until a curator merges it.** Merged content is picked up by the app's sync into its database on the next deploy.

Full schema and authoring guidance: [`.claude/skills/franchise-research/SKILL.md`](.claude/skills/franchise-research/SKILL.md).
