> **Lead decision after review (round 2):** this pass keeps each round's old value as handling = E,
> stability = 0.85·E, reload 0 (EV = E), so calibre parity and shotgun-special compensation
> survive the split. `rules/ammo.py` `MODE = "zero"` restores the zeroing argued below. The rest of
> this note is the case for zeroing and its per-round cost.

# Ammunition (134 rows: cartridges, 12g shells, RPG-7 warheads)

## Decision: 0 / 0 / 0 on every round (lead's default kept, deliberately)

Rule: a round does not change ADS speed, reload speed or sway, so all ammo gets handling 0,
reload_speed 0, stability 0. Recoil, deviation, velocity, loudness, weight and price are left
exactly as they are; nothing is moved into recoil. Implemented in `rules/ammo.py`; no overrides.

### What the old ammo ergonomics was

- Range −4…+3 (bean bag +10, birdshot +5, slug +4). Archetypes: tracers and subsonics +1…+3,
  hot / +P / JHP / match / heavy AP −1…−3 (RULES_MINED.md section 5).
- Within-calibre regression on 115 non-default rounds (R² 0.61): tracer +1.1, subsonic +1.8,
  −0.22 per point of average recoil, −0.15 per +100 velocity, +0.29 per +0.1 deviation,
  −0.2 per 1000 credits. So it ran **with** recoil (soft rounds got less recoil *and* more ergo),
  against velocity and accuracy, and against price. It was a filler that topped up rounds that
  were weak on the scored stats.
- The history says so directly: the ammo super sheets score ergonomics at 1 point in
  `balance_score`; `556-ammo-super.xlsx` C6 says "tracer = most ergo unless subsonic is there";
  `10mm-super.xlsx` G15 calls it tracer "logic" that should be undone at some point.

### Why not stability (the miner's option B) or recoil (option A)

- Stability would make tracers and subsonics reduce breathing and walking sway. No player could
  predict that from the round, and it would make "soft" rounds doubly soft, since they already
  carry less recoil. Handling or reload (option C) are worse fits still.
- Recoil is the physically right home for "harshness", but the soft rounds already have the lower
  recoil; folding ergo in would widen recoil gaps that were tuned and played. The case is not
  strong enough to touch recoil (RULES.md section 7), so I did not.

### Is the tracer / subsonic compensation still needed?

- Tracers: no. Their drawback (a visible trace) is real, but they keep −1…−3 recoil per axis and
  +0.3…+0.5 suppression. On the super sheets' own strength score, with ergo removed, tracers
  still score at or above the issue round in 5.56 (+0.9 vs −2.6), .308 (−2.7 vs −3.7), 9mm
  (−2.3 vs −2.4) and 7.62x39; they fall just under it in 5.45 (−0.5 vs +0.3).
- Subsonics: they lose the most (+3 in .308, 7.62x54R, 5.45, 9mm). Their reason to exist is
  loudness −0.5…−0.6 with a suppressor, which the strength score does not count. Losing about
  15 ms of ADS does not change that niche. If playtests show them unpicked, give them −1 h / −1 v
  recoil rather than a sway bonus.
- Slot parity on the super sheets' strength (SD inside each calibre, with → without ergo):
  shrinks in 4 (7.62x39 4.7→4.3, 10mm 5.3→5.1, .45 3.4→2.5, 7.62x25 1.25→0.76), flat in 3
  (5.56, .40, 5.8), grows in 5 (.308 3.6→4.1, 7.62x54R 3.5→4.3, 5.45 1.1→1.3, 9x18 0.3→0.9,
  9mm 1.8→2.6). Those five are the calibres where ergo was used as the equaliser; their super
  sheets need re-scoring with ergo removed from `balance_score` if the team wants the old parity.

### Size of the change

An old ergonomics point bought about 5 ms ADS and 0.4% reload speed (plus draw/stow/stamina, which
now come from weight for every round alike). Each round therefore moves by its old ergo against
the issue round: a +3 round loses about 15 ms ADS and 1.2% reload; a −2 round gains about 10 ms
and 0.8%. Defaults are 0, so stock builds do not move; the 12g default (00 buck, −3) moves into
the shotgun bases at calibration.

The largest relative moves are the shotgun specials against buckshot: slug −7, birdshot −8, bean
bag −13 old points (35–65 ms ADS). These were never physical (a slug does not ADS faster); slugs
keep their +600 velocity and accuracy at +3/+3 recoil, birdshot its 152 pellets, the bean bag
its −15/−10 recoil. Flagged for the lead as the one place the decision is felt.

Per calibre (old ergo = EV each round gives up, positive, or gains, negative, relative to today):

| class | gives up (old ergo > 0) | gains (old ergo < 0) |
|---|---|---|
| ammo_10mm | 10mm Roosevelt Trailblazer 135gr Green Tracer +2; 10mm Chicago Ammunition 220gr RNFP +1; 10mm Federal Premium 125gr RHT +1 | 10mm Polar Cartridge 220gr HCFP -3; 10mm Freedom Civil Defense 60gr HPLF -2; 10mm Federal HST 175gr JHP -2; 10mm Underworld 180gr XTP JHP -2; 10mm Appalachian Silvertip 175gr JHP -1; 10mm Copperhead Honey Badger 115gr EHP -1 |
| ammo_12g | 12G Fox Hill 2.75" Mean Bean Bag +10; 12G Federal Game Load 2.75" 4-Shot (152 Pellets) +5; 12G Roosevelt Accutip 2.75" Slug +4 | 12G MILI 2.75" #00 Buckshot (9 Pellets) -3 |
| ammo_40sv | Federal STREAK 180gr TMJ Tracer +3; Federal Cartridge Mk.309 Mod 0 155gr Ball +1; Lance Lawman 125gr RHT +1; S2 Research RIP 115gr FHP +1 | Federal Cartridge Mk.308 Mod 0 155gr JHP -2; Federal Premium 180gr HST -1; Appalachian Ranger T-Series 180gr JHP -1; Sierra 9 Woodsman 130gr Monolithic Solid Copper -1; Sierra 9 Barrier Blind 77gr APC -1 |
| ammo_45acp | .45 ACP Pulsar 225gr Red Tracer +3; .45 ACP Bison Bore 185gr JHP +2; .45 ACP Munitions Incorporated 230gr Subsonic TMJ +2; .45 ACP S2 Research 162gr RIP +1; .45 ACP Lance Lawman 155gr RHT Frangible +1 | .45 ACP Federal Defense 185gr FMJ SWC -4; .45 ACP Sierra 9 Defense 117gr APC -3; .45 ACP Federal Defense 230gr HST JHP -2; .45 ACP Underworld 255gr Hardcast Flat Nose -2; .45 ACP Lance Lawman 230gr TMJ -1; .45 ACP Lance Gold Dot 230gr BJHP -1 |
| ammo_5.45x39 | Lugansk 7U1 79gr US +3; Kazarov 7T3 49gr Red Tracer +2 | Kazarov 7N10 56gr PP -1; Fox Performance 55gr HPBT -1; Hawthorne BLACK 60gr V-MAX -1; Kazarov 7N40 64gr FMJ -1; TsNIITekhMash 7N39 63gr Igolnik -1 |
| ammo_5.8x42 | Sanxian DBX95 64gr Green Tracer +3; Sanxian DBX10 71gr Tracer APBT +1; Sanxian DBP191 74gr FMJ +1; Sanxian DVF18 76gr HP +1 | Sanxian DVC12 85gr AP -2; Sanxian DBP10 71gr FMJ -1; Sanxian DBU141 86gr Match Grade -1; Sanxian DVP88 81gr AP -1 |
| ammo_556x45 | Anhalt Patrone DM51/DEA 55gr +1; Federal M856A1 64gr Red Tracer +1 | Copperhead Mk.262 Mod1 SMK 77gr -1; Emmeo M995 52gr AP -1; CAe L31A1 62gr Enhanced Performance -1; Appalachian M855A1 62gr EPR -1 |
| ammo_7.62x54r | TsNIITekhMash Bramit 148gr Subsonic +3; Norilsk 7T2M 149gr Green Tracer +2; Prva Garda Rifle Line 150gr SP-BT +1; Serrano & Belmonte 174gr HPBT +1 | TsNIITekhMash 7N37 Chórnoye Górlyshko 182gr BS -2; Norilsk B-32M 162gr API -2; Norilsk 7N1 Snaiperskye 151gr PS -1; Norilsk 7N14 Snaiperskaya 152gr SNB -1 |
| ammo_762x25 | 7.62x25 Type 64/P Subsonic +2; 7.62x25 Fiocchi 85gr FMJ +2 | 7.62x25 Z113 Factory ĐS-K51XG 80gr AP -2; 7.62x25 Czech vz.48 85gr FMJ -2; 7.62x25 Tula 57-N-134S 85gr Pst -1; 7.62x25 57-T-134S PTS AP -1; 7.62x25 PPU 85gr FMJ -1 |
| ammo_762x39 | Serrano & Belmonte Sv43 123gr Red Tracer +2; Hawthorne Sub X 255gr Subsonic +1 | TsNIITekhMash 8M3 Effect 124gr Hollow Point -2; Kazarov 7N23 BP gzh 122gr -2; Prva Garda Rifle Line 123gr JSP -1; Laukaa S405 123gr FMJ -1 |
| ammo_762x51 | Hawthorne .308 Sub X 190gr Subsonic +3; Appalachian M62 142gr Red Tracer +2; Appalachian Mk.319 Mod0 130gr OTM +1 | Appalachian M80A1 130gr EPR -1; CAe L59A1 155gr Enhanced Performance -1; Emmeo M993 129gr AP -1; Federal M118LR 175gr OTM -1 |
| ammo_9x18 | Novosibirsk 57-T-181 56gr Red Tracer +1; Kazarov 7N25 PBM 56gr AP +1 | Bison Caliber 115gr HCFN +P -2; Hawthorne XTP 95gr JHPFB -1; Underworld Xtreme Penetrator 95gr SM -1; TsNIITekhMash SP7 gzh 80gr -1 |
| ammo_9x19 | ZFM Luger 154gr FMJ-FP Subsonic +3; Pulsar 119gr Green Tracer +2; S2 Research RIP 92gr FHP +1 | Appalachian M1152 115gr FMJ-FN +P+ -2; Kazarov 7N31 PBP gzh 64gr +P+ -2; Appalachian XM1153 147gr JHP -1; Novosibirsk 7N21 80gr PST -1; BVT Scorpio NATO 115gr FMJ +P -1 |
| rpg7_warhead | - | - |

RPG-7 warheads had no ergonomics and stay empty.

## Dominations

`check_family.py` reports 74 ammo pairs. They are artefacts: the checker sees only sheet columns,
while rounds differ mainly in calibers.csv (damage curves, penetration, suppression, tracer,
pellets, fire). 59 of the 74 pairs are already dominated today with old ergonomics included as a
column; the 15 new ones are rounds whose only sheet-visible edge was ergo (tracers, HP rounds,
birdshot, dragon's breath against buck) and all have calibers.csv advantages. Not fixed.

## Data oddities seen (not changed)

- `bullet_velocity` 0.02 on `10mm_roosevelt_umc_180gr_fmj`, `10mm_polar_cartridge_220gr_hcfp`,
  `40sv_federal_american_eagle_180gr_fmj`, `40sv_federal_premium_180gr_hst` looks misplaced.
- Five .45 ACP / 7.62x25 rows have no Studio category (not reachable).
