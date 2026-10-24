# Contributing to Orrery content

This repo is the **canon** for [Orrery](https://github.com/rfsbraz/orrery). Canon is content readers trust, so the process is built to be **auditable, reportable, and trackable**.

## The three ways in

- **Report** something wrong or missing → open an issue (Content error / Missing work / Reading order / New franchise). Blank issues are off; the forms ask for what a curator needs, including a **source**.
- **Propose** a change → open a pull request. The PR template asks for sources; unsourced changes are not merged.
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

Say how you produced a change in the AI use section of the PR template. It is encouraged, not held against you. What is not acceptable is submitting output nobody read: unsourced claims, invented dates, or a diff you have not checked yourself. The rules above are the whole bar, and they apply identically to hand-written and agent-drafted work.

## Low-effort and automated PRs

Orrery is maintained in my spare time, and every PR takes real time to review. I'm happy to get contributions from people who read with Orrery and want the canon to be better.

I will close, without review, PRs that look like contribution farming: accounts opening many PRs across unrelated projects, or changes made mainly to collect contributions rather than to fix something you ran into. This applies even when the change itself is correct.

The easiest way to get a PR merged is to start with an issue, agree on the approach there, and then open the PR.

## Review and merge

A curator reviews for accuracy, sourcing, schema, and stable-ID discipline. **Nothing is canon until a curator merges it.** Merged content is picked up by the app's sync into its database on the next deploy.

Full schema and authoring guidance: [`.claude/skills/franchise-research/SKILL.md`](.claude/skills/franchise-research/SKILL.md).

## Conduct and security

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report security problems as described in [SECURITY.md](SECURITY.md), not in a public issue.
