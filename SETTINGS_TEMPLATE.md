# Bambu A1 Mini — Print Settings Template

<!--
INSTRUCTIONS FOR LLM:
Fill in the Value column in the Summary table for every setting that differs from
Bambu defaults. Leave Value blank (or delete the row) for settings you want at default.
Fill in the Filament Tab section for the material being used.
Setting names are fixed — do not rename them.

INSTRUCTIONS FOR RUNNING THE SCRIPT:
  python3 stl_to_bambu_3mf.py \
    --stl your_file.stl \
    --settings this_file.md \
    --material "TPU 95A" \
    --plate-name "My Part — TPU 95A"
Output .3mf defaults to same directory as the STL. Override with --output path.
-->

## Summary of All Changes

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| Quality | Elephant foot compensation | 0 mm | | e.g. 0.1 — compensates for first-layer squish |
| Quality | Bridge flow | 1.0 | | e.g. 0.9 — reduce for cleaner bridges |
| Quality | Avoid crossing wall | ☑ | | ☑ or ☐ — prevents stringing on multi-copy plates |
| Strength | Wall loops | 3 | | number of perimeter walls |
| Strength | Sparse infill density | 15% | | e.g. 10% for flexible/squishy parts |
| Strength | Sparse infill pattern | grid | | e.g. gyroid (best for flexible parts), honeycomb, etc. |
| Strength | Top shell layers | 5 | | |
| Strength | Bottom shell layers | 4 | | |
| Speed | Outer wall | 200 mm/s | | |
| Speed | Inner wall | 250 mm/s | | |
| Speed | Top surface | 100 mm/s | | |
| Speed | Bridge | 150 mm/s | | |
| Speed | Sparse infill | 300 mm/s | | |
| Speed | Internal solid infill | 250 mm/s | | |
| Speed | Gap infill | 100 mm/s | | |
| Speed | Initial layer infill | 60 mm/s | | |
| Acceleration | Normal printing | 5000 mm/s² | | |
| Acceleration | Outer wall accel | 2000 mm/s² | | |
| Acceleration | Top surface accel | 2000 mm/s² | | |
| Acceleration | Initial layer | 500 mm/s² | | |
| Others | Skirt loops | 2 | | |
| Others | Enable prime tower | ☐ | | ☑ or ☐ |

## Filament Tab Settings

| Setting | Value | Notes |
|---|---|---|
| Nozzle temperature | | e.g. 230 for TPU, 265 for PETG-CF |
| Bed temperature | | e.g. 35 for TPU, 70 for PETG-CF |
| Fan speed (general) | | e.g. 30% or 20–50% range |
| Max volumetric speed | | e.g. 6 mm³/s (lower = better surface quality) |
