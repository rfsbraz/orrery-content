---
stage: visual-language
summary: "Wrote the art block on jim-butcher/theme.yaml; validate.py now passes clean, 7 asset jobs unblocked."
---

## Emblem

A battered hand lantern, soot-smudged glass, wick trimmed low, held at the
end of a bare arm so its light claims only a few feet of dark. Grounded in
each series' own documented reason for carried light rather than a fixed
one: Harry's magic reliably fries powered electronics (candles and oil lamps
out of stated necessity, not mood), the Calderon legions' picket-fire, and a
Spire vessel's running lanterns - the last already named in the wing's own
palette rationale, not a fresh claim.

## Motifs

Six, chosen to be carried by all three series without costuming any one:
a hand lantern claiming a small circle of light; rain/dew/frost catching a
single light source; a doorway, gate or ship's rail stood at as a threshold;
worn brass/iron/leather fittings polished by handling; a one-lamp work-table
mid-task; fog or high mist swallowing the middle distance. None names a
wizard, a legion or an airship directly - each motif is legible in a Chicago
alley, a Roman-analog frontier camp, and an airship gondola alike.

## Atmosphere / line / texture / accent

- **Atmosphere**: tense, on-duty vigilance ("the mood of overtime"), not
  gothic dread, comic warmth or epic wonder - ruling out the three genres'
  own defaults explicitly.
- **lineCharacter** (the load-bearing field): hard-edged chiaroscuro - shadow
  as one flat ink pool with a clean boundary, not built from hatching. Named
  its two closest-adjacency risks directly and ruled against both: the
  Discworld wing's dense stipple, and the Wheel of Time wing's interlace
  (both share this wing's night-sky palette, spectral-adjacent warmth, or
  amber/gold accent, so the differentiation had to be explicit, not implied).
- **backgroundTexture**: damp, rain-cockled paper with feathering ink -
  distinct from Jordan's homespun weave and Pratchett's toned broadsheet.
- **accentUse**: sodium-amber on exactly one lit surface per image (lantern
  glass, a lit window, one brass fitting), never a wash.

## Avoid

Named per-genre cliches (wizard hats/glowing spells; trench-coat noir
signage; toga-and-laurel pageantry; brass-goggles steampunk kitsch;
leather-clad urban-fantasy cover pose) plus the two cross-wing technique
reservations (stipple, interlace) and the standard "accent as wash" ban.

## Validation

`python scripts/validate.py --slug jim-butcher` - clean, no errors (the
standing `theme.art` error is gone). `python scripts/asset_audit.py
jim-butcher` now reports `art:yes` and lists 7 unblocked jobs (4 life
events, 3 franchise events; 0 eras since eras.yaml is `[]`).

## For downstream

Asset prompts are not written here - that is the next stage's job, working
directly against this art block. The 7 listed jobs (jim-butcher-born-1971,
storm-front-exercise, storm-front-published-2000, codex-alera-bet-2003,
turn-coat-number-one-2009, cinder-spires-deal-2013,
peace-talks-battle-ground-split-2020) are what `asset_audit.py` lists next.

Commit: e9190d2.
