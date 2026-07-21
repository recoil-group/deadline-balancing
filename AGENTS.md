# AGENTS.md

## Project Context

This public repo is Deadline's balancing/data workspace. It contains game CSVs, focused change sheets, generated changelogs/diffs, and balancing-team tools.

This is not the main game source repo. When available, sibling `../deadline` is a roblox-ts project whose `src/` compiles to `out/`, which Rojo syncs into Studio. Read `../deadline/AGENTS.md` or `../deadline/CLAUDE.md` before working there.

A connected Roblox Studio place may contain attachment, weapon, and other game data that is not represented in this repo or the main source repo.

The root balancing CSVs are authoritative for the stats and fields they define; in particular, `balancing.csv` is the master sheet for general attachment stats. They are not complete definitions: inspect Studio for the additional weapon and attachment data, and consult `../deadline` for how CSV and Studio data are applied at runtime.

## Repo Map

- `README.md`: quick overview and local script usage.
- `balancing.csv`: primary attachment stats sheet.
- `testing.csv`: testing/dev import sheet; ignore unless specifically asked to use it.
- Root CSVs loaded into Studio include `calibers.csv`, `optics.csv`, `lasers.csv`, `flashlights.csv`, `camo.csv`, and `progression.csv`.
- `changes/`: focused one-time change sheets, usually paired `.csv` and `.xlsx`. The `.xlsx` files are the human-editing source of truth; Python scripts read the `.csv` files.
- `archive/`: historical balancing CSVs for changelog generation.
- `changelogs/` and `diffs/`: generated Markdown changelog outputs.
- `demos/`: small HTML balancing visualizations/tools.
- `renaming/`: temporary renaming helpers.

## Git Workflow

- Prefer working directly on `main` unless the user specifies a different branch or workflow.

## Balancing Repo Notes

- `name` is the primary key used to match items across CSVs and Studio.
- `fire_rate` and `bullet_damage` are fractional modifiers applied to base weapon or ammo stats.
- The scripts use `utf-8-sig` CSV handling. This standard should apply to all CSVs.
- Empty cells in change sheets are significant: `port.py` can overwrite target cells with empty strings.
- For CSV work, check `git status --short`, read `README.md`, and sample the first three lines (`sed -n '1,3p' <file>.csv` or `Get-Content <file>.csv -TotalCount 3`).

## Related Source and Studio Context

The general data flow is:

```text
balancing.csv -> imported csv_stats -> stats keyed by name -> completed item build
calibers.csv  -> imported csv_calibers -> caliber data -> selected ammunition properties
...other root csvs
```

Useful balance-related source landmarks in `../deadline` include:

- `src/shared/module/namespace/AttachmentStatsData.ts`: loads general, optic, laser, and flashlight CSV data.
- `src/shared/module/namespace/CaliberManifest.ts`: loads caliber/ammunition data and resolves referenced projectile/shell assets.
- `src/shared/class/ItemBuild/`: build traversal, compatibility, attachment handling, and final stats. Start with `BuildConfig.ts`, `ItemBuild.ts`, `module/count_stats.ts`, and `module/attach_accessories.ts`.
- `src/shared/framework/core/manifest/AttachmentManifest.ts`: associates registered attachments with their CSV stats and Studio definitions.
- `src/shared/framework/core/manifest/item/framework_properties_manifest.ts`: associates item definitions with base CSV stats.

Studio data conventions:

- Weapons live under `ReplicatedStorage.data.item.<category>.<weapon>`.
  - `properties` defines intrinsic weapon behavior outside the general CSV, such as base RPM and fire modes, operation and magazine types, animations and sounds, procedural handling, and mappings from completed stats to concrete gameplay values.
  - `defaults` defines the stock nested attachment build. Changing it can change the stock weapon's completed stats and behavior without changing the weapon's own CSV row.
  - `model`, `offsets`, and `player_offsets` define geometry and presentation; named parts and attachment points can also affect behavior.
- Attachment definitions live under `ServerStorage.attachment_data`. Each attachment is a root `ModuleScript` whose returned table can define its type, display data, compatibility, nested mount map, default children, incompatibilities, and `global_flags`.
  - A child `runtime_properties` module defines category-specific behavior not represented by ordinary general stats, such as an ammo caliber selection, optic behavior, magazine display behavior, or muzzle particle and flash-hider behavior.
  - A child `property_patch` module can replace portions of the weapon's intrinsic `properties`, including RPM, fire modes, recoil mappings, animations, operation type, or magazine type. Check it when a conversion changes more than its visible CSV deltas suggest.
  - A child `attributes` module generally defines selectable appearance or configuration data. Verify its consumer before assuming it is gameplay-neutral.
- Current source assigns weapon base stats from the CSV row matching the weapon name and replaces an attachment's inline `stats` with the CSV row matching the attachment name. Treat inline Studio `stats` as legacy or non-authoritative unless current source shows a different path.

Other useful Studio landmarks include:

- `ReplicatedStorage.data.csv`: imported, chunked copies of the root CSVs.
- `ServerScriptService.ext-util.attachment-management`: Studio-side attachment import/export and maintenance utilities.

## Roblox Studio MCP

Studio MCP is read-only by default. Use inspection/search/read tools; do not mutate Studio or start/stop Play unless the user explicitly requests a change, command, or test run.

The MCP server is configured in `~/.codex/config.toml`.

On macOS:

```toml
[mcp_servers.Roblox_Studio]
command = "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
```

On Windows:

```toml
[mcp_servers.Roblox_Studio]
command = 'cmd.exe'
args = ['/c', '%LOCALAPPDATA%\Roblox\mcp.bat']
startup_timeout_sec = 30
```

The connected Studio most likely has place ID `7452050927`, though other Deadline places are possible. Confirm the active instance before relying on it.

In Studio, start with the narrowest relevant service/folder and inspect an Instance before reading its script. Large broad tree dumps are slow and noisy.

## Other Notes

- Keep private source code, server-only implementation details, credentials, unreleased content, and proprietary Studio data out of this public repo unless the user explicitly requests publication.
