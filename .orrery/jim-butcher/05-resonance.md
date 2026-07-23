---
stage: event-resonance
summary: "Resonance ruling for jim-butcher reviewed and closed out: 1 include (fantasy-paperback-boom-1965), 9 excluded, two factual corrections to existing notes, one missed candidate added."
---

## What I found

The scaffold stage had already done this stage's job: `franchise.yaml` carried a
full `globalEvents` ruling (1 include, 8 exclude, each noted). My job here was
to audit that ruling against `global.yaml` and the actual data, not write it
from scratch.

## Kept (1)

- `fantasy-paperback-boom-1965` - predates him, but created the mass-market
  paperback category his entire career (Roc/Ace, 2000-present) publishes
  inside. Legitimate inheritance, matches the skill's own worked example.

## Excluded (9)

`chain-bookshop-1982`, `online-bookselling-1995`,
`ebook-and-self-publishing-2007`, `sept-11-2001`, `financial-crisis-2008`,
`prestige-fantasy-adaptation-2011`, `covid-19-pandemic-2020`, `booktok-2020`,
`portugal-bailout-2011` - all lived through, none answered on the page.

Added one the scaffold missed: `carnation-revolution-1974` reaches him by date
(he was two) and was never ruled on. Excluded on the same ground as
`portugal-bailout-2011` - American author, no connection to Portuguese
politics.

## Two corrections to existing notes

- `chain-bookshop-1982`'s note said "he was eleven." Checked against his
  1971-10-26 birthdate: on 1982-09-01 he was still ten, two months short of
  his birthday. Fixed.
- `sept-11-2001`'s note said the attacks fell "between Fool Moon and Grave
  Peril." Checked publication dates directly (Wikipedia infoboxes): Fool Moon
  published January 2001, Grave Peril September 1, 2001 - ten days *before*
  the attacks, not after. The true gap is Grave Peril to Summer Knight (2002).
  Corrected the note to that sequence rather than repeat an unverified claim.

Neither of these changed a ruling, only the evidence behind it - but the
stage's job is exactly to be the one that checks, so I didn't let them stand.

## Not added

Checked the remaining pre-birth global events (both world wars, the pulp
magazines, Penguin paperback, armed-services editions, Lady Chatterley) against
the one-sentence test: none produces a specific inheritance claim beyond what
`fantasy-paperback-boom-1965` already covers, so none joins `include`, and they
aren't formal `exclude` entries since they never reach him by the lifetime
gate in the first place.

## Validation

`python scripts/validate.py --slug jim-butcher`: 1 error, the expected
pre-existing `theme.art` gap. Zero new warnings.

## For reading-orders

`franchise.yaml` is clean of any open globalEvents work; no markers left to
clear.
