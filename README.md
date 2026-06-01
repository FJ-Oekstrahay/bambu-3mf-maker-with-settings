# bambu-3mf-maker-with-settings

Two Python CLI tools for generating Bambu Studio `.3mf` files with process settings applied programmatically — no GUI required.

- **`stl_to_bambu_3mf.py`** — the everyday tool. Give it an STL and a settings markdown file, get a ready-to-open `.3mf`.
- **`make_bambu_3mf.py`** — lower-level. Patches an existing `.3mf` with per-plate settings, supports multi-material plates.

## Requirements

- Python 3.8+
- `numpy` (`pip install numpy`)
- `stl_to_bambu_3mf.py` only: `numpy` is required. `make_bambu_3mf.py` uses standard library only.

## Workflow

### 1. Get your settings file

The scripts consume a markdown settings file — a table of Bambu Studio settings with your chosen values. You can write it by hand or generate it with an LLM.

**To generate with an LLM (Claude, ChatGPT, etc.):**

Open `llm-settings-prompt.md`, fill in the YOUR PART section at the top (part name, material, what it is, key requirements), and paste the whole thing into your LLM. It will output a completed settings markdown ready to use.

**To write by hand:**

Copy `SETTINGS_TEMPLATE.md`, fill in the Value column for settings you want to change, leave the rest blank.

**To print the template from the CLI:**

```bash
python stl_to_bambu_3mf.py --print-template
```

### 2. Run `stl_to_bambu_3mf.py`

```bash
python stl_to_bambu_3mf.py \
  --stl your_part.stl \
  --settings your_settings.md \
  --material "TPU 95A" \
  --plate-name "My Part — TPU 95A"
```

Output `.3mf` is written to the same directory as the STL, named after the STL stem and material. Override with `--output path/to/output.3mf`.

Multiple STLs land on the same plate:

```bash
python stl_to_bambu_3mf.py \
  --stl left.stl --stl right.stl \
  --settings my_settings.md \
  --material "PETG-CF"
```

**All arguments:**

| Argument | Description |
|---|---|
| `--stl` | STL file(s) to include (repeatable) |
| `--settings` | Markdown settings file |
| `--material` | Material name (label and filament slot match) |
| `--plate-name` | Plate name shown in Bambu Studio (optional) |
| `--output` | Output `.3mf` path (optional — defaults to STL directory) |
| `--template` | Source `.3mf` template to use (optional — uses bundled A1 mini default) |
| `--print-template` | Print `SETTINGS_TEMPLATE.md` to stdout and exit |

### 3. Open in Bambu Studio

Double-click the `.3mf`. Settings are pre-applied. Slice and print.

---

## `make_bambu_3mf.py` — multi-plate / advanced use

Patches an existing `.3mf` with per-plate process settings. Use this when you already have a `.3mf` and want to apply settings programmatically, or when you need multiple plates with different materials in a single file.

```bash
python make_bambu_3mf.py \
  --source input.3mf \
  --plate 1 --material "PETG-CF" --objects 6,8 --settings petgcf.md \
  --output output.3mf
```

**Two plates, different materials:**

```bash
python make_bambu_3mf.py \
  --source input.3mf \
  --plate 1 --material "PETG-CF" --objects 6,8 --settings petgcf.md \
  --plate 2 --material "TPU 95A" --objects 2,4 --settings tpu.md \
  --output output.3mf
```

**Arguments:**

| Argument | Description |
|---|---|
| `--source` | Source `.3mf` file to patch |
| `--output` | Output `.3mf` file path |
| `--plate N` | Plate number (repeatable) |
| `--material` | Material name for this plate |
| `--objects` | Comma-separated object IDs to assign to this plate |
| `--settings` | Markdown settings file for this plate |

Object IDs must match those in the source `.3mf`. Check `Metadata/model_settings.config` inside the zip if you're unsure.

---

## Settings files

### Format

A markdown file with a `## Summary of All Changes` section containing a settings table, plus an optional `## Filament Tab Settings` section:

```markdown
## Summary of All Changes

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| Strength | Wall loops | 3 | 2 | fewer walls = more flex |
| Strength | Sparse infill density | 15% | 10% | squishy toy |
| Speed | Outer wall | 200 mm/s | 25 mm/s | |

## Filament Tab Settings

| Setting | Value | Notes |
|---|---|---|
| Nozzle temperature | 230 | |
| Bed temperature | 35 | |
| Fan speed (general) | 20–30% | |
| Max volumetric speed | 6 mm³/s | |
```

Rows with a blank Value are skipped. Notes column is ignored by the script.

### Template and LLM prompt

| File | Purpose |
|---|---|
| `SETTINGS_TEMPLATE.md` | Blank template — copy and fill in by hand |
| `llm-settings-prompt.md` | Paste into an LLM with your part description to generate a filled template |

### Settings key map

`make_bambu_3mf.py` contains a `SETTING_KEY_MAP` near the top that maps human-readable names to Bambu config JSON keys. It covers common quality, strength, speed, acceleration, and filament settings.

To add a setting not in the map: add an entry with the human name, the JSON key (from a `.3mf`'s `Metadata/project_settings.config`), and the value type (`"string"`, `"array"`, or `"integer"`).

---

## How it works

Both tools read or build a `.3mf` (a zip archive), locate `Metadata/project_settings.config` (JSON) and `Metadata/model_settings.config` (XML), patch them with per-plate process settings via `SETTING_KEY_MAP`, and repack the zip. `stl_to_bambu_3mf.py` additionally builds the `3D/3dmodel.model` geometry from STL binary data.

---

## Limitations

- Tested with Bambu A1 Mini profiles. Other printers may use different JSON keys or array lengths.
- `stl_to_bambu_3mf.py` does not auto-orient objects — they import in STL orientation. Adjust in Bambu Studio if needed.
- Settings not in `SETTING_KEY_MAP` (e.g. some exotic per-printer options) must be set manually in Bambu Studio after import.

## License

MIT — see [LICENSE](LICENSE)
