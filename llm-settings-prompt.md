# LLM Prompt: Generate Bambu Print Settings

Copy everything below the line and paste it into Claude, ChatGPT, or another LLM.
Fill in the YOUR PART section before sending.

---

I need Bambu Studio print settings for a specific part. I'll give you the part details and you fill in the settings template below.

## Your Part

<!-- FILL IN BEFORE SENDING -->
- **STL file / part name:**
- **Material:** (e.g. TPU 95A, PETG-CF, PLA, ABS)
- **Printer:** Bambu A1 Mini, 0.4 mm nozzle
- **What the part is / does:**
- **Key requirements:** (e.g. flexible, strong, heat-resistant, cosmetic surface, tight tolerances, needs supports)
- **Any other context:** (e.g. wall thickness, functional vs display, post-processing)

---

## Instructions

Fill in the **Value** column for every setting that differs meaningfully from the Bambu default.
Leave the Value blank for any setting that should stay at default — don't guess at settings you're not changing.

Rules:
- Setting names in the table are fixed — do not rename them.
- Values must match the format shown in the Notes column (mm, %, mm/s, mm/s², °C, ☑/☐).
- If you recommend a value that's a range (e.g. fan speed), write the range: `20–30%`.
- After the table, write a short paragraph (3–5 sentences) explaining the key trade-offs in your choices — especially any setting where you're deviating significantly from the typical default for this material.
- Do not invent settings not in the template.

Output the completed markdown below, ready to save as a `.md` file and pass directly to `stl_to_bambu_3mf.py`.

---

## Settings Template

```markdown
# [Part Name] — [Material] Print Settings
## Bambu A1 Mini · Bambu Studio 2.7.x

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
```
