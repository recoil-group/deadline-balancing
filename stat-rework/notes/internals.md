# Internals family: re-stat notes

Rules live in `rules/internals.py` (it reuses `mass_z` and `split` from `rules/receiver.py`); 4 hand
overrides in `overrides/internals.csv`. Weight credit 0. Existing trigger and auto-sear fire rates are
untouched; since round 6 the Mosin bolt and knob carry `fire_rate` (below).

## Split rules (fractions of old ergonomics: handling / reload / stability)

| Kind | Split | Mass lean | Why |
|---|---|---|---|
| Fire selectors, safeties, switches, decockers | 1.6 / 0 / 0 | none | the fire-mode switch is a handling animation |
| "Enhanced safety" selectors (bolt hold-open notch) | 0.8 / 1.2 / 0 | none | the notch is used to lock the bolt back |
| Charging handles, bolt catches/releases, BAD lever, mag catch, Mosin bolt and bolt handle, R700 bottom metal | 0.7 / 1.3 / 0 | 0.2 toward reload | empty reloads and manual loading; a bigger latch is quicker to grab, ambi counts as +0.3 z |
| Triggers, trigger shoe, trigger bar, trigger-blade safety | 0.5 / 0 / 1.0 | 0.4 | a lighter, crisper pull disturbs the aim less; a trigger does not speed ADS. EV ≈ 0.77 of old |
| Trigger guards | 0.8 / 0 / 0.5 | 0.4 | quicker gloved access to the trigger; a stiffer guard steadies a little. EV ≈ 0.72 of old |
| Takedown levers | OEM: selector split; aftermarket: old value as handling, +1 stability | – | extended/ledge levers are thumb rests |
| Case deflectors (AUG) | 0.8 / 0 / 0.9 | 0.5 | at the cheek on a bullpup; low-profile leans handling |
| Bolts, carriers, BCGs (semi/auto) | 0.8 / 0 / 0.9 | 0.5 | light carrier leans handling, heavy/enhanced leans stability; buffered SCAR carrier takes its −1 on handling |
| Gas blocks, pistons, gas selectors | 1.0 / 0 / 0.8 | 0.5 | low-profile leans handling, heavy leans stability |
| Auto sears | 0.5 / 0 / 1.5 | none | full-auto conversion is hard to hold |
| Springs, guide rods, retainers, hammers, pins, extractors, ejectors, plungers, bolt faces/plugs, lugs | zero | – | no effect on any of the three |

Trigger choice (lead asked to decide): stability, not near zero. Aftermarket triggers sell a lighter,
crisper pull, which is what steadier aim means here; zeroing them would have made the expensive match
triggers pure fire-rate/deviation picks and left the default ones dominated. Scaled to ~0.77 of the
old value so they are less of a free source than before.

The mass lean uses the same `z` (−1 lightest … +1 heaviest in the competing set) as receivers.
Bolt-action bolts (all weapons Mosin/R700) are treated as reload controls, since their old ergonomics
sped bolt work that now belongs to fire rate for cycling; nothing goes to fire rate.

## Overrides

- `kf_416_trigger` = `hart_m4a1_std_trigger` (h1 / s2): both mil-spec single-stage, both free; the old
  +1 made the 416 trigger a free domination.
- `aft_mk20_gas_block` h4 / s0.5: low-profile, no front sight base; otherwise best on all three.
- `corvus_mounts_m4_trigger_guard` h3.5 / r9.5: R700 bottom metal (internal box) filed as a trigger
  guard; reload control, trimmed so reload stays under 10.
- `hera_arms_straight_pull_charging_handle` h2 / r9: non-reciprocating side charger, quickest on
  empty reloads; separates it from the lighter Raptor (they tied).

## Remaining dominations (explained)

- **Slide backplates > auto sears** (KOSCH): the sear's payoff is `fire_rate +0.71`, which the check
  does not count as better. Not a real domination.

## Best on all three (left, with reason)

Mostly ties at zero in an axis the part cannot touch (selectors have only handling; gas blocks and
triggers have no reload), plus price: `ardian_weapons_ar15_talon_ambi_2lever_fire_selector` (pricier),
AR gas blocks (all zero; recoil and weight decide), `metrik_precision_..._skeletonized_trigger` (others
zero; $750), `cerberus_arms_aug_raptor_charging_handle` and the DDG ambi SCAR handle (highest old
value; heavier and pricier), `resolute_bolt` (lighter and +3 over the default bolt in the old sheet;
$200).

## Misfiled / notes

- `corvus_mounts_m4_trigger_guard` is R700 bottom metal (magwell slot), not a trigger guard.
- `kosch_*_auto_sear` sit in the slide-backplate slot.
- `sig_sauer_p320_takedown_lever` is the only P320 lever (default), so it is treated as OEM (zero).

## Round 5: reload scope

Reload hardware is re-statted by kind (`reload_scope.py`, RULES.md section 13):

- Bolt catches and releases, and the B.A.R. lever: −2%.
- KOSCH ambidextrous magazine catch: −3%, like the other enhanced releases.
- Enhanced charging handles: −(1% + 0.25% per 0.01 dw), so −1.5% for the 0.02 dw extended latches to −3.7% for the 0.11 dw straight-pull side charger. The latch size sets it, and the part's weight measures that size.
- R700 Badger bottom metal: −3%, as a flared well.
- Standard charging handles (Hart M4, AFT, Scalar, SG58, Aquila AUG), the Mosin default bolt and infantry handle, the AK enhanced safety and triggers hold 0, with their old reload share moved into handling (EV kept).

## Round 6: cycling

The Resolute bolt and the Crazy Ivan knob are cycling parts. Their reload is 0, and each carries
`fire_rate +0.01` (Mosin 50 → 50.5 RPM), priced at 3 EV and taken out of their handling, so their
value is unchanged (`cycling.py`, RULES.md section 14). The Mosin default bolt, the infantry bolt
and the infantry handle are 0. The R700 has no choosable cycling part.
