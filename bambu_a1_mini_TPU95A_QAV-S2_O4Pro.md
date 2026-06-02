# Bambu A1 Mini — Advanced Mode Print Settings
## Profile: TPU 95A — QAV-S 2 Bardwell O4 Pro Mounts & Inserts

> **Parts:** O4_Pro_Mount_Left, O4_Pro_Mount_Right, O4_Pro_Insert_Left, O4_Pro_Insert_Right
> **Material:** TPU 95A | **Plate:** All 4 parts on one plate, laid flat on widest face
> **Changes from default are highlighted with ⚠️**

---

## Quality Tab

### Layer Height

| Setting | Value | Unit |
|---|---|---|
| Layer height | 0.2 | mm |
| Initial layer height | 0.2 | mm |
| Mixed color sublayer | ☐ | — |

### Line Width

| Setting | Value | Unit |
|---|---|---|
| Default | 0.42 | mm |
| Initial layer | 0.5 | mm |
| Outer wall | 0.42 | mm |
| Inner wall | 0.45 | mm |
| Top surface | 0.42 | mm |
| Sparse infill | 0.45 | mm |
| Internal solid infill | 0.42 | mm |
| Support | 0.42 | mm |

### Seam

| Setting | Value |
|---|---|
| Seam position | Aligned |
| Seam placement away from overhangs (experimental) | ☐ |
| Smart scarf seam application | ☑ |
| Scarf application angle threshold | 155° |
| Scarf around entire wall | ☐ |
| Scarf steps | 10 |
| Scarf joint for inner walls | ☑ |
| Override filament scarf seam setting | ☐ |
| Role-based wipe speed | ☑ |

### Precision

| Setting | Value | Unit |
|---|---|---|
| Slice gap closing radius | 0.049 | mm |
| Resolution | 0.012 | mm |
| Arc fitting | ☑ | — |
| X-Y hole compensation | 0 | mm |
| X-Y contour compensation | 0 | mm |
| Auto circle contour-hole compensation | ☐ | — |
| Elephant foot compensation | 0.1 ⚠️ | mm |
| Precise Z height | ☐ | — |

> ⚠️ **Elephant foot compensation 0 → 0.1 mm:** TPU first layers tend to squish/spread slightly wider than rigid filaments. A small compensation keeps the mating faces accurate.

### Ironing

| Setting | Value |
|---|---|
| Ironing Type | No ironing |

### Wall Generator

| Setting | Value |
|---|---|
| Wall generator | Classic |

### Advanced

| Setting | Value | Unit |
|---|---|---|
| Order of walls | inner/outer | — |
| Print infill first | ☐ | — |
| Bridge flow | 0.9 ⚠️ | — |
| Thick bridges | ☐ | — |
| Only one wall on top surfaces | Top surfaces | — |
| Only one wall on first layer | ☐ | — |
| Smooth speed discontinuity area | ☑ | — |
| Smooth coefficient | 80 | — |
| Avoid crossing wall | ☑ ⚠️ | — |
| Smoothing wall speed along Z (experimental) | ☐ | — |

> ⚠️ **Bridge flow 1.0 → 0.9:** Reduces sagging on any bridged spans in TPU.
> ⚠️ **Avoid crossing wall ☐ → ☑:** Keeps the nozzle from dragging across open areas and stringing across the plate between the 4 parts.

---

## Strength Tab

### Walls

| Setting | Value | Unit |
|---|---|---|
| Wall loops | 4 ⚠️ | — |
| Embedding the wall into the infill | ☐ | — |
| Detect thin wall | ☑ ⚠️ | — |

> ⚠️ **Wall loops 2 → 4:** These are structural drone parts under vibration and crash load. 4 walls gives the solid shell these need.
> ⚠️ **Detect thin wall ☐ → ☑:** The inserts are only 4.4 mm wide — thin wall detection ensures the slicer doesn't skip any geometry.

### Top/Bottom Shells

| Setting | Value | Unit |
|---|---|---|
| Top surface pattern | Monotonic | — |
| Top surface density | 100 | % |
| Top shell layers | 5 | — |
| Top shell thickness | 1 | mm |
| Top paint penetration layers | 5 | — |
| Bottom surface pattern | Monotonic | — |
| Bottom surface density | 100 | % |
| Bottom shell layers | 4 ⚠️ | — |
| Bottom shell thickness | 0 | mm |
| Bottom paint penetration layers | 3 | — |
| Internal solid infill pattern | Rectilinear | — |

> ⚠️ **Bottom shell layers 3 → 4:** Matches top shell count for symmetrical part strength.

### Sparse Infill

| Setting | Value | Unit |
|---|---|---|
| Sparse infill density | 45% ⚠️ | % |
| Fill multiline | 1 | — |
| Sparse infill pattern | gyroid ⚠️ | — |
| Length of sparse infill anchor | 400% | mm or % |
| Maximum length of sparse infill anchor | 20 | mm or % |

> ⚠️ **Infill density 15% → 45%:** Functional parts that will be compressed and flexed during installation and crashes. Don't go sparse here.
> ⚠️ **Pattern Grid → Gyroid:** Gyroid distributes stress omnidirectionally and handles the flex-fatigue cycling of TPU far better than grid.

### Advanced

| Setting | Value | Unit |
|---|---|---|
| Infill/Wall overlap | 15 | % |
| Infill direction | 45 | ° |
| Bridge direction | 0 | ° |
| Minimum sparse infill threshold | 15 | mm² |
| Infill combination | ☐ | — |
| Detect narrow internal solid infill | ☑ | — |
| Ensure vertical shell thickness | Enabled | — |
| Detect floating vertical shells | ☑ | — |

---

## Speed Tab

### Initial Layer Speed

| Setting | Value | Unit |
|---|---|---|
| Initial layer | 15 | mm/s |
| Initial layer infill | 30 mm/s ⚠️ | mm/s |

> ⚠️ **Initial layer infill 105 → 30 mm/s:** The default 105 mm/s is reckless for TPU on the first layer. Slow this down to match the initial layer speed intent.

### Other Layers Speed

| Setting | Value | Unit |
|---|---|---|
| Outer wall | 30 mm/s ⚠️ | mm/s |
| Inner wall | 35 mm/s ⚠️ | mm/s |
| Small perimeters | 50% | mm/s or % |
| Small perimeter threshold | 0 | mm |
| Sparse infill | 40 mm/s ⚠️ | mm/s |
| Internal solid infill | 35 mm/s ⚠️ | mm/s |
| Vertical shell speed | 80% | mm/s or % |
| Top surface | 25 mm/s ⚠️ | mm/s |
| Slow down for overhangs | ☑ | — |
| Overhang speed @ 10% | 0 | mm/s |
| Overhang speed @ 25% | 50 | mm/s |
| Overhang speed @ 50% | 30 | mm/s |
| Overhang speed @ 75% | 10 | mm/s |
| Overhang speed @ 100% | 10 | mm/s |
| Slow down by height | ☐ | — |
| Bridge | 25 mm/s ⚠️ | mm/s |
| Gap infill | 35 mm/s ⚠️ | mm/s |
| Support | 30 mm/s ⚠️ | mm/s |
| Support interface | 25 mm/s ⚠️ | mm/s |

> ⚠️ **All print speeds drastically reduced for TPU.** TPU 95A on a direct drive system like the A1 Mini should stay in the 25–40 mm/s range for extrusion moves. The default 200–300 mm/s profile will cause under-extrusion, stringing, and jams with flexible filament. These are the most critical changes in the entire profile.

### Travel Speed

| Setting | Value | Unit |
|---|---|---|
| Travel | 100 | mm/s |

> Travel speed is fine at 100 mm/s — no filament is being pushed, so the elasticity of TPU doesn't matter here.

### Acceleration

| Setting | Value | Unit |
|---|---|---|
| Normal printing | 1500 mm/s² ⚠️ | mm/s² |
| Travel | 5000 mm/s² ⚠️ | mm/s² |
| Initial layer travel | 2000 mm/s² ⚠️ | mm/s² |
| Initial layer | 300 mm/s² ⚠️ | mm/s² |
| Outer wall | 1000 mm/s² ⚠️ | mm/s² |
| Inner wall | 0 | mm/s² |
| Top surface | 500 mm/s² ⚠️ | mm/s² |
| Sparse infill | 100% | mm/s² or % |

> ⚠️ **Accelerations reduced across the board.** High acceleration with TPU causes the elastic filament path to "bounce," leading to ringing artifacts and inconsistent extrusion. Lower accel keeps the extruder force predictable.

---

## Support Tab

### Support

| Setting | Value |
|---|---|
| Enable support | ☐ |
| Type | tree (auto) |
| Style | Default |
| Threshold angle | 30° |
| On build plate only | ☐ |
| Remove small overhangs | ☑ |

> No supports needed if all parts are oriented flat on their widest face as recommended. Do not use supports with TPU unless absolutely necessary — they are extremely difficult to remove cleanly from flexible parts.

### Raft

| Setting | Value | Unit |
|---|---|---|
| Raft layers | 0 | layers |

### Filament for Supports

| Setting | Value |
|---|---|
| Support/raft base | Default |
| Support/raft interface | Default |

### Advanced

| Setting | Value | Unit |
|---|---|---|
| Initial layer density | 90 | % |
| Initial layer expansion | -1 | mm |
| Support wall loops | -1 | — |
| Top Z distance | 0.2 | mm |
| Bottom Z distance | 0.2 | mm |
| Base pattern | Default | — |
| Base pattern spacing | 2.5 | mm |
| Pattern angle | 0 | ° |
| Top interface layers | 2 | layers |
| Bottom interface layers | 2 | layers |
| Interface pattern | Default | — |
| Top interface spacing | 0.5 | mm |
| Normal support expansion | 0 | mm |
| Support/object XY distance | 0.35 | mm |
| Z overrides X/Y | ☐ | — |
| Support/object first layer gap | 0.2 | mm |
| Don't support bridges | ☐ | — |
| Independent support layer height | ☑ | — |

---

## Others Tab

### Bed Adhesion

| Setting | Value | Unit |
|---|---|---|
| Skirt loops | 2 ⚠️ | — |
| Skirt height | 1 | layers |
| Brim type | Auto | — |
| Brim width | 5 | mm |
| Brim-object gap | 0.1 | mm |

> ⚠️ **Skirt loops 0 → 2:** Add a skirt to prime the nozzle and verify TPU flow is clean before hitting your parts. TPU can be slow to get flowing consistently after a cold start.

### Prime Tower

| Setting | Value | Unit |
|---|---|---|
| Enable | ☐ ⚠️ | — |
| Skip points | ☑ | — |
| Internal ribs | ☐ | — |
| Width | 35 | mm |
| Max speed | 90 | mm/s |
| Brim width | 3 | mm |
| Infill gap | 150 | % |
| Rib wall | ☑ | — |
| Extra rib length | 0 | mm |
| Rib width | 8 | mm |
| Fillet wall | ☑ | — |

> ⚠️ **Prime tower ☑ → ☐:** Single-material print — prime tower is unnecessary and wastes TPU.

### Purge Options

| Setting | Value |
|---|---|
| Purge into objects' infill | ☐ |
| Purge into objects' support | ☑ |

### Special Mode

| Setting | Value |
|---|---|
| Slicing Mode | Regular |
| Print sequence | By layer |
| Spiral vase | ☐ |
| Timelapse | Traditional |
| Fuzzy Skin | None (allow...) |
| Fuzzy skin generator mode | Displacement |
| Fuzzy skin noise type | Classic |
| Fuzzy skin point distance | 0.3 mm |
| Fuzzy skin thickness | 0.2 mm |
| Apply fuzzy skin to first layer | ☐ |

### Advanced

| Setting | Value | Unit |
|---|---|---|
| Use beam interlocking | ☐ | — |
| Interlocking depth of a segmented region | 0 | mm |

### G-code Output

| Setting | Value |
|---|---|
| Reduce infill retraction | Auto |

### Post-processing Scripts

*(Empty — no scripts configured)*

---

## Filament Tab Settings (set separately in Bambu Studio)

> These are not in the Process settings above but are equally important for TPU.

| Setting | Recommended Value |
|---|---|
| Nozzle temperature | 230°C |
| Bed temperature | 35–40°C |
| Retraction distance | 0.8 mm |
| Retraction speed | 25 mm/s |
| Max volumetric speed | 8 mm³/s |
| Wipe on layer change | ☑ Enabled |
| Fan speed (general) | 30–50% |
| Fan speed (first layer) | 0% |
| Slow down if layer time < | 8 s |
| Min print speed | 10 mm/s |

---

## Summary of All Changes

| Tab | Setting | Default | TPU Value | Reason |
|---|---|---|---|---|
| Quality | Elephant foot compensation | 0 mm | 0.1 mm | TPU first layer spread |
| Quality | Bridge flow | 1.0 | 0.9 | Reduce TPU bridge sag |
| Quality | Avoid crossing wall | ☐ | ☑ | Reduce stringing between parts |
| Strength | Wall loops | 2 | 4 | Structural drone parts |
| Strength | Detect thin wall | ☐ | ☑ | 4.4 mm inserts need this |
| Strength | Bottom shell layers | 3 | 4 | Symmetric shell strength |
| Strength | Sparse infill density | 15% | 45% | Functional/mechanical parts |
| Strength | Sparse infill pattern | Grid | gyroid | Better flex-fatigue resistance |
| Speed | Initial layer infill | 105 mm/s | 30 mm/s | TPU first layer adhesion |
| Speed | Outer wall | 200 mm/s | 30 mm/s | **Critical — TPU speed limit** |
| Speed | Inner wall | 300 mm/s | 35 mm/s | **Critical — TPU speed limit** |
| Speed | Sparse infill | 270 mm/s | 40 mm/s | **Critical — TPU speed limit** |
| Speed | Internal solid infill | 250 mm/s | 35 mm/s | **Critical — TPU speed limit** |
| Speed | Top surface | 200 mm/s | 25 mm/s | TPU top surface quality |
| Speed | Bridge | 50 mm/s | 25 mm/s | TPU bridge control |
| Speed | Gap infill | 250 mm/s | 35 mm/s | TPU flow consistency |
| Speed | Support | 150 mm/s | 30 mm/s | TPU support quality |
| Speed | Support interface | 80 mm/s | 25 mm/s | TPU support interface |
| Speed | Normal printing accel | 6000 mm/s² | 1500 mm/s² | Reduce TPU bounce/ringing |
| Speed | Travel accel | 10000 mm/s² | 5000 mm/s² | Smoother travel with TPU |
| Speed | Initial layer travel accel | 6000 mm/s² | 2000 mm/s² | Gentle start |
| Speed | Initial layer accel | 500 mm/s² | 300 mm/s² | TPU first layer adhesion |
| Speed | Outer wall accel | 5000 mm/s² | 1000 mm/s² | Clean TPU perimeters |
| Speed | Top surface accel | 2000 mm/s² | 500 mm/s² | TPU top surface quality |
| Others | Skirt loops | 0 | 2 | Prime nozzle before parts |
| Others | Prime tower | ☑ | ☐ | Single material — not needed |
