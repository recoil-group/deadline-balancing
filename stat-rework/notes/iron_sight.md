# Iron sight family: re-stat notes

Rules in `rules/iron_sight.py`, overrides in `overrides/iron_sight.csv` (1 row). No weight
credit.

## Rules applied

| Sub-category | Rule | Result |
|---|---|---|
| Front and rear sights, apertures, posts, folding BUIS (folded or raised), weapon-integrated sights (AK, Mosin, pistols, SA58, UMP, G3, RPG, PSRL) | handling = 1.5 E, reload 0, stability 0 | +1 → h +1.5 (EV 0.9) |
| Fixed tall sights that compete with folding BUIS on rails: Axtell fixed, Vectorworks Peak, KF standard post and diopter, the M4 front-sight gas block | handling = 1.0 E | +1 → h +1; FSB +3 → h +3 |
| Carry handles (Hart M4A1, Tristar, Cosmotac VISM, SG58, FAL long) | handling = 1.0 E (fixed tall) | Tristar +4 → h +4 |
| Bases, blocks, hoods, 0-value posts | 0 | value lives in the sight on top |
| Misfiled parts | their real family's rules | see below |

Why:

- An iron sight only changes how quickly the sight picture comes together, so its value is
  handling. Reload is 0 and stability is 0: a sight does not steady the gun.
- Since 0.25.2 every sight is +1 whether folded or not (9a43e1b), and two count, so two plain sights
  give +3 handling. Folded and raised states are the same part and score the same.
- The lead's rule "folding/low-profile slightly better than fixed tall ones" is applied only
  where the two actually compete (rail-mounted sights and the M4 FSB against a low-profile gas
  block with a folding front). Integrated sights with no folding alternative keep 1.5, so whole
  weapons do not shift for no choice. The difference is 0.5 handling per sight.
- Carry handles keep their old premium (+1…+4) as handling, under the fixed-tall factor. They
  also host the carry-handle optics. Tristar was already cut 7 → 4 by the team.

## Overrides

- `hughnitions_company_extra_high_front_sight` +2 → h 1.5. Every other sight was cut to +1 in
  0.25.2; this one looks missed, and it was the best item in its slot on every stat.

## Misfiled items (re-statted with their real family's rules)

- `ak12_std_415mm_barrel`, `kazarov_group_ak12k_314mm_barrel`,
  `kazarov_group_std_rpk16_559mm_barrel` → barrel. **They carry `is_iron_sight` in Studio**, so
  they compete with real iron sights for the "first two iron sights" stacking slots. On an AK12
  with two more flagged sights, either a sight's or the barrel's non-weight stats may be dropped,
  depending on order. This looks like a Studio flag bug worth checking.
- `ak12_gen2_dustcover` → receiver (also flagged `is_iron_sight`; it has the integrated rear
  sight).
- `archient_technologies_elysium_addon_module` → handguard. It is also **flagged
  `is_iron_sight`**, so its −8 can be dropped by fitting two other flagged sights before it. That
  is a possible exploit.
- `sanxian_qbz95_carry_handle` (+10) → handguard. It competes with the QBZ95 top rails (8–11),
  which are handguard parts, so it uses the same split.
- `hart_m4fs_gasblock` stays here (an FSB is a sight), but competes with internals gas blocks.
- Holotec sight hoods (0) are optic accessories; all are 0.

## Remaining dominations (all explained)

- Pistol rear sights (Glock pattern, Makarov): all +1, differing only in real weight (0.01–0.05
  dw): night, suppressor-height, fibre and plain sights are visual or night-use variants.
- Axtell front against rear rail base, AK74 against AKM rear sight blocks: front and rear bases
  share a rail set but are not alternatives; the blocks differ only in weight.
- **Best in set on all three:** Tristar, the AK12 Gen1 rear sight and the carry handles in the
  picatinny iron-sight rail sets. Those sets are mostly 0-value bases whose value sits in the
  child sight, and every iron sight has 0 reload and 0 stability, so the top handling item is
  "best on all three" by construction.

## Open points I decided myself

- Carry handles and the M4 FSB at +3/+4 look high next to a +1 folding sight. I kept them, at the
  fixed-tall factor, because the Tristar cut shows the team set these values deliberately. If the
  FSB +3 is also a missed 0.25.2 port, it should become +1. On the M4 stock build (FSB, carry handle,
  aperture), old +7 becomes h +7.5 (EV 4.5). The weapon-base calibration absorbs the shift, and
  folding-BUIS builds gain about 1 EV relative to it.
- Stability stays 0 for every iron sight; there is no physical case for sway from a sight.
