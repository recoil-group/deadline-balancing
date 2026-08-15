# deadline balancing

Attachment stats and other stuff for [Deadline](https://www.roblox.com/games/3837841034).

## changelogs

- [0.25.4](changelogs/0-25-4.md)
- [0.25.3](changelogs/0-25-3.md)
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

## balancing knowledge base

- [Balancing guide](knowledge/balancing.md): goals and design priorities.
- [Stat reference](knowledge/stats.md): stat behavior, units, formulas, and interactions.

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

Each version has up to two files:

- `x-y-z.csv` — a frozen snapshot of `balancing.csv` at release. Never apply
  renames to it. Only fix genuine errors in the snapshot itself, such as a
  shifted column or a dropped row.
- `x-y-z-renamed.csv` — the same snapshot with every rename made *since* that
  release applied forward. This is the base for the next version's changelog.
  Create it the first time a rename lands after the release, and keep applying
  later renames to it.

Renaming the frozen snapshot in place breaks changelog regeneration for that
version: its base sheet still uses the old names, so every renamed attachment
shows up as removed-and-new. Keeping the two files separate means old
changelogs stay reproducible while new diffs stay clean.

Cut the archive and generate the changelog in the same pass. If the snapshot is
taken days after the changelog, the two disagree by whatever landed in between.

### port.py

Script to port changes from a CSV or Excel change sheet into `balancing.csv` or `testing.csv`. Usage:

```bash
python port.py (change sheet) (target sheet) (header row)
python port.py "changes/changes.csv" "testing.csv" 2
python port.py "changes/changes.xlsx" "balancing.csv" 2
python port.py "changes/changes.xlsx" "balancing.csv" 2 --dry-run
python port.py "changes/changes.xlsx" "balancing.csv" 2 --dry-run --format json
```

- Updates the date in the target sheet automatically.
- Matches rows by `name` column, make sure those are included in the change sheet.
- Order of columns in the change sheet does not matter.
- Empty cells will overwrite existing data. Be careful.
- `[header row]` is the row # of the column headers in the change sheet. Useful for extra labels or dates above the headers.
- Warns when source names or columns are not present in the target.
- `--dry-run` prints every proposed old-to-new value without writing and
  identifies blank overwrites. Exact textual differences such as `5` and `5.0`
  remain effective complete-state changes.
- Rows without a `name`, names absent from the target, and unknown source
  columns are ignored. The latter two are warnings in the preview.
- The preview also warns about blank overwrites, `pretty_name` changes, and
  source names or headers with surrounding whitespace. Warnings never stop a
  port. In text output, `!` marks warned change lines; JSON contains a complete
  structured warning list.
- An uncached formula in a cell that would be imported stops the port because
  its unknown result would otherwise be exported as a blank override.
- Writes are atomic, and the target date is updated only when cells change.

### xlsx_to_csv.py

Exports cached values from the first worksheet of an `.xlsx` or `.xlsm` workbook
to a UTF-8 CSV. Reports formula cells with cached or missing results.

```bash
python xlsx_to_csv.py "changes/changes.xlsx" [output.csv]
```

### inspect_xlsx.py

Prints a compact, read-only view of an Excel change sheet for coding agents. It
shows every worksheet, populated cells and coordinates, cached formula results,
repeated formula patterns, tables, merged ranges, comments, hyperlinks, and
hidden regions without rendering or modifying the workbook. Conservative
header cues identify likely table and section headers, including multiple
sections in one worksheet, while leaving interpretation to the reader.

Recommended agent workflow:

1. Run `inspect_xlsx.py` before using a general spreadsheet importer or renderer.
2. If the output is truncated or the task is focused, rerun it with `--sheet`
   and `--range`.
3. Use `--show-formulas` when exact expressions are needed inline.
4. Only render the workbook when the task depends on layout, formatting,
   charts, or other visual details.

```bash
python inspect_xlsx.py "changes/m4-stocks.xlsx"
python inspect_xlsx.py "changes/308-ammo-super.xlsx" --sheet Model --range A1:C39
python inspect_xlsx.py "changes/m4-stocks.xlsx" --sheet m4-stocks --range N3:Q5 --show-formulas
```

Use `--max-cells` and `--max-formula-patterns` to control output size, and
remember that formula results are cached values saved by Excel. The script does
not recalculate them or guarantee that they are current. Displayed floats are
rounded to remove unhelpful binary floating-point noise; workbook values are
never changed.

### update_xlsx_from_csv.py

Updates shared columns in an existing workbook from a CSV, matching rows by
`name` and skipping formulas by default. The workbook is updated in place.

```bash
python update_xlsx_from_csv.py "balancing.csv" "changes/changes.xlsx" 2
```

Use `--dry-run` to preview changes. Saving with `openpyxl` may clear cached
formula results. CSV names absent from the workbook are expected and are not
reported.

### fix_booleans.py

Lowercases `TRUE`/`FALSE` cells in any CSV. Accepts multiple files and rewrites
them in place, leaving all other cells untouched.

```bash
python fix_booleans.py calibers.csv
python fix_booleans.py balancing.csv optics.csv --dry-run
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
