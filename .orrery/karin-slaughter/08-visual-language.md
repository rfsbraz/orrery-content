# Karin Slaughter - visual language handoff

## Emblem: the stainless exam table

An empty examination table, wiped to a shine, one overhead lamp switched
off above it, a few instruments laid in a single parallel row along its
near edge, and a closed case file squared at the far end, tied shut with
string. The table itself is the throughline, not what has ever crossed it:
the same object sits unchanged in a small county clinic in Grant County and
in a state facility in Atlanta, so it carries Sara Linton's own path from
rural coroner to GBI-adjacent forensic work without needing a different
look for either setting. It reads first as furniture - clean, orderly,
unremarkable - because the method is the subject, never a body on it.

## Motifs

Red Georgia clay and kudzu-smothered structures (barn, silo, fence line);
a small county courthouse square (Grant County's Heartsdale register); an
anonymous, fluorescent-lit Atlanta government corridor with stacked case
folders (the GBI register); the exam table itself, always empty; a manila
case file curled and foxed with humidity; a screened porch in heat-haze;
kudzu overtaking chain-link, a telephone pole, an abandoned gas pump; and
an investigator or examiner seen from behind or three-quarter on, hands at
work, face never the point of the frame (explicit permission for anonymous
figures, since a crime scene and a courtroom both genuinely have people in
them).

## Spanning rural Grant County and Atlanta Will Trent

The motif list is deliberately built as a pair down its middle: the clay
road and courthouse square carry Grant County, the government corridor and
badge-on-a-lanyard carry Atlanta, and the emblem (the exam table) and the
case-file motif belong equally to both, since forensic method and case
paperwork don't change character when Sara's career moves from one to the
other. Atmosphere states the same split explicitly (Grant County close,
small and sun-bleached; Atlanta taller, cooler-lit, more anonymous) while
holding both to the same procedural calm rather than switching moods.

## Line, texture, accent

`lineCharacter`: a fine dip-pen line laid down warm and slightly wet, so it
blots and softens a little at the tail of each stroke, as if the paper has
taken on humidity - one consistent register throughout (not an alternating
technical/organic split), with forensic objects held as steady as the
humidity allows and foliage/heat-haze let go looser on the same pen.
`backgroundTexture`: warm parchment with a humidity-cockle and occasional
faint water-stain ring, never a wash covering the sheet. `accentUse`: the
palette's kudzu green on exactly one element (a vine tendril, a case-file
tab, a surveyor's flag, a lit exit sign), never a fill.

## Differentiation from the neighbouring crime wings

Read both `theme.art` blocks in full before writing. Gillian Flynn's line
is ballpoint-clean and bone-dry (a copy-desk edit mark, from her
journalism years) - this wing's line is never dry, it visibly blots with
damp on every stroke. Tana French's line is a cold, twice-scratched
dry-point retrace (an interrogation, doubled for an unreliable narrator) -
this wing draws once, warm, and lets the humidity do the softening instead
of a second pass. Both differences are named directly in the `avoid` list
so a future prompt-writer sees the guardrail without re-deriving it. Jo
Nesbo's ledger was also checked (a dual ruled/freehand register from his
finance-analyst years); this wing stays a single consistent register
throughout rather than alternating two techniques, which was a deliberate
choice to avoid converging on that same structural trick for an unrelated
reason.

## Avoid list

Graphic gore, visible wounds or an autopsy shown in progress (forensic work
stays clean tools and clean surfaces, an empty table and a closed file,
never a body or blood); crime-thriller cover costume (chalk outlines,
crime-scene tape and caution cones, a bloody knife shown in use);
Southern-gothic postcard kitsch (literal Spanish moss, plantation-ruin
decay, rocking-chair-porch nostalgia); Gillian Flynn's ballpoint-clean line
or Tana French's twice-scratched interrogation staging by name; Atlanta
reduced to skyline-postcard iconography rather than its anonymous
corridors; and the ABC "Will Trent" or Netflix "Pieces of Her" adaptations'
visual identity.

## Validation

`python scripts/validate.py --slug karin-slaughter` passes clean: `OK - 573
works, 34 authors, 32 characters, 11 achievements, all references resolve.`
The prior `theme.art` error is gone. `asset_audit.py karin-slaughter`
reports `art:yes` and now lists 11 pending jobs (3 life events, 8 franchise
events). One YAML-mechanics fix needed after the first write: two `avoid`
list items opened with a colon on their first line ("crime-thriller cover
costume: chalk outlines...") which YAML parses as a nested mapping key
inside a plain scalar sequence entry - rephrased both to drop the colon
rather than quoting the whole line. Commit `a99a6c0` on
`wing/karin-slaughter`, not pushed.
