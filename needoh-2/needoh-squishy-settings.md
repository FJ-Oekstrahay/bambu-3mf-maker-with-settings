# Needoh Squishy Cube — TPU 95A Print Settings
## Bambu A1 Mini · Bambu Studio 2.7.x

---

## Quality Tab

### Layer Height

| Setting | Value | Notes |
|---|---|---|
| Layer height | 0.2 mm | Standard; fine enough detail without slowing print |
| Initial layer height | 0.2 mm | Match layer height for TPU — no squish on first layer |

### Line Width

| Setting | Value |
|---|---|
| Default | 0.42 mm |
| Initial layer | 0.42 mm |
| Outer wall | 0.42 mm |
| Inner wall | 0.42 mm |
| Top surface | 0.42 mm |
| Sparse infill | 0.42 mm |
| Internal solid infill | 0.42 mm |
| Support | 0.42 mm |

### Seam

| Setting | Value | Notes |
|---|---|---|
| Seam position | Nearest | Minimizes travel moves; fine for a squishy toy |
| Smart scarf seam | ☐ | Not needed for this geometry |
| Scarf application angle threshold | 155° | Default |
| Scarf joint for inner walls | ☐ | Not needed |

### Precision

| Setting | Value | Notes |
|---|---|---|
| Elephant foot compensation | 0.1 mm | TPU squishes on first layer — compensation improves base geometry |
| Slice gap closing radius | 0.049 mm | Default |
| Resolution | 0.012 mm | Default |
| Arc fitting | ☑ | Smoother curves on rounded faces |
| X-Y hole compensation | 0 mm | No precision holes in this model |

### Ironing

| Setting | Value | Notes |
|---|---|---|
| Ironing type | No ironing | Not applicable for a squishy TPU toy |

### Advanced (Quality)

| Setting | Value | Notes |
|---|---|---|
| Order of walls | inner/outer | Better dimensional accuracy on outer surface |
| Bridge flow | 0.9 | Slightly reduced for cleaner bridging |
| Avoid crossing wall | ☑ | Critical for TPU — prevents stringing across perimeters |
| Print infill first | ☐ | Default; walls after infill is unnecessary here |

---

## Strength Tab

### Walls

| Setting | Value | Notes |
|---|---|---|
| Wall loops | 3 | With 0% infill, walls are the only structure — 3 loops (1.26mm) gives flex without collapse |
| Detect thin wall | ☐ | No thin features expected in this geometry |

### Top/Bottom Shells

| Setting | Value | Notes |
|---|---|---|
| Top shell layers | 3 | Thinner cap allows more compression at top |
| Top shell thickness | 0.6 mm | Matches 3 layers at 0.2 mm |
| Bottom shell layers | 2 | Thinner base for more flex at bottom |
| Bottom shell thickness | 0.4 mm | Matches 2 layers at 0.2 mm |
| Top surface pattern | Concentric | Works well with TPU; avoids long straight passes |
| Bottom surface pattern | Monotonic | Solid, even coverage on build plate side |

### Sparse Infill

| Setting | Value | Notes |
|---|---|---|
| Sparse infill density | 0% | Hollow interior — only wall perimeters print, no interior lattice |
| Sparse infill pattern | Gyroid | Retained as default; not used at 0% density |
| Length of sparse infill anchor | 400% | Default |

---

## Speed Tab

### Initial Layer Speed

| Setting | Value | Notes |
|---|---|---|
| Initial layer | 20 mm/s | Slower for better TPU bed adhesion |
| Initial layer infill | 25 mm/s | Slightly faster than perimeters is fine |

### Other Layer Speeds

| Setting | Value | Notes |
|---|---|---|
| Outer wall | 40 mm/s | TPU quality degrades fast above 40 mm/s |
| Inner wall | 60 mm/s | Can run a bit faster than outer |
| Small perimeters | 50% | Relative; slows automatically on tight curves |
| Sparse infill | 80 mm/s | Low-density gyroid at 8% — fast is fine |
| Internal solid infill | 60 mm/s | Shell infill; controlled speed for surface quality |
| Top surface | 40 mm/s | Match outer wall for clean top layers |
| Bridge | 50 mm/s | Conservative for TPU bridge stability |
| Gap infill | 40 mm/s | Slow and controlled for gap fill quality |

### Travel Speed

| Setting | Value |
|---|---|
| Travel | 150 mm/s |

### Acceleration

| Setting | Value | Notes |
|---|---|---|
| Normal printing | 2000 mm/s² | Conservative for TPU — reduces vibration artifacts |
| Travel | 5000 mm/s² | Default; travel doesn't affect print quality |
| Initial layer | 300 mm/s² | Low for first layer adhesion |
| Outer wall | 1000 mm/s² | Smooth outer surface |
| Top surface | 1000 mm/s² | Smooth top layers |
| Inner wall | 0 | Auto |
| Initial layer travel | 1500 mm/s² | Moderate for first layer travel moves |

---

## Support Tab

| Setting | Value | Notes |
|---|---|---|
| Enable support | ☐ | Cube geometry needs no support |
| Support type | Normal | N/A |
| Threshold angle | 40° | N/A — support disabled |
| Support on build plate only | ☑ | Default; irrelevant since support is off |

### Raft

| Setting | Value |
|---|---|
| Raft layers | 0 |

---

## Others Tab

### Bed Adhesion

| Setting | Value | Notes |
|---|---|---|
| Skirt loops | 3 | Extra loops to prime TPU flow before print starts |
| Skirt height | 1 | One layer is sufficient for priming |
| Brim type | Outer | TPU needs adhesion help; outer brim on all edges |
| Brim width | 8 mm | Wide brim — TPU lifts easily, especially at corners |
| Brim-object gap | 0.1 mm | Small gap makes brim removal easier |

### Prime Tower

| Setting | Value |
|---|---|
| Enable prime tower | ☐ |

### Special Mode

| Setting | Value | Notes |
|---|---|---|
| Print sequence | By layer | Default; single object so no difference |
| Slicing mode | Regular | Default |
| Spiral vase | ☐ | Not applicable |
| Fuzzy skin | None | Clean surface; fuzzy skin would reduce squish feel |

---

## Filament Tab Settings

*(Set in the filament profile, not the process profile)*

| Setting | Value | Notes |
|---|---|---|
| Nozzle temperature | 230°C | Mid-range for Bambu TPU 95A |
| Bed temperature | 35°C | Low temp for TPU — too hot causes adhesion problems |
| Retraction distance | 0.8 mm | Direct drive; conservative for TPU |
| Retraction speed | 25 mm/s | Slow retraction reduces TPU deformation |
| Max volumetric speed | 6 mm³/s | Conservative cap for surface quality |
| Wipe on layer change | ☑ | Reduces ooze between layers |
| Fan speed (general) | 40% | Moderate cooling; too much reduces layer bonding |
| Fan speed (first layer) | 0% | Never cool first layer |
| Slow down if layer time < | 8 s | Allow adequate cooling on small cross-sections |
| Min print speed | 10 mm/s | Floor to prevent stalling |

---

## Summary of All Changes

*(Settings that differ from Bambu A1 Mini TPU 95A defaults)*

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| Filament | Nozzle temperature | 220 | 230 | TPU requires higher nozzle temp |
| Filament | Bed temperature | 45 | 35 | Lower bed temp for TPU adhesion control |
| Strength | Sparse infill density | 15% | 0% | Hollow interior — no internal lattice, just wall perimeters |
| Strength | Sparse infill pattern | Grid | gyroid | Retained; no effect at 0% density |
| Strength | Wall loops | 2 | 3 | Walls are the only structure at 0% infill — 3 loops = 1.26mm |
| Strength | Top shell layers | 5 | 3 | Thinner cap = more flex at top |
| Strength | Bottom shell layers | 3 | 2 | Thinner base = more flex at bottom |
| Quality | Elephant foot compensation | 0 mm | 0.1 mm | TPU squishes on first layer |
| Quality | Avoid crossing wall | ☐ | ☑ | Prevents TPU stringing |
| Speed | Outer wall | ~150 mm/s | 40 mm/s | TPU quality degrades fast above 40 |
| Speed | Inner wall | ~200 mm/s | 60 mm/s | TPU quality |
| Speed | Initial layer speed | ~30 mm/s | 20 mm/s | Better bed adhesion |
| Others | Brim type | None | outer_only | TPU needs adhesion help |
| Others | Brim width | 5 mm | 8 mm | TPU lifts easily |
| Others | Skirt loops | 2 | 3 | Extra priming for TPU flow |
