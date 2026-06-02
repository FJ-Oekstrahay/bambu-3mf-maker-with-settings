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

Fill in **every Value cell** in the template below. For each setting:
- If it should differ from the Bambu default, give a specific value.
- If the Bambu default is appropriate for this part and material, write **default** in the Value column.
- Never leave a Value cell blank — a blank tells the script to skip the setting, which is different from explicitly keeping the default.

Rules:
- Setting names are fixed — do not rename them.
- Values must match the format shown in the Notes column (mm, %, mm/s, mm/s², °C, ☑/☐).
- For ranges (e.g. fan speed) write the range: `20–30%`.
- After the tables, write a section called "Key Trade-offs" with 4–6 sentences explaining your most important choices — especially anything that deviates significantly from the typical default for this material, and why.
- Do not add settings not in the template.
- The Summary of All Changes table at the end must list every setting you changed from default. Leave out settings where you wrote "default". The script only reads this summary table — it is the machine-readable output.

Output the entire completed markdown, ready to save as a `.md` file and pass directly to `stl_to_bambu_3mf.py`.

---

## Settings Template

# [Part Name] — [Material] Print Settings
## Bambu A1 Mini · Bambu Studio 2.7.x

---

## Quality Tab

### Layer Height

| Setting | Value | Notes |
|---|---|---|
| Layer height | | e.g. 0.2 mm standard; 0.12 fine detail; 0.28 for speed |
| Initial layer height | | e.g. 0.2 mm; match layer height for flexible materials |

### Line Width

| Setting | Value |
|---|---|
| Default | |
| Initial layer | |
| Outer wall | |
| Inner wall | |
| Top surface | |
| Sparse infill | |
| Internal solid infill | |
| Support | |

### Seam

| Setting | Value | Notes |
|---|---|---|
| Seam position | | Aligned / Nearest / Random / Back |
| Smart scarf seam | | ☑ or ☐ |
| Scarf application angle threshold | | e.g. 155° |
| Scarf joint for inner walls | | ☑ or ☐ |

### Precision

| Setting | Value | Notes |
|---|---|---|
| Elephant foot compensation | | e.g. 0.1 mm for TPU or soft first layers |
| Slice gap closing radius | | default 0.049 mm |
| Resolution | | default 0.012 mm |
| Arc fitting | | ☑ or ☐ |
| X-Y hole compensation | | e.g. 0 mm if no precision holes |

### Ironing

| Setting | Value | Notes |
|---|---|---|
| Ironing type | | No ironing / All top surfaces / Topmost only |

### Advanced (Quality)

| Setting | Value | Notes |
|---|---|---|
| Order of walls | | inner/outer or outer/inner |
| Bridge flow | | e.g. 0.9 — reduce for cleaner bridges |
| Avoid crossing wall | | ☑ or ☐ |
| Print infill first | | ☑ or ☐ |

---

## Strength Tab

### Walls

| Setting | Value | Notes |
|---|---|---|
| Wall loops | | e.g. 2 toys/flex; 3–4 general; 5+ structural |
| Detect thin wall | | ☑ or ☐ |

### Top/Bottom Shells

| Setting | Value | Notes |
|---|---|---|
| Top shell layers | | e.g. 4–5 typical |
| Top shell thickness | | |
| Bottom shell layers | | e.g. 3–4 typical |
| Bottom shell thickness | | |
| Top surface pattern | | Monotonic / Hilbert / Archimedean / Concentric |
| Bottom surface pattern | | Monotonic / Hilbert / Archimedean / Concentric |

### Sparse Infill

| Setting | Value | Notes |
|---|---|---|
| Sparse infill density | | e.g. 10% flex toys; 15–20% general; 40%+ structural |
| Sparse infill pattern | | grid / gyroid / honeycomb / lightning / etc. (use lowercase enum values) |
| Length of sparse infill anchor | | default 400% |

---

## Speed Tab

### Initial Layer Speed

| Setting | Value | Notes |
|---|---|---|
| Initial layer | | e.g. 15–20 mm/s; lower for TPU |
| Initial layer infill | | e.g. 25–30 mm/s |

### Other Layer Speeds

| Setting | Value | Notes |
|---|---|---|
| Outer wall | | e.g. 100–200 mm/s typical |
| Inner wall | | e.g. 150–250 mm/s |
| Small perimeters | | e.g. 50% (relative) |
| Sparse infill | | e.g. 200–300 mm/s |
| Internal solid infill | | e.g. 150–250 mm/s |
| Top surface | | e.g. 80–100 mm/s |
| Bridge | | e.g. 100–150 mm/s |
| Gap infill | | e.g. 80–100 mm/s |

### Travel Speed

| Setting | Value |
|---|---|
| Travel | |

### Acceleration

| Setting | Value | Notes |
|---|---|---|
| Normal printing | | e.g. 2000–5000 mm/s² |
| Travel | | e.g. 5000–10000 mm/s² |
| Initial layer | | e.g. 300–500 mm/s² |
| Outer wall | | e.g. 1000–2000 mm/s² |
| Top surface | | e.g. 1000–2000 mm/s² |
| Inner wall | | 0 for auto |
| Initial layer travel | | e.g. 1500–2000 mm/s² |

---

## Support Tab

| Setting | Value | Notes |
|---|---|---|
| Enable support | | ☑ or ☐ |
| Support type | | Normal / Tree |
| Threshold angle | | e.g. 40–55° |
| Support on build plate only | | ☑ or ☐ |

### Raft

| Setting | Value |
|---|---|
| Raft layers | |

---

## Others Tab

### Bed Adhesion

| Setting | Value | Notes |
|---|---|---|
| Skirt loops | | e.g. 2 general; 3+ for TPU flow priming |
| Skirt height | | e.g. 1 layer |
| Brim type | | None / Auto / Outer / Inner (stored as: no_brim / auto_brim / outer_only / inner_only) |
| Brim width | | e.g. 5 mm |
| Brim-object gap | | e.g. 0.1 mm |

### Prime Tower

| Setting | Value |
|---|---|
| Enable prime tower | |

### Special Mode

| Setting | Value | Notes |
|---|---|---|
| Print sequence | | By layer / By object |
| Slicing mode | | Regular / Even-odd |
| Spiral vase | | ☑ or ☐ |
| Fuzzy skin | | None / Contour / All walls |

---

## Filament Tab Settings

*(Set in the filament profile, not the process profile)*

| Setting | Value | Notes |
|---|---|---|
| Nozzle temperature | | e.g. 220 PLA / 230 TPU / 265 PETG-CF |
| Bed temperature | | e.g. 55 PLA / 35 TPU / 70 PETG-CF |
| Retraction distance | | e.g. 0.8 mm direct drive; max 1.0 mm for TPU |
| Retraction speed | | e.g. 25–40 mm/s |
| Max volumetric speed | | e.g. 6–8 mm³/s; lower = better surface quality |
| Wipe on layer change | | ☑ or ☐ |
| Fan speed (general) | | e.g. 30–70%; lower for TPU layer bonding |
| Fan speed (first layer) | | e.g. 0% — never cool first layer |
| Slow down if layer time < | | e.g. 8 s |
| Min print speed | | e.g. 10 mm/s |

---

## Key Trade-offs

[LLM fills in here]

---

## Summary of All Changes

*(Script reads this table. Include every setting that differs from the Bambu default. Omit settings left at default.)*

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| | | | | |
