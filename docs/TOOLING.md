# The tooling: skills, scripts, and how to use them

This repo ships the machinery it was built with. If you want to contribute a
wing, an era scheme, a set of editions or a correction, you are welcome to use
the same agents and scripts we do, and you are equally welcome to ignore all of
it and write YAML by hand. Both routes land in the same place: a pull request a
human reads.

Nothing here is required. The scripts are the fast path, not the toll gate.

## The scripts (no AI needed, run them anywhere)

Plain Python, no API keys, no network except where noted. Run from the repo
root.

| Script | What it answers |
|---|---|
| `validate.py` | Is this content legal? Schema, references, spoilers, assets, contrast, comment policy. **The gate.** Exits non-zero on error. |
| `validate.py --slug <wing>` | The same, with the warning list narrowed to one wing. Checking stays catalogue-wide, because a broken reference crosses wings. |
| `wing_digest.py <wing>` | A whole wing in ~2.4KB instead of ~98KB of YAML. `--missing cover\|edition\|synopsis\|era` answers coverage questions directly. |
| `aura_density.py [wing]` | How much context each work carries, and the longest stretch of publishing years with no events at all. |
| `event_density.py` | The shared `global.yaml` budget. Catalogue-wide by nature, so no slug. |
| `i18n_coverage.py` | Which locale overlays are complete, per file and per field. |
| `asset_audit.py [wing]` | Which images exist and which are missing. Refuses to list jobs for a wing with no visual language. |
| `stage_plan.py <wing>` | Which curation stages a wing actually needs, RUN/SKIP/JUDGE with reasons. |
| `fetch.py URL [URL...]` | Batched, cached HTTP with a browser User-Agent. `--grep`, `--check` for link sweeps, `--save DIR` for binaries. |
| `prepare_asset.py <img> <wing> <id> --chroma` | Turn a generated image into a committable asset: key out the magenta, trim, convert to a capped webp. |
| `issue_sync.py` / `art_intake.py` | The art queue: file issues for missing assets, and wire finished art back into content. |
| `rename_wing.py <old> <new>` | Rename a wing's slug across every id, holding URLs out of the rewrite. |

**Before you open a PR, `python scripts/validate.py` must exit 0.** Check the
exit code on its own line, not through a pipe: `cmd | tail` reports *tail's*
exit code, which is always 0, and has hidden a red validator here more than
once.

## The skills (Claude Code agents)

`.claude/skills/<name>/SKILL.md` are authored agent instructions. Each owns one
curation stage, with its own sourcing rules, refusal conditions and definition
of done. They are readable documents: even if you never run one, they are the
clearest statement of what "good" means for that layer.

The stage list, what each one writes, and which may run in parallel is in
[`.claude/commands/author.md`](../.claude/commands/author.md). Two rules from
it are worth knowing before you run anything:

- **Stages that write the same file must not run in parallel.** Two agents once
  wrote `works.yaml` concurrently and the merge silently kept covers for only
  half the bibliography while looking complete.
- **A stage skipped for lack of inputs is a result; a stage run without its
  inputs is damage.** The discovery stages forbid coining. Run blind, they turn
  a missing source into invented canon that looks exactly like researched canon.

Running the whole pipeline for an author is `/author <name>`. Individual stages
can be run alone.

## What the tools are bad at

Worth stating plainly, because it is the reason for every gate in here.

Language models invent things that sound like facts. Not occasionally, and not
only on obscure subjects. Real examples from this repo's own history, all
caught before merge:

- A tax dispute attributed to Agatha Christie, sourced from an article about
  *Chris* Christie.
- An author "born on the day of the Carnation Revolution" because a lead said
  "born in 1974". He was born in September.
- A death attributed to a novelist that belonged to one of his characters.
- A widely repeated origin story for a novel, traceable to no words the author
  ever said.
- Backlist sales figures cited by a dozen sites, every one of them quoting each
  other and none quoting a source.

They are also confidently wrong about their own work: three stages in one
session reported committing files they never staged.

So the discipline is not optional decoration:

1. **Two independent sources** for anything about a living person's health,
   money, legal trouble or family. One source is not a fact, it is a rumour with
   a URL.
2. **Verify the artefact, not the report.** Open the file, fetch the URL, look
   at the image. A summary is a claim.
3. **Watch a guard fail before trusting it.** Break something deliberately and
   confirm the check fires, then restore it. A check that only ever passes is
   indistinguishable from a check that does nothing.
4. **Prefer an honest gap.** `confidence: low` with a note, or an empty layer
   with a documented reason, beats a plausible invention. Two wings ship with no
   eras at all because the evidence did not support any.

## If you are contributing

Use whatever helps. What we ask is what we ask of ourselves: every non-obvious
claim carries a source, the validator is green, ids are never renamed, and you
have read what you are submitting.

A PR that says "generated with X, I checked the dates against Y and Z, the
prize year I could not confirm so I left it out" is a good PR. Being open about
the method is not a mark against a contribution here.
