# Handoff Prompt: Bambu Script Expansions

Five improvements ranked by value. Implement in order; each is independent.

## 1. Material presets

Create `presets/` directory under `bambu/`. Add known-good baseline settings files:
- `presets/tpu95a.md` — TPU 95A: temps, speeds, brim, wall counts, slow outer wall, gyroid infill
- `presets/petgcf.md` — PETG-CF: temps, speeds, fan, support settings
- `presets/pla.md` — PLA: temps, speeds, defaults

Add `--preset <name>` flag to both `make_bambu_3mf.py` and `3mf_restamp.py`. When specified, load the preset as the base settings, then apply any additional `--settings` overrides on top. Preset overrides are lower priority than explicit `--settings` input.

## 2. Settings diff output

When `3mf_restamp.py` runs, after applying settings, compare the new `project_settings.config` against the source config and print a table of what actually changed (key, old value, new value). Currently only shows what was requested — this shows what actually landed.

Add `--diff` flag to opt in (or enable by default and add `--no-diff` to suppress).

## 3. Validation layer

Add a `validate_settings(settings_dict)` function in `make_bambu_3mf.py` that warns (not errors) on physically inconsistent combinations:
- `sparse_infill_density == 0` AND `wall_loops <= 1` → warn "hollow shell with only 1 wall loop will be fragile"
- `support_on_build_plate_only` enabled but no overhangs heuristic (skip if can't detect)
- speed > 200 mm/s for TPU material → warn "TPU above 200 mm/s will likely fail"

Call it at the end of settings application in both scripts. Warnings go to stderr.

## 4. Slice preview via Bambu Studio CLI

Bambu Studio ships a headless slicer CLI (`bambu-studio --slice`). After stamping a 3mf, optionally invoke it to get layer count, estimated print time, and filament usage without opening the GUI.

Add `--slice-preview` flag to `3mf_restamp.py`. When set, run the CLI and print the summary. Find the CLI binary at `/Applications/Bambu Studio.app/Contents/MacOS/bambu-studio` — verify it exists before wiring up.

## 5. Fuzzy key matching for unrecognized settings

In `apply_settings()` in `make_bambu_3mf.py`, when a setting name doesn't match the key map AND the fallback normalization also fails to find a key in the config, use `difflib.get_close_matches()` to suggest the 2-3 closest known keys from SETTING_KEY_MAP and from the actual config keys. Print suggestion as a warning to stderr.

Currently these silently skip — a fuzzy suggestion would catch typos and near-misses.

---

Reference files:
- `make_bambu_3mf.py` — main script, SETTING_KEY_MAP, apply_settings
- `3mf_restamp.py` — restamp script, already handles Metadata/ config path
- `SETTINGS_TEMPLATE.md` — LLM settings template
- `llm-settings-prompt.md` — LLM prompt for generating settings
