# Bayonets, knives, lugs (11 rows)

## Rules (`rules/bayonet.py`)

- **Blade** = mass and length past the muzzle. It is slower to swing onto target (handling),
  makes walking sway worse and costs more to hold steady (stability), the same as a long barrel
  in RULES.md. **Decision: stability negative, not positive.** The heavy front's one genuine
  benefit, damping muzzle rise, is already on the sheet as −4…−5 vertical recoil, and counting it
  again as steadiness would pay for it twice. Split: handling 0.8 × A, stability 1.0 × A
  (EV 0.95 × A).
- **A = assembly ergonomics.** The blade is the gun-contact node, so its required one-option
  sub-parts give it their old ergonomics and keep only weight (RULES_MINED.md 9.4, following the
  Oct 2026 commits that moved sub-part ergo onto the base part). The grips, the AK scabbard
  slings and the M11 knife grip each carried +1.
  - AKM Type I and Type II: −4 + 1 + 1 = −2, giving h −1.5, s −2. Type II is heavier (0.25 against
    0.23 dw assembled) with more recoil damping (−5 against −4 v).
  - M9 Phrobis III: −3 + 1 = −2, giving h −1.5, s −2 (−5 v).
  - M11 EOD (not reachable): −4 + 1 = −3, giving h −2.5, s −3.
- **Lug** (Goliath AUG): a small clamp at the muzzle. handling = E = −1, no sway effect.

## EV drift

The two AKM blades show as drift (old −4, EV −1.8) only because the +2 of their grip and sling
moved onto them. The assembly stays at −2 old, now EV −1.84.

## Dominations

None. The two AKM blades trade weight against recoil.

## Round 7: profiles and roles

Handling and stability now come from each part's row in `profiles/bayonet.csv` (RULES.md section 15); the split rules, weight leans and overrides above are history for these two stats.

Bayonets cost handling (`handling`); containers and blank rows are `zero`.

Profiles: zero 6, handling 5. Unidentified counterparts: 0.
