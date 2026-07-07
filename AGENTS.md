# AGENTS.md

## Project Context

This repo is the balancing/data workspace for the Roblox game Deadline. It is not the main game source repo. The connected Roblox Studio place exposes compiled/synced game code, runtime modules, remotes, config modules, item/property modules, maps, assets, and Studio utility scripts.

Default Studio MCP posture: read-only. Use `get_studio_state`, `search_game_tree`, `inspect_instance`, `script_search`, `script_grep`, `script_read`, and `get_console_output` for exploration. Do not use mutating tools such as `multi_edit`, `insert_asset`, `generate_material`, `upload_image`, `execute_luau`, or `start_stop_play` unless the user explicitly asks for a Studio change or command execution.

## Repo Map

- `README.md`: quick overview and local script usage.
- `balancing.csv`: primary attachment stats sheet.
- `testing.csv`: testing/dev import sheet.
- Root CSVs loaded into Studio include `calibers.csv`, `optics.csv`, `lasers.csv`, `flashlights.csv`, `camo.csv`, and `progression.csv`.
- `changes/`: focused change sheets, usually paired `.csv` and `.xlsx`.
- `archive/`: historical balancing CSVs for changelog generation.
- `changelogs/` and `diffs/`: generated Markdown outputs.
- `demos/`: small HTML balancing visualizations.
- `renaming/`: attachment rename helpers and intermediate data.

## Local Scripts

- `python port.py <change sheet> <target sheet> <header row>` ports matching rows by `name` into the target CSV and updates the target timestamp. The current code requires the header-row argument even though `README.md` describes it as optional.
- `python changelog.py <old sheet> <new sheet>` writes `changelogs/<version>.md`.
- `python diff.py <old sheet> <new/change sheet>` writes `diffs/<new-sheet-name>.md`.

The scripts use `utf-8-sig` CSV handling. Empty cells in change sheets are significant: `port.py` can overwrite target cells with empty strings.

## Studio MCP

The MCP server is configured in `~/.codex/config.toml` as:

```toml
[mcp_servers.Roblox_Studio]
command = "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
```

On 2026-06-29, the connected Studio state was Edit mode for Deadline place `7452050927`, with available DataModel `Edit`.

If `list_roblox_studios` returns a stale/opaque ID while a place is open, inspect the latest Studio log under `~/Library/Logs/Roblox/*_Studio_*_last.log`, find the current `studioSid`, and call `set_active_studio` with that value before retrying state/tree tools.

## Studio Landmarks

- `ServerScriptService.main`: compiled roblox-ts server bootstrap. It requires `ServerScriptService.main.dl_server`.
- `ServerScriptService.main.controller`: high-level server controllers such as players, bots, protection, debug, misc setup, and tag handlers.
- `ServerScriptService.main.remote`: server remote definitions grouped by assignments, chat, data, framework, game, git attachment stats, insitux, match, and monetization.
- `ServerScriptService.main.server`: server systems, including classes, core services, gamemodes, modules, namespaces, web API, ECS, grenade systems, and AI.
- `ServerScriptService.main.server.namespace`: managers such as GameData, GamemodeManager, HitregManager, PlayerManager, ServerAttachmentManifest, WeaponControl, Anticheat, ChatManager, InsituxServer, ServerFramework, and ServerMetadata.
- `ServerScriptService.main.server.webapi`: web API code; avoid dumping secrets unless the user specifically asks and there is a clear reason.
- `ServerScriptService.storybook`: ModuleScript stories/tests for gameplay and GUI components.
- `ServerScriptService.ext-util.attachment-management`: Studio utilities for attachment import/export and maintenance, including `import_csvs`, `import_arbitrary_csv`, `regen_attachment_properties`, `balancing.generate_spreadsheet_data`, rename helpers, weld helpers, and PBR helpers.
- `ReplicatedStorage.client`: client entry modules, GUI tree, FX modules, namespaces, and controllers such as `dl_client`, `dl_replicator`, and `grenade_replicator`.
- `ReplicatedStorage.client.gui`: UI modules for main menu, loadout, deploy, settings, profile, shop, quests, servers, weapon editor, ingame/death/match views, chat, leaderboard, loading, and reusable components.
- `ReplicatedStorage.module`: shared modules for remotes, shared state, teams, casting, data, namespaces, raycasting, rodux, shootables, sight raycasting, utilities, voxels, grenades, and characters.
- `ReplicatedStorage.module.namespace`: data/runtime modules including `AttachmentStatsData`, `GitAttachmentStats`, `ProgressionData`, `CaliberManifest`, `AttachmentCamoData`, `TestConfig`, and serialization helpers.
- `ReplicatedStorage.module.util`: helper modules including CSV loading, attachment lookup, weapon setup parsing, rename/update helpers, and general utilities.
- `ReplicatedStorage.class`: shared class-like modules plus `GunshotEmitter`, `ItemBuild`, and `SoundEventPlayer`.
- `ReplicatedStorage.class.ItemBuild`: item build, compatibility, attachment type, and setup logic.
- `ReplicatedStorage.framework`: client/shared framework code, item manager, controllers, animation/simulation code, item framework code, and weapon/melee/throwable/healing logic.
- `ReplicatedStorage.data`: replicated assets and data folders for items, models, FX, sounds, attachment parts, attachment offsets, and chunked CSV data.
- `ReplicatedStorage.data.csv`: in-Studio CSV chunks for stats, progression, calibers, optics, lasers, flashlights, and camo.
- `ReplicatedFirst`: loading/startup scripts and fallback/loading GUI.
- `StarterPlayer`: standard player script containers plus custom starter character models/scripts.
- `ServerStorage`: large storage area with export `StringValue`s, resources/maps, PBR data/cache, client data, `TagList`, and `attachment_data`.
- `ServerStorage.attachment_data`: large attachment module tree with `ALPHA`, `PRELOAD`, `NEW`, and `CLOTHING`.
- `Workspace`: active scene folders for map, characters, effects, grenades, ignore/runtime folders, customization/editor rooms, terrain, camera, and some item models/modules with `properties`, `runtime_properties`, `stats`, or `attributes`.
- `SoundService`, `Lighting`, and `MaterialService`: audio presets/groups, lighting presets/effects, and material/surface appearance assets.

## Navigation Notes

- Start with the narrowest service/folder relevant to the task; the place contains very large trees, especially `ServerStorage`.
- Use `script_search` when a script/module name is known and `script_grep` for symbols or strings across Studio scripts.
- Use `inspect_instance` before `script_read` when checking whether a target is a script, module, value object, model, or folder.
- Treat Studio-side source as reference unless the user explicitly asks to modify Studio.
- For Studio-side adjustments, inspect the relevant instance and read involved scripts/modules before changing properties or code.
- For CSV work, check `git status --short`, read `README.md`, and sample headers with `sed -n '1,3p' <file>.csv` before editing.
