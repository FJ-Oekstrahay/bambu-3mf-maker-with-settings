# Task: build `stl_to_bambu_3mf.py` — a reusable STL-and-settings → Bambu .3mf generator

You are building a single-purpose, reusable Python tool for Geoff (A1 mini owner). It ingests
**one material's STL file(s)** plus **one settings markdown** and emits **one Bambu Studio .3mf**
that loads and slices correctly. Single material, single plate. No multi-plate / per-plate-material
logic — Geoff runs the tool once per material and gets one file each time.

Work in: `/Users/moltyjoe/.openclaw/workspace/projects/bambu/`

## Why this design (read before coding)

A `.3mf` is an OPC package — a ZIP containing:
- `3D/3dmodel.model` (+ `3D/Objects/object_N.model`) — mesh geometry, build/placement
- `Metadata/project_settings.config` — JSON: ALL print/filament/printer settings (temps, speeds, walls)
- `Metadata/model_settings.config` — XML: object names, plate assignment, per-object overrides
- `[Content_Types].xml`, `_rels/.rels`, thumbnails

Temperature is a **filament** setting; speeds/walls/elefant-foot are **process** settings. For a single
material this is simple: everything goes into the one global `project_settings.config`. No conflicts,
no per-object overrides needed. That is why single-material-per-file is the reliable approach (a prior
investigation confirmed Bambu has no clean per-plate material container, and that the earlier
multi-plate attempt's `process_settings_N.config` files are dead — Bambu never reads them).

## Architecture — reuse the known-good scaffold; only swap geometry + settings

Do NOT generate Bambu's scaffolding from scratch (content types, rels, the 559-key
`project_settings.config` baseline are fiddly and printer-specific). Instead use an existing
**template .3mf** as the scaffold and replace only what changes:

- Template (default): `QAV-S_2_Bardwell_-_O4_Pro_Insert_Left.3mf` — a valid A1 mini, 0.4 nozzle,
  Bambu Studio 02.07.00.55 project. Make `--template` a CLI arg defaulting to this file.
- From the template, **copy verbatim**: `[Content_Types].xml`, `_rels/.rels`,
  `Metadata/slice_info.config`. Preserve each member's original zip compression method
  (PNGs STORED, configs DEFLATED) — match `make_bambu_3mf.py`'s compression-preservation logic.
- **Replace** `Metadata/project_settings.config` with the template's baseline JSON **after applying
  the settings markdown** (see Settings engine below).
- **Regenerate** geometry (`3D/3dmodel.model` + `3D/Objects/object_N.model`) from the input STLs.
- **Regenerate** `Metadata/model_settings.config` for the new objects + a single named plate.
- **Drop** the template's thumbnails / `plate_*.png` / `plate_*.json` — Bambu regenerates thumbnails
  on load. (Leaving stale thumbnails of the wrong parts is worse than none.) Remove the thumbnail
  `<Relationship>` entries from `_rels/.rels` if you keep that file, OR keep rels minimal pointing
  only at `/3D/3dmodel.model`. Verify the rels you ship don't reference files you didn't include.

## Reuse the settings engine — do not rewrite it

`make_bambu_3mf.py` in this directory already has a debugged settings engine. Import and reuse:
- `SETTING_KEY_MAP` (human-name → (json_key, type) lookup)
- `parse_settings_markdown(md_path)` — parses the `## Summary of All Changes` table
- `apply_settings(settings, md_rows, material, source_settings)` — applies ⚠️ rows, skips forbidden
  keys, returns (modified_dict, report_rows)
- `coerce_value`, `is_forbidden_key`, `FORBIDDEN_KEY_FRAGMENTS`

Import them (`from make_bambu_3mf import ...`) rather than copy-pasting, so there's one source of truth.
If any are not cleanly importable (e.g. module side effects), refactor minimally — don't fork the logic.

The settings markdowns to test against:
- `bambu_a1_mini_PETGCF_QAV-S2_O4Pro_Mounts.md`  (PETG-CF: outer wall 80, nozzle 265)
- `bambu_a1_mini_TPU95A_QAV-S2_O4Pro.md`          (TPU 95A: outer wall 30, nozzle 230)

Note on temperature: in the template, `nozzle_temperature` etc. are 6-element per-filament arrays.
For single material, the objects all use filament slot 1 (`extruder=1` in model_settings.config).
Apply the spec temperature to the slot(s) the objects actually use. The existing `coerce_value`
already repeats a scalar across all array slots — that's fine and safe for single material.

## STL parsing (no new dependencies)

`numpy` is available; `trimesh`/`numpy-stl`/`lib3mf` are NOT. The STLs are **binary**. Parse them
directly: 80-byte header, uint32 triangle count, then per triangle 12 floats (normal + 3 verts) + 2-byte
attribute. Build an indexed mesh for 3MF: dedupe vertices (round to ~1e-5 to merge shared verts, or use
`numpy.unique` on the Nx3 vertex array with `return_inverse`) and emit `<vertices>` + `<triangles>`.

Cross-check while developing: the 4 sample STLs have triangle counts 3142 / 3142 / 9338 / 9302,
matching the template's `mesh_stat face_count` values — use that to sanity-check your parser.

## Geometry / placement

- One `<object>` per STL. Object id / naming: follow Bambu's pattern (the template uses object ids
  2,4,6,8 referencing component models object_1..4; you can use a simpler scheme — each top-level
  object directly containing a mesh — as long as ids are unique and `model_settings.config` matches).
  Simpler is fine: a single mesh object per STL, no `<components>` indirection, is valid 3MF.
- Translate each mesh so it rests on the bed (min Z = 0) and lay objects out without overlap. A1 mini
  bed is 180×180 mm. Simple auto-arrange: compute each mesh XY bounding box, place left-to-right
  (and wrap to a second row if needed) with a ~5 mm gap, roughly centered on the bed. Geoff can
  rearrange in Bambu; just don't stack them on top of each other.
- The tool does NOT auto-orient/auto-rotate (that's a Bambu feature). Objects import in STL
  orientation. Note this in `--help` / a comment so Geoff knows to orient in Bambu if needed.
- Object name in `model_settings.config` = STL filename (basename). The build `<item>` per object
  with an identity-rotation transform `1 0 0 0 1 0 0 0 1 tx ty tz` placing it at its bed position.

## model_settings.config

XML `<config>` with, for each object: an `<object id="N">` carrying
`<metadata key="name" value="<stl filename>"/>`, `<metadata key="extruder" value="1"/>`, and the
mesh part metadata (mirror the template's structure closely enough that Bambu accepts it).
Then ONE `<plate>` element:
- `<metadata key="plater_id" value="1"/>`
- `<metadata key="plater_name" value="<descriptive name>"/>` — **must mention the material**, e.g.
  `"Mounts — PETG-CF"`. Make `--plate-name` a CLI arg; default to `f"{material}"` or
  `f"{stem} — {material}"`.
- a `<model_instance>` per object mapping `object_id` → that plate (instance_id 0, identify_id any
  stable unique value).

## CLI

```
python stl_to_bambu_3mf.py \
  --stl path/a.stl --stl path/b.stl \
  --settings bambu_a1_mini_PETGCF_QAV-S2_O4Pro_Mounts.md \
  --material "PETG-CF" \
  --plate-name "Mounts — PETG-CF" \
  --output QAV-S2_O4Pro_Mounts_PETG-CF.3mf
```
`--stl` repeatable (also accept comma-separated). `--template` optional (default as above).
`--plate-name` optional. `--material` required (used for settings + naming).

## Deliverables — produce BOTH demo files

The 4 sample STLs are extracted in `./stl/`:
- `stl/QAV-S_2_Bardwell_-_O4_Pro_Mount_Left.stl`, `..._Mount_Right.stl`   → PETG-CF
- `stl/QAV-S_2_Bardwell_-_O4_Pro_Insert_Left.stl`, `..._Insert_Right.stl` → TPU 95A

Generate:
1. `QAV-S2_O4Pro_Mounts_PETG-CF.3mf`  — 2 Mount STLs, PETG-CF settings, plate name mentioning PETG-CF
2. `QAV-S2_O4Pro_Inserts_TPU95A.3mf`  — 2 Insert STLs, TPU 95A settings, plate name mentioning TPU 95A

## Verification (structural — you CANNOT open Bambu Studio; say so)

Write `stl_to_3mf_verification.txt`. For each output:
- valid zip; opens with `zipfile`
- `project_settings.config` is a JSON **dict** (not array — array triggers Bambu "geometry only" reject)
- spec values landed: PETG-CF → `outer_wall_speed` 80, `nozzle_temperature` 265, `elefant_foot_compensation`
  0.1, `reduce_crossing_wall` 1; TPU → `outer_wall_speed` 30, `nozzle_temperature` 230, same elefant/crossing
- `model_settings.config` is valid XML, one `<plate>`, `plater_name` contains the material string,
  one `<model_instance>` per input STL with matching object_ids
- `3dmodel.model` parses as XML, object/vertex/triangle counts > 0 and triangle counts match source STLs
- no dangling files referenced by `_rels/.rels` that aren't in the archive

Then **state explicitly** that final validation requires Geoff loading each file in Bambu Studio — the
script only checks structure, not slicer acceptance. Do not claim the files print correctly.

## Constraints

- Keep `make_bambu_3mf.py` working (you're importing from it) — don't break its CLI.
- Match the template's per-file zip compression methods in output.
- Don't touch any `machine_*`, `printer_*`, gcode, or other hardware keys (the existing
  `FORBIDDEN_KEY_FRAGMENTS` guard already covers this — keep using it).

## Return format

Return only: files touched (one-line summary each) and the verification result (pass/fail + the key
values checked per output file). No diffs, no code blocks, no file contents.
If you commit, end the commit message with:
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
