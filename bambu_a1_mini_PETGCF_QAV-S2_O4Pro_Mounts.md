# Bambu A1 Mini — Advanced Mode Print Settings
## Profile: PETG-CF — QAV-S 2 Bardwell O4 Pro Camera Mounts (Left + Right)

> **Parts:** O4_Pro_Mount_Left, O4_Pro_Mount_Right
> **Material:** PETG-CF | **Plate:** Plate 1 — Mounts only
> **Geometry:** 6.02 mm wide × 30.00 mm deep × 36.53 mm tall, oriented flat on 6×30 mm face
> **Changes from Bambu A1 Mini defaults are marked ⚠️**
>
> ⚠️ **HARDWARE REQUIREMENT: Hardened steel nozzle required.** PETG-CF is abrasive and
> will permanently damage a brass nozzle within a single print. Do not print with brass.

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

> ⚠️ **Elephant foot compensation 0 → 0.1 mm:** PETG-CF first layers tend to squish outward slightly. The mount seating surfaces are dimensionally critical for camera fit — 0.1 mm compensation keeps them accurate.

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
| Bridge flow | 0.95 ⚠️ | — |
| Thick bridges | ☐ | — |
| Only one wall on top surfaces | Top surfaces | — |
| Only one wall on first layer | ☐ | — |
| Smooth speed discontinuity area | ☑ | — |
| Smooth coefficient | 80 | — |
| Avoid crossing wall | ☑ ⚠️ | — |
| Smoothing wall speed along Z (experimental) | ☐ | — |

> ⚠️ **Bridge flow 1.0 → 0.95:** Slight reduction prevents PETG-CF from sagging on bridged spans.
> ⚠️ **Avoid crossing wall ☐ → ☑:** Reduces stringing between the two mount parts during travel moves.

---

## Strength Tab

### Walls

| Setting | Value | Unit |
|---|---|---|
| Wall loops | 4 ⚠️ | — |
| Embedding the wall into the infill | ☐ | — |
| Detect thin wall | ☑ ⚠️ | — |

> ⚠️ **Wall loops 2 → 4:** These are primary structural parts on a drone. 4 walls provides the impact and vibration resistance the camera cage needs. The designer specifically recommends a stiff, tough material — back that up with wall count.
> ⚠️ **Detect thin wall ☐ → ☑:** The mounts taper in some areas; thin wall detection prevents the slicer from skipping geometry.

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

> ⚠️ **Bottom shell layers 3 → 4:** Matches top shell count; symmetrical shell thickness improves part strength and prevents warping during cooling.

### Sparse Infill

| Setting | Value | Unit |
|---|---|---|
| Sparse infill density | 45% ⚠️ | % |
| Fill multiline | 1 | — |
| Sparse infill pattern | gyroid ⚠️ | — |
| Length of sparse infill anchor | 400% | mm or % |
| Maximum length of sparse infill anchor | 20 | mm or % |

> ⚠️ **Infill density 15% → 45%:** Structural drone part subject to crash loads and vibration. 15% is decorative; 45% is mechanical.
> ⚠️ **Pattern Grid → Gyroid:** Gyroid distributes impact stress omnidirectionally and handles the repeated shock loads of drone crashes better than grid. Also prints well in PETG-CF without the direction-dependent weak spots of rectilinear patterns.

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
| Initial layer infill | 60 mm/s ⚠️ | mm/s |

> ⚠️ **Initial layer infill 105 → 60 mm/s:** PETG-CF benefits from a slower, more deliberate first layer to ensure proper bed adhesion on textured PEI. The default 105 mm/s is fine for PLA but risks poor adhesion with PETG-CF.

### Other Layers Speed

| Setting | Value | Unit |
|---|---|---|
| Outer wall | 80 mm/s ⚠️ | mm/s |
| Inner wall | 150 mm/s ⚠️ | mm/s |
| Small perimeters | 50% | mm/s or % |
| Small perimeter threshold | 0 | mm |
| Sparse infill | 180 mm/s ⚠️ | mm/s |
| Internal solid infill | 150 mm/s ⚠️ | mm/s |
| Vertical shell speed | 80% | mm/s or % |
| Top surface | 80 mm/s ⚠️ | mm/s |
| Slow down for overhangs | ☑ | — |
| Overhang speed @ 10% | 0 | mm/s |
| Overhang speed @ 25% | 50 | mm/s |
| Overhang speed @ 50% | 30 | mm/s |
| Overhang speed @ 75% | 10 | mm/s |
| Overhang speed @ 100% | 10 | mm/s |
| Slow down by height | ☐ | — |
| Bridge | 40 mm/s ⚠️ | mm/s |
| Gap infill | 150 mm/s ⚠️ | mm/s |
| Support | 150 | mm/s |
| Support interface | 80 | mm/s |

> ⚠️ **Speed reductions for PETG-CF:** PETG-CF needs more conservative speeds than PLA to maintain layer adhesion and avoid delamination. The carbon fibers reduce inter-layer bonding compared to plain PETG — slower outer walls compensate. These are still significantly faster than the TPU profile. The default 200–300 mm/s profile is tuned for PLA and will cause delamination and stringing with PETG-CF.

### Travel Speed

| Setting | Value | Unit |
|---|---|---|
| Travel | 100 | mm/s |

### Acceleration

| Setting | Value | Unit |
|---|---|---|
| Normal printing | 3000 mm/s² ⚠️ | mm/s² |
| Travel | 8000 mm/s² ⚠️ | mm/s² |
| Initial layer travel | 3000 mm/s² ⚠️ | mm/s² |
| Initial layer | 400 mm/s² ⚠️ | mm/s² |
| Outer wall | 3000 mm/s² ⚠️ | mm/s² |
| Inner wall | 0 | mm/s² |
| Top surface | 1500 mm/s² ⚠️ | mm/s² |
| Sparse infill | 100% | mm/s² or % |

> ⚠️ **Accelerations reduced from defaults:** High acceleration with PETG-CF causes ringing artifacts and can stress the CF-reinforced filament path. 3000 mm/s² outer wall is a good balance of speed and surface quality for these small structural parts.

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

> No supports needed. Parts are 36.53 mm tall and oriented flat on their 6×30 mm face. All overhangs are within the self-supporting range for PETG-CF at this layer height.

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

> ⚠️ **Skirt loops 0 → 2:** Add a skirt to purge the nozzle and confirm clean PETG-CF flow before hitting the parts. PETG-CF can string and blob at the start of a print if not primed.

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

> ⚠️ **Prime tower ☑ → ☐:** Single-material plate — prime tower is unnecessary.

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

> These live outside the Process settings panel but are equally critical for PETG-CF.

| Setting | Recommended Value |
|---|---|
| Nozzle temperature | 265°C |
| Bed temperature | 70°C (textured PEI) |
| Retraction distance | 0.8 mm |
| Retraction speed | 35 mm/s |
| Max volumetric speed | 15 mm³/s |
| Wipe on layer change | ☑ Enabled |
| Fan speed (general) | 70% |
| Fan speed (first layer) | 0% |
| Fan speed (second layer) | 30% (ramp up gradually) |
| Slow down if layer time < | 5 s |
| Min print speed | 20 mm/s |

> **Bed surface:** Use the textured PEI plate. PETG-CF bonds well to it without glue.
> Do NOT use smooth PEI — PETG-CF bonds too aggressively and can damage the sheet.

---

## Summary of All Changes from Bambu A1 Mini Defaults

| Tab | Setting | Default | PETG-CF Value | Reason |
|---|---|---|---|---|
| Quality | Elephant foot compensation | 0 mm | 0.1 mm | Dimensional accuracy on seating surfaces |
| Quality | Bridge flow | 1.0 | 0.95 | Prevent PETG-CF bridge sag |
| Quality | Avoid crossing wall | ☐ | ☑ | Reduce stringing between parts |
| Strength | Wall loops | 2 | 4 | Structural drone cage part |
| Strength | Detect thin wall | ☐ | ☑ | Handle tapering geometry |
| Strength | Bottom shell layers | 3 | 4 | Symmetric shell, prevent warping |
| Strength | Sparse infill density | 15% | 45% | Mechanical/structural part |
| Strength | Sparse infill pattern | Grid | gyroid | Omnidirectional impact resistance |
| Speed | Initial layer infill | 105 mm/s | 60 mm/s | PETG-CF bed adhesion |
| Speed | Outer wall | 200 mm/s | 80 mm/s | PETG-CF layer adhesion |
| Speed | Inner wall | 300 mm/s | 150 mm/s | PETG-CF layer adhesion |
| Speed | Sparse infill | 270 mm/s | 180 mm/s | PETG-CF flow consistency |
| Speed | Internal solid infill | 250 mm/s | 150 mm/s | PETG-CF layer bonding |
| Speed | Top surface | 200 mm/s | 80 mm/s | PETG-CF surface quality |
| Speed | Bridge | 50 mm/s | 40 mm/s | PETG-CF bridge control |
| Speed | Gap infill | 250 mm/s | 150 mm/s | PETG-CF flow consistency |
| Speed | Normal printing accel | 6000 mm/s² | 3000 mm/s² | Reduce ringing with CF filament |
| Speed | Travel accel | 10000 mm/s² | 8000 mm/s² | Smoother travel |
| Speed | Initial layer travel accel | 6000 mm/s² | 3000 mm/s² | Careful start |
| Speed | Initial layer accel | 500 mm/s² | 400 mm/s² | PETG-CF first layer adhesion |
| Speed | Outer wall accel | 5000 mm/s² | 3000 mm/s² | Clean CF perimeters |
| Speed | Top surface accel | 2000 mm/s² | 1500 mm/s² | Surface quality |
| Others | Skirt loops | 0 | 2 | Prime nozzle before parts |
| Others | Prime tower | ☑ | ☐ | Single material — not needed |
