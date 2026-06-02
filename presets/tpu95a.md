# TPU 95A — Baseline Preset
## Bambu A1 Mini · TPU 95A (Flexible)

> Conservative baseline for TPU 95A flexible filament. All speeds significantly reduced.
> Override with --settings for part-specific adjustments.

---

## Summary of All Changes

| Tab | Setting | Default | Value | Notes |
|---|---|---|---|---|
| Filament | Nozzle temperature | 220 | 230 | TPU requires higher nozzle temp |
| Filament | Bed temperature | 45 | 35 | Lower bed temp for TPU adhesion control |
| Speed | Initial layer speed | 20 | 15 | Slow first layer for TPU adhesion |
| Speed | Outer wall | 200 | 30 | Critical — TPU max safe wall speed |
| Speed | Inner wall | 300 | 40 | TPU inner wall limit |
| Speed | Sparse infill | 270 | 80 | TPU infill — still conservative |
| Filament | Fan speed (general) | 70 | 30 | TPU needs less cooling for layer bonding |
| Filament | Fan speed (first layer) | 0 | 0 | Never cool first layer |
| Strength | Wall loops | 2 | 3 | Baseline shell for flex parts |
| Strength | Sparse infill density | 15% | 15% | Standard density |
| Strength | Sparse infill pattern | Grid | gyroid | Better flex-fatigue resistance |
| Filament | Retraction distance | 1.0 | 0.8 | Shorter retraction for TPU to prevent jams |
| Filament | Retraction speed | 40 | 25 | Slow retraction for flexible filament |
| Filament | Max volumetric speed | 15 | 6 | TPU needs lower volumetric limit |
| Others | Brim type | no_brim | outer_only | Outer brim helps TPU adhesion |
| Others | Brim width | 5 | 6 | Slightly wider for TPU |
| Quality | Elephant foot compensation | 0 | 0.1 | TPU first layers spread slightly |
