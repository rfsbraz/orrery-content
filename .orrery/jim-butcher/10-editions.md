---
stage: editions
summary: "editions.yaml created: 33/34 works, English only, sourced via lookup.py + OpenLibrary/ISFDB cross-checks"
---

## Coverage: 33 of 34 works, English (en) only

No pt-PT translation exists for this wing, so every entry is the original-
language edition, recorded because Orrery uses editions as the buy-button
layer even for an English original. One edition per work: Roc for the
Dresden Files through Skin Game, Ace for Codex Alera and (as "Penguin
Publishing Group"/Ace) Peace Talks onward and the Cinder Spires, Orbit UK
wherever no clean US ISBN surfaced (Summer Knight, Death Masks, Blood Rites,
Small Favor, Skin Game, Peace Talks - a different but equally real English
printing, not a fallback), and Subterranean Press/Podium/Pocket Star for the
specialty and licensed items.

## Source: lookup.py, not hand-fetching

`python scripts/metadata/lookup.py jim-butcher --author "Jim Butcher"
--markets en --json` returned 194 candidates across 57 title clusters in one
call. Every chosen ISBN was then opened individually at OpenLibrary (batched,
never one-by-one) to confirm its `works` key against the correct work id and,
where available, its `physical_format`. Storm Front's ISBN is additionally
cross-checked against ISFDB.

Three traps the candidate table held: Del Rey's two "Jim Butcher's the
Dresden files" records are graphic-novel adaptations (confirmed via their own
`by_statement` naming an adaptation/penciller/inker), not prose editions;
"Wizard for Hire" and "Wizard Under Fire" (SFBC) are two-novel omnibus
bind-ups (754 pages gave the second one away); and Storm Front/Fool
Moon/Summer Knight each carry several Buzzy Multimedia audio-CD ISBNs,
excluded as non-print.

## Deliberate absence: Warriorborn

No entry, and none is possible: jim-butcher.com's own announcement states it
"was released September 19, 2023 as an ebook and an audiobook," and neither
OpenLibrary nor ISFDB holds an ISBN for either format. Matches works.yaml's
existing note.

## Weaker spots, flagged rather than hidden

- **The Law**: the only ISBN found (9781039414808, OpenLibrary) is
  single-sourced and its publisher field is blank there; recorded as
  Subterranean Press on the strength of jim-butcher.com's own statement that
  a Subterranean collector's edition exists (ISFDB has no ISBN for either of
  its two listed editions). A human with a browser at Subterranean Press's
  own (JS-rendered, unfetchable) site could confirm this directly.
- **Small Favor, Skin Game, Brief Cases (2018)**: each has a US OpenLibrary
  record with a blank or self-contradictory publisher field; the Orbit UK or
  alternate-year US edition was used instead rather than asserting a
  publisher name OpenLibrary itself doesn't state.
- Several later entries (Peace Talks' OL record also carries a
  clearly-erroneous "2015" duplicate ISBN row) are noted in-file so the next
  auditor doesn't re-litigate them.

## Verification

`python scripts/validate.py --slug jim-butcher`: 0 errors (2 comment-wording
warnings raised and fixed during the pass). `python scripts/metadata/lookup.py
--verify-isbns jim-butcher`: **33 editions, 0 suspect**. No coverUrl anywhere,
no `title` field anywhere (English original throughout).

## For translation

If pt-PT work starts on this wing later, none of this file's picks bear on
it - Portuguese editions are separately sourced and this file's US/UK split
doesn't generalise to any other language.
