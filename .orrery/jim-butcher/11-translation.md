---
stage: translation
summary: "pt-PT overlay added: 100% coverage (franchise description, 34 synopses, 3 events, 1 order + debated, author bio + 4 lifeEvents). No Portuguese edition exists for any work; all titles stay English. Spoiler omissions preserved. Rendered and read in both locales."
---

## Coverage: 49/49 slots, all five missing files now complete

Before: `i18n_coverage.py` listed jim-butcher as entirely MISSING (5 files, 49
prose slots: franchise.yaml 1, works.yaml 34, events.yaml 6, orders.yaml 2,
authors/jim-butcher.yaml 9). After: pt-PT is 90/98 files fully covered
catalogue-wide (was 85/98); all five jim-butcher files are now complete and no
other locale/file regressed (the four pre-existing partial files - christie,
jordan, king, pratchett events/authors - are unchanged, not this wing's).

## Titles: every one stays English, and why

Jim Butcher has **no published Portuguese edition anywhere**, in either
region. `lookup.py --markets pt` returned zero candidates. The one
Portuguese-language edition findable at all - "Frente de Tempestade" (Storm
Front), Editora Underworld, 2011 - is Brazilian and the publisher is defunct;
tagging it pt-PT would be the exact mislabelling trap this skill warns
against, so it plays no part here. Bertrand.pt's own author page (fetched via
archive.org; live site blocks fetch.py) lists Jim Butcher exclusively under
English-language imports (Little, Brown; Penguin Publishing Group; Dynamite's
graphic-novel adaptations) with an EN/FR-only language filter - no PT option
at all. `editions.yaml` is untouched (never overlaid per the schema; also
confirmed empty of any pt-PT candidate). Every work `title` in the base file
is left alone; `works.yaml`'s overlay header records this so the next
translator doesn't re-run the same search.

## Invented in-world terms: translated plainly, no coining

With no Portuguese edition to source terminology from, in-world nouns are
translated by sense, matching the brandon-sanderson ("Alomancia" only where a
real PT edition backs it, plain description otherwise) and terry-pratchett
("Universidade Invisível", "Guarda") precedent: Fúria/Fúrias (Codex Alera's
elemental bond - keeps the English pun, since "fury" already does double duty
there), Conselho Branco, Corte Vermelha/Corte Branca, Guardião (Warden),
Torre <nome> (Spire Albion/Olympia/Aurora), Nascidos-Guerreiros
(Warriorborn), eterealista. Personal names, ship names (Predator), race names
(Canim, Marat, Vord) and place-names with no sense to translate (Albion,
Alera, Canea) stay as-is. "Buffy, a Caçadora de Vampiros" and "O Senhor dos
Anéis" use their sourced pt-PT broadcast/publication titles (verified by web
search) since they're real external works being name-dropped, not this
catalogue's own.

## Spoiler boundaries: preserved exactly, not re-derived

White Night's and Backup's synopses mirror the spoiler-audit stage's rewritten
English precisely - neither names Thomas as Harry's half-brother, matching
Blood Rites' own "family revelation" vagueness. I translated the *rewritten*
text, not a fuller version reconstructed from a plot summary elsewhere.
Changes' synopsis keeps "a sua criança" (not "filho"/"filha") to preserve the
same gender-neutral vagueness as the base "his child." Ghost Story's
translation stays as careful as the English it mirrors - it never states that
Harry died at the end of Changes, only that his last case changed him.

## Rendered and read: quoted evidence, not just the coverage script

Built the app against this branch's content locally (temporary submodule
checkout in a sibling `orrery` working copy, reverted after; nothing pushed).
`render-check.mjs --paths /f/jim-butcher --locales en,pt`: both pages 200,
images resolve (bar the one pre-existing OpenLibrary cover gap on The Law,
unrelated to translation), `lang="pt-PT"` confirmed, no base-language chrome
markers on the pt page. Beyond the script, fetched and grepped the rendered
HTML directly and confirmed actual Portuguese lines: the franchise
description ("A obra publicada completa de Jim Butcher..."), a work synopsis
("Harry Dresden é o único feiticeiro profissional de Chicago..."), the order
name and its `debated` text, and - on the author page (which redirects into
the wing page; the bio and lifeEvents render there) - the bio and all four
lifeEvent titles ("Nasce em Independence, Missouri", "Uma aposta na aula de
escrita dá origem a Storm Front", "Uma aposta tola no fórum de escrita da Del
Rey dá origem a Codex Alera").

**One thing flagged, not fixed, not a translation defect:** grepping the raw
HTML for "half-brother" found one hit, inside an embedded JSON payload
carrying the full work object (including the unrendered `note` field) for
client hydration - present identically on the **English** page too (verified:
`grep -c half-brother` on the en page also returns 1), so it predates this
stage and isn't locale-specific. The actual rendered prose on both locales
stays redacted. Surfacing this for whoever owns the app's data-serialization
boundary; not something a content-side translation pass can fix.

## Validation

`python scripts/validate.py --slug jim-butcher`: 0 errors, 0 warnings.
`python scripts/validate.py` (full catalogue): 0 new warnings - the ~79 shown
are all pre-existing, on other wings. `python scripts/i18n_coverage.py`:
90/98, no regression anywhere, jim-butcher fully covered.

Commit: 8758406 on `wing/jim-butcher` (not pushed).
