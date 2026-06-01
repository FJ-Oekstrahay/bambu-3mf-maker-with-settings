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
| Sparse infill pattern | | Grid / Gyroid / Honeycomb / Lightning / etc. |
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
| Brim type | | None / Auto / Outer / Inner |
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

## Summary of All Changes

*(Fill this in after completing the per-tab sections above. One row per setting that differs from the Bambu default. This is the section the script reads.)*

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| | | | | |
