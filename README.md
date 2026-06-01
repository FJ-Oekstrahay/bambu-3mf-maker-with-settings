# bambu-3mf-maker-with-settings

A Python CLI tool that builds multi-plate Bambu Studio `.3mf` files with full per-material process settings applied programmatically. Useful when you need precise control over settings (temperature, speeds, wall counts, etc.) that Bambu Studio's UI doesn't easily script — for example, generating print-ready files for different materials on separate plates in a single automated step.

## Requirements

- Python 3.8+
- Standard library only — no `pip install` needed

## Usage

Basic pattern:

```
python make_bambu_3mf.py \
  --source input.3mf \
  --plate <N> --material "<name>" --objects <id,id,...> --settings <file.md> \
  --output output.3mf
```

**Arguments:**

| Argument | Description |
|---|---|
| `--source` | Source `.3mf` file to use as template |
| `--output` | Output `.3mf` file path |
| `--plate N` | Plate number (repeatable) |
| `--material` | Material name for this plate (label only) |
| `--objects` | Comma-separated object IDs to assign to this plate |
| `--settings` | Markdown file containing the settings table for this plate |

**Single plate:**

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

The `--settings` file is a markdown document with a "Summary of All Changes" section containing a table of settings to apply. Each row maps a human-readable setting name to a new value.

## How it works

The script reads the source `.3mf` (which is a zip archive), locates `Metadata/project_settings.config` (JSON) and `Metadata/model_settings.config` (XML), patches them with per-plate process settings using a `SETTING_KEY_MAP` lookup table, and repacks the zip preserving per-file compression methods. Per-plate `process_settings_N.config` files are written for each plate. The `3D/3dmodel.model` geometry file is copied byte-for-byte from the source.

## Settings key map

The script contains a `SETTING_KEY_MAP` dict near the top that maps human-readable setting names (e.g. `"Nozzle temperature"`) to their Bambu config JSON keys (e.g. `"nozzle_temperature"`). The map covers common quality, strength, speed, acceleration, and temperature settings.

To add support for a setting not already in the map, add an entry to `SETTING_KEY_MAP` with the human name, the JSON key (from a Bambu `.3mf` `project_settings.config`), and the value type (`"string"`, `"array"`, or `"integer"`).

## Limitations

- Only tested with Bambu X1C and P1S profiles. Other printers may use different JSON keys or array lengths.
- The key map covers common settings. Exotic or printer-specific settings may need additions to `SETTING_KEY_MAP`.
- Object IDs must match those present in the source `.3mf` — check `Metadata/model_settings.config` in the source file if you're unsure what IDs to use.

## License

MIT — see [LICENSE](LICENSE)
