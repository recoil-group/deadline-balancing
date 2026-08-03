# deadline balancing

Attachment stats and other stuff for [Deadline](https://www.roblox.com/games/3837841034).

## changelogs

- [0.24.2](changelogs/0-24-2.md)
- [0.24.1](changelogs/0-24-1.md)
- [0.24.0](changelogs/0-24-0.md)
- [0.23.3](changelogs/0-23-3.md)
- [0.23.2](changelogs/0-23-2.md)
- [0.23.1](changelogs/0-23-1.md)
- [0.23.0](changelogs/0-23-0.md)

## wiki

Contains information about stats, gameplay, mechanics, and more.

<https://github.com/recoil-group/deadline-balancing/wiki>

## demos

- [Shotgun spread demo](demos/shotgun-spread/)
- [Ammo damage curve demo](demos/ammo-damage/)

## repo guide

### balancing.csv

Master balancing sheet. Should always be up to date with the latest changes.

### testing.csv

Testing sheet. Gets imported into dev branch when updated.

### weapon_names.json

Dynamic weapon display-name rules keyed by weapon code. Each rule lists the attachments required for that name; nested attachment arrays are interchangeable options.

### /changes

Folder containing all change sheets. These are used to balance groups of attachments to then be ported into `balancing.csv`.

### /changelogs

Folder containing all generated changelog markdown files.

### /archive

Folder containing all balancing sheets from previous versions. These are used to generate changelogs.

### port.py

Script to port changes from a CSV or Excel change sheet into `balancing.csv` or `testing.csv`. Usage:

```bash
python port.py (change sheet) (target sheet) (header row)
python port.py "changes/changes.csv" "testing.csv" 2
python port.py "changes/changes.xlsx" "balancing.csv" 2
```

- Updates the date in the target sheet automatically.
- Matches rows by `name` column, make sure those are included in the change sheet.
- Order of columns in the change sheet does not matter.
- Empty cells will overwrite existing data. Be careful.
- `[header row]` is the row # of the column headers in the change sheet. Useful for extra labels or dates above the headers.
- Warns when source names or columns are not present in the target.

### xlsx_to_csv.py

Exports cached values from the first worksheet of an `.xlsx` or `.xlsm` workbook
to a UTF-8 CSV. Reports formula cells with cached or missing results.

```bash
python xlsx_to_csv.py "changes/changes.xlsx" [output.csv]
```

### update_xlsx_from_csv.py

Updates shared columns in an existing workbook from a CSV, matching rows by
`name` and skipping formulas by default. The workbook is updated in place.

```bash
python update_xlsx_from_csv.py "balancing.csv" "changes/changes.xlsx" 2
```

Use `--dry-run` to preview changes. Saving with `openpyxl` may clear cached
formula results. CSV names absent from the workbook are expected and are not
reported.

### fix_calibers.py

Lowercases `TRUE`/`FALSE` cells in `calibers.csv`, or in a supplied CSV.

```bash
python fix_calibers.py [calibers.csv]
```

### changelog.py

Script to compare two sheets and output a changelog. Usage:

```bash
python changelog.py (old sheet) (new sheet)
python changelog.py "archive/old-sheet.csv" "balancing.csv"
```

- Outputs a changelog to `changelogs/version-changelog.md`.
- Matches rows by `name` column.
- Uses the `pretty_name` column for display in the changelog, falling back to `name`.
- Reports changed and new entries.

### diff.py

Basically changelog.py but for comparing smaller change sheets. Usage:

```bash
python diff.py (old sheet) (new sheet)
python diff.py "old-sheet.csv" "changes/new-sheet.csv"
```

- Outputs a changelog to `diffs/new-sheet.md`.
- Matches rows by `name` column.
- Uses the `pretty_name` column for display in the changelog, falling back to `name`.
- Reports changed, new, and removed entries.
